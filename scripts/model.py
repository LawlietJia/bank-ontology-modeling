"""Portable model contract and deterministic checks; never decides business truth."""
import hashlib
import json
from pathlib import Path

KINDS = {'concept':'概念','object':'业务对象','role':'业务角色','attribute':'属性','relation':'关系','event':'事件','state':'状态','rule':'业务规则','metric':'指标','decision':'决策','action':'业务动作','mapping':'来源映射'}
LEGACY_KINDS = dict(KINDS)
KINDS.update(information_unit='信息单元', constraint='业务约束')
STATES = {'candidate':'待确认','reviewed':'已评审','approved':'已确认','deprecated':'已废弃'}
DETAILS = {
 'domain':'业务领域','identity':'身份判定','classification':'分类依据','scope':'适用范围','nature':'陈述性质',
 'subject':'主体ID','object':'客体ID','owner_id':'所属对象ID','target':'目标ID','cardinality':'业务基数',
 'datatype':'值类型','unit':'计量单位','currency':'币种口径','time_basis':'时间口径','allowed_values':'允许值',
 'condition':'适用条件','expression':'规则或计算表达','exceptions':'例外情形','positive_case':'正例','negative_case':'反例',
 'unknown_handling':'缺失信息处理','inputs':'所需输入','outputs':'产出','actor':'参与角色','authorization':'权限与审批',
 'preconditions':'前置条件','effects':'业务效果','failure':'失败处理','success':'成功判定','idempotency':'重复执行处理',
 'state_from':'原状态ID','state_to':'目标状态ID','trigger':'触发条件','source_table':'来源表','source_field':'来源字段',
 'transformation':'映射逻辑','coverage':'覆盖范围','external_iri':'参考IRI','reference_version':'参考版本','alignment':'对齐方式',
 'rationale':'建模理由','owner':'业务责任','decision_id':'所支持决策ID'}
REF_FIELDS = {'subject','object','owner_id','target','state_from','state_to','decision_id'}
REF_LIST_FIELDS = {'source_unit_ids','parent_ids','equivalent_ids','disjoint_ids','instance_of_ids',
                   'domain_ids','range_ids','target_ids','about_ids','related_unit_ids','exception_unit_ids'}
DETAILS.update({
 'iri':'语义IRI','term_name':'规范名称','labels':'可读标签JSON','synonyms':'同义词列表JSON','model_level':'建模层次',
 'parent_ids':'父类ID列表JSON','equivalent_ids':'等价类ID列表JSON','disjoint_ids':'互斥类ID列表JSON',
 'instance_of_ids':'所属类ID列表JSON','property_type':'属性类型','domain_ids':'定义域ID列表JSON','range_ids':'值域类ID列表JSON',
 'source_unit_ids':'依据信息单元ID列表JSON','content':'原文内容','unit_type':'信息单元类型','statement_nature':'陈述性质',
 'representation':'表述形式列表JSON','about_ids':'涉及对象ID列表JSON','related_unit_ids':'引用信息单元ID列表JSON',
 'exception_unit_ids':'例外信息单元ID列表JSON','constraint_type':'约束类别','target_ids':'约束目标ID列表JSON',
 'specification':'约束规格JSON','effective_from':'生效日期','effective_to':'失效日期','verification_owner':'验证责任',
 'conformance_basis':'标准条款依据','interpretation':'解释与适用边界'})
REQUIRED = {'object':['identity'], 'relation':['subject','object','cardinality'], 'attribute':['owner_id','datatype'],
 'rule':['condition','expression','exceptions','unknown_handling','positive_case','negative_case'],
 'metric':['expression','scope','unit','time_basis'], 'event':['subject','trigger','time_basis'],
 'action':['actor','authorization','preconditions','effects','failure','success','idempotency'],
 'decision':['inputs','outputs','actor'], 'mapping':['target','transformation','coverage']}
