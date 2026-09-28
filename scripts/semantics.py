"""Validate business semantic specifications, not actual policy outcomes or SHACL."""
import math
import re
from datetime import date
from urllib.parse import urlsplit

LEVELS={'class','individual','property','statement'}
UNIT_TYPES={'requirement','recommendation','instruction','permission','statement','definition','example','note','other'}
NATURES={'normative','fact','proposed','example','modeling_decision','unknown'}
CONSTRAINT_TYPES={'unique','cardinality','value_range','enumeration','date_order','disjoint','reference','custom'}


def specification_error(kind,s):
    if not isinstance(kind,str) or kind not in CONSTRAINT_TYPES:return '未知约束类别'
    if not isinstance(s,dict) or not s:return '约束规格须为非空JSON对象'
    number=lambda v:isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
    if kind in {'value_range','cardinality'}:
        if not any(k in s for k in ('min','max')):return '须给出min或max'
        for key in ('min','max'):
            if key in s and not number(s[key]):return '边界须为有限数值'
            if kind=='cardinality' and key in s and (not isinstance(s[key],int) or s[key]<0):return '基数须为非负整数'
        if 'min' in s and 'max' in s and s['min']>s['max']:return '最小值不得大于最大值'
        for k in ('min_inclusive','max_inclusive'):
            if k in s and not isinstance(s[k],bool):return '边界包含标记须为布尔值'
        if 'min' in s and 'max' in s and s['min']==s['max'] and (s.get('min_inclusive',True) is False or s.get('max_inclusive',True) is False):return '范围为空'
    elif kind=='enumeration':
        values=s.get('values')
        if not isinstance(values,list) or not values:return 'values须为非空列表'
        if any(v is None or not isinstance(v,(str,int,float,bool)) or isinstance(v,float) and not math.isfinite(v) for v in values):return '枚举须由有效标量组成'
    elif kind=='date_order':
        if s.get('operator') not in ('lt','le'):return '日期顺序operator须为lt或le'
    elif kind=='unique':
        if not s.get('scope'):return '唯一性须指定适用范围scope'
    elif kind=='reference':
        if s.get('policy') not in ('must_exist','allow_external','requires_resolution'):return '引用须指定policy'
    elif kind=='custom':
        if not s.get('expression') or not s.get('language'):return '自定义约束须有expression和language'
    return None


def check_semantics(m,records,issue,ref_lists):
    baseline=m.get('project',{}).get('status')=='baseline'
    required_severity='error' if baseline else 'warning'
    iri_index={}
    def detail(r):return r.get('details',{}) if isinstance(r.get('details',{}),dict) else {}
    def absent(value):return value is None or value=='' or value==[] or value=={}
    for rid,r in records.items():
        d=detail(r)
        for key in ref_lists:
            if key in d and (not isinstance(d[key],list) or any(not isinstance(x,str) or not x.strip() for x in d[key])):
                issue('reference_shape',rid,key+'须为非空ID组成的列表（可为空列表）')
        if m.get('schema_version')=='1.0' and r.get('kind') in {'information_unit','constraint'}:
            issue('schema',rid,'新增记录类型须使用schema_version 1.1')
        level=d.get('model_level')
        if level is not None and (not isinstance(level,str) or level not in LEVELS):issue('model_level',rid,'未知建模层次')
        if 'labels' in d and (not isinstance(d['labels'],dict) or not d['labels'] or any(not isinstance(v,str) or not v.strip() for v in d['labels'].values())):
            issue('metadata',rid,'labels须为语言代码到非空标签的JSON对象')
        if 'synonyms' in d and (not isinstance(d['synonyms'],list) or any(not isinstance(v,str) for v in d['synonyms'])):
            issue('metadata',rid,'synonyms须为字符串列表')
        iri=d.get('iri')
        if iri:
            try:valid=isinstance(iri,str) and bool(urlsplit(iri).scheme) and not re.search(r'[\s<>"{}|\\^`]',iri)
            except ValueError:valid=False
            if not valid:issue('invalid_iri',rid,'IRI须是无空白的绝对标识符')
            elif iri in iri_index:issue('duplicate_iri',rid,'IRI与'+iri_index[iri]+'重复；同义项应通过标签或有依据的映射表达')
            else:iri_index[iri]=rid
        if m.get('schema_version')=='1.1' and r.get('kind') in {'concept','object','role','attribute','relation'} and r.get('status')!='deprecated':
            for key in ('model_level','term_name','labels'):
                if absent(d.get(key)):issue('detail_missing',rid,'缺少语义元数据 '+key,required_severity)
        if level=='class' and d.get('instance_of_ids'):issue('model_level',rid,'本契约不把同一记录同时作为类与实例；请分开记录')
        if level=='individual' and not d.get('instance_of_ids'):issue('detail_missing',rid,'实例缺少所属类',required_severity)
        if d.get('property_type') is not None:
            expected={'attribute':'data','relation':'object'}.get(r.get('kind'))
            if d['property_type'] not in ('data','object') or expected and d['property_type']!=expected:
                issue('property_type',rid,'attribute用data，relation用object')
        if level=='property' and r.get('status')!='deprecated':
            for key in ('property_type','domain_ids'):
                if absent(d.get(key)):issue('detail_missing',rid,'属性缺少 '+key,required_severity)
            if d.get('property_type')=='object' and not d.get('range_ids'):issue('detail_missing',rid,'对象属性缺少值域类',required_severity)
            if d.get('property_type')=='data' and d.get('range_ids'):issue('property_type',rid,'数据属性使用datatype而非值域类')
        for key in ref_lists:
            values=d.get(key,[])
            if not isinstance(values,list):continue
            for target in values:
                if not isinstance(target,str) or target not in records:continue
                target_level=detail(records[target]).get('model_level')
                if key in {'source_unit_ids','related_unit_ids','exception_unit_ids'} and records[target].get('kind')!='information_unit':
                    issue('reference_kind',rid,key+'只能引用信息单元：'+target)
                if key in {'parent_ids','equivalent_ids','disjoint_ids','instance_of_ids','domain_ids','range_ids'}:
                    if target_level not in (None,'class'):issue('reference_kind',rid,key+'只能引用类：'+target)
                    if target==rid and key in {'parent_ids','disjoint_ids','instance_of_ids'}:issue('self_reference',rid,key+'不能引用自身')
        for key in ('effective_from','effective_to'):
            if d.get(key):
                try:date.fromisoformat(d[key])
                except (ValueError,TypeError):issue('date_format',rid,key+'须为有效ISO日期')
        if d.get('effective_from') and d.get('effective_to'):
            try:
                if date.fromisoformat(d['effective_from'])>date.fromisoformat(d['effective_to']):issue('date_order',rid,'生效日期晚于失效日期')
            except (ValueError,TypeError):pass
        if r.get('kind')=='information_unit':
            if not isinstance(d.get('unit_type'),str) or d['unit_type'] not in UNIT_TYPES:issue('unit_type',rid,'未知信息单元类型')
            if not isinstance(d.get('statement_nature'),str) or d['statement_nature'] not in NATURES:issue('statement_nature',rid,'未知陈述性质')
            if not isinstance(d.get('representation'),list) or not d['representation'] or any(not isinstance(v,str) or not v for v in d['representation']):issue('representation',rid,'表述形式须为非空字符串列表')
        if r.get('kind')=='constraint':
            error=specification_error(d.get('constraint_type'),d.get('specification'))
            if error:issue('constraint_spec',rid,error)
            targets=d.get('target_ids',[])
            if d.get('constraint_type') in ('date_order','disjoint') and (not isinstance(targets,list) or len(targets)!=2 or len(set(x for x in targets if isinstance(x,str)))!=2):
                issue('constraint_spec',rid,'日期顺序或互斥须给出两个不同的有序目标ID')
    # Iterative ancestry traversal avoids recursion overflow for large reference trees.
    for rid,r in records.items():
        parents=detail(r).get('parent_ids',[])
        todo=list(parents) if isinstance(parents,list) else [];seen=set()
        while todo:
            p=todo.pop()
            if not isinstance(p,str):continue
            if p==rid:issue('inheritance_cycle',rid,'存在循环继承');break
            if p in seen or p not in records:continue
            seen.add(p);more=detail(records[p]).get('parent_ids',[])
            if isinstance(more,list):todo.extend(more)
        disjoint=detail(r).get('disjoint_ids',[])
        if isinstance(disjoint,list) and seen & {v for v in disjoint if isinstance(v,str)}:
            issue('disjoint_ancestor',rid,'类声明与其父类或祖先互斥')