REQUIRED.update(information_unit=['content','unit_type','statement_nature','representation'],
                constraint=['constraint_type','target_ids','specification','condition','exceptions',
                            'unknown_handling','positive_case','negative_case'])

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def write(path, data):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def file_hash(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()

def references(record):
    result={x for x in record.get('links',[]) if isinstance(x,str)}
    for key in REF_FIELDS | REF_LIST_FIELDS:
        value=record.get('details',{}).get(key)
        if value: result.update(x for x in (value if isinstance(value,list) else [value]) if isinstance(x,str))
    return result

def has_test_evidence(test):
    def has_text(value):
        if isinstance(value,str):return bool(value.strip())
        if isinstance(value,dict):return any(has_text(v) for v in value.values())
        if isinstance(value,list):return any(has_text(v) for v in value)
        return False
    return has_text(test.get('evidence'))

def validate(m, base_dir=None):
    out=[]
    def issue(code,loc,message,severity='error'): out.append(dict(code=code,location=loc,message=message,severity=severity))
    if not isinstance(m,dict): return [dict(code='schema',location='model',message='模型必须是对象',severity='error')]
    if m.get('schema_version') not in {'1.0','1.1'}: issue('schema','schema_version','支持 schema_version 1.0 或 1.1')
    project=m.get('project',{}); baseline=project.get('status')=='baseline'
    if project.get('status') not in {'draft','baseline'}: issue('schema','project.status','项目状态应为 draft 或 baseline')
    for key in ['id','title','version','purpose','domains','application','owner']:
        if not project.get(key): issue('project_missing','project.'+key,'缺少项目字段 '+key)
    groups={}
    for collection in ['records','sources','questions','tests','decisions']:
        values=m.get(collection)
        if not isinstance(values,list): issue('schema',collection,'必须为列表'); groups[collection]={}; continue
        idx={}
        for i,item in enumerate(values):
            if not isinstance(item,dict) or not isinstance(item.get('id'),str) or not item['id'].strip():
                issue('missing_id',f'{collection}[{i}]','缺少稳定字符串ID'); continue
            if item['id'] in idx: issue('duplicate_id',collection+'.'+item['id'],'ID重复')
            idx.setdefault(item['id'],item)
        groups[collection]=idx
    records=groups['records']; sources=groups['sources']; source_blocks={}
    if baseline and not records: issue('empty_baseline','records','空模型不可成为实施基线')
    for sid,s in sources.items():
        if base_dir and s.get('blocks_path'):
            path=Path(s['blocks_path']); path=path if path.is_absolute() else Path(base_dir)/path
            try:
                parsed=read(path); source_blocks[sid]={b['anchor'] for b in parsed['blocks']}
                if s.get('sha256') and s['sha256']!=parsed['source']['sha256']: issue('source_version',sid,'解析件与登记的文件哈希不同')
            except (OSError,KeyError,ValueError) as exc: issue('source_unavailable',sid,str(exc))
    for rid,r in records.items():
        if r.get('kind') not in KINDS: issue('kind',rid,'未知记录类型')
        if r.get('status') not in STATES: issue('status',rid,'未知评审状态')
        for key in ['name','definition']:
            if not r.get(key): issue('record_missing',rid,'缺少 '+key)
        if not isinstance(r.get('details',{}),dict): issue('schema',rid,'details必须为对象'); continue
        if not isinstance(r.get('links',[]),list) or not isinstance(r.get('evidence',[]),list): issue('schema',rid,'links和evidence必须为列表'); continue
        for target in references(r):
            if target not in records: issue('missing_reference',rid,'引用不存在：'+str(target))
        evidence=r.get('evidence',[])
        approved_decision=any(d.get('status')=='approved' and rid in d.get('affects',[]) and d.get('approved_by') and d.get('approved_at') for d in groups['decisions'].values())
        for e in evidence:
            if not isinstance(e,dict): issue('schema',rid,'证据必须是对象'); continue
            sid=e.get('source_id')
            if sid not in sources: issue('missing_source',rid,'证据来源不存在：'+str(sid))
            if not e.get('anchor'): issue('missing_anchor',rid,'证据缺少定位')
            if sid in source_blocks and e.get('anchor') not in source_blocks[sid]: issue('invalid_anchor',rid,'解析件没有此定位：'+str(e.get('anchor')))
            if 'field' in e:
                field=e['field']
                valid_field=isinstance(field,str) and (
                    (field in {'name','definition'} and field in r) or
                    (field.startswith('details.') and field[8:] in r['details']))
                if not valid_field: issue('invalid_evidence_field',rid,'证据field须指向本记录的name、definition或已存在的details字段：'+str(field))
        if r.get('status')!='deprecated':
            if not evidence and not approved_decision: issue('no_evidence',rid,'缺少来源或明确批准的建模决定','error' if baseline else 'warning')
            for key in REQUIRED.get(r.get('kind'),[]):
                if not r['details'].get(key): issue('detail_missing',rid,'缺少 '+DETAILS.get(key,key),'error' if baseline else 'warning')
            if baseline and r.get('status')!='approved': issue('unapproved',rid,'实施基线含未确认记录')
            if baseline and not approved_decision: issue('approval_missing',rid,'实施基线缺少带批准人、时间和影响ID的批准记录')
    for qid,q in groups['questions'].items():
        for rid in q.get('affects',[]):
            if rid not in records: issue('missing_reference',qid,'问题引用不存在：'+rid)
        if baseline and q.get('blocking') and q.get('status')!='resolved': issue('open_blocker',qid,'关键问题未关闭')
        if q.get('status')=='resolved' and not q.get('resolution'): issue('resolution_missing',qid,'已关闭问题须有处理决定')
    for tid,t in groups['tests'].items():
        refs=t.get('record_ids',[])
        if not isinstance(refs,list) or any(not isinstance(rid,str) or not rid.strip() for rid in refs):
            issue('test_references',tid,'验收record_ids须为模型记录ID列表')
        else:
            if not refs: issue('test_unlinked',tid,'未关联模型记录，请补充验收所用记录或在验证记录中说明适用范围','warning')
            for rid in refs:
                if rid not in records: issue('missing_reference',tid,'验收引用不存在：'+rid)
        if not t.get('question') or not t.get('expected'): issue('test_incomplete',tid,'验收须包含问题和预期')
        if t.get('result') not in ('not_run','pass','fail'): issue('test_result',tid,'验收结果须为not_run、pass或fail')
        if baseline and (t.get('result')!='pass' or not has_test_evidence(t)):
            issue('test_not_passed',tid,'验收未通过或缺少验证记录')
        elif t.get('result')=='pass' and not has_test_evidence(t):
            issue('test_evidence_missing',tid,'声明通过但缺少验证记录，须补充实际走查依据','warning')
    if not groups['tests']: issue('missing_tests','tests','缺少能力问题与验收案例；草案也应登记预期，未执行可记not_run','error' if baseline else 'warning')
    from semantics import check_semantics
    check_semantics(m,records,issue,REF_LIST_FIELDS)
    return out
