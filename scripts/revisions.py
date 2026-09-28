"""Three-way proposals; no mutation until every change has an explicit decision."""
import copy
from model import digest, references, validate

COLLECTIONS=('records','questions','tests','sources')
MISSING={'__missing__':True}

def _get(m,path):
    if path[0] in COLLECTIONS:
        value=next((x for x in m.get(path[0],[]) if x['id']==path[1]),MISSING)
        keys=path[2:]
    else: value=m; keys=path
    for k in keys:
        if not isinstance(value,dict) or k not in value: return MISSING
        value=value[k]
    return value

def _diff(a,b,path):
    if a==b: return []
    if a!=MISSING and b!=MISSING and isinstance(a,dict) and isinstance(b,dict):
        return [p for k in sorted(a.keys()|b.keys()) for p in _diff(a.get(k,MISSING),b.get(k,MISSING),path+[k])]
    return [path]

def impacts(m,ids):
    affected=set(ids)
    while True:
        more={r['id'] for r in m['records'] if references(r)&affected}
        if more<=affected: break
        affected |= more
    return sorted(affected)

def propose(base,edited,current):
    if len({x['project']['id'] for x in (base,edited,current)})!=1: raise ValueError('项目ID不一致')
    for m in (base,edited,current):
        errors=[x for x in validate(m) if x['severity']=='error' and x['code'] not in {'missing_reference','unapproved','approval_missing','test_not_passed','open_blocker','detail_missing','no_evidence'}]
        if errors: raise ValueError('输入不合法：'+str(errors))
    paths=[]
    for col in COLLECTIONS:
        a={x['id']:x for x in base.get(col,[])}; b={x['id']:x for x in edited.get(col,[])}
        for rid in sorted(a.keys()|b.keys()): paths+=_diff(a.get(rid,MISSING),b.get(rid,MISSING),[col,rid])
    for key in ['title','purpose','domains','application','owner']:
        paths+=_diff(base['project'].get(key,MISSING),edited['project'].get(key,MISSING),['project',key])
    changes=[]
    for path in paths:
        a=_get(base,path); b=_get(edited,path); c=_get(current,path)
        if b==c: continue
        seeds=[]
        if path[0]=='records':seeds=[path[1]]
        elif path[0]=='sources':seeds=[r['id'] for r in current['records'] if any(e.get('source_id')==path[1] for e in r.get('evidence',[]))]
        elif path[0]=='questions':seeds=list(set(_get(current,[path[0],path[1]]).get('affects',[]))|set(_get(edited,[path[0],path[1]]).get('affects',[])))
        elif path[0]=='project' and path[1] in {'purpose','domains','application'}:seeds=[r['id'] for r in current['records']]
        changes.append({'id':'CH-'+digest([path,a,b])[:16],'path':path,'base':a,'edited':b,'current':c,
            'conflict':c!=a,'impact':impacts(current,seeds)})
    return {'project_id':current['project']['id'],'base_version':base['project']['version'],'current_version':current['project']['version'],
        'current_hash':digest(current),'changes':changes,'word_opinions':[]}

def _set(m,path,value):
    if path[0] in COLLECTIONS:
        col=m[path[0]]; idx=next((i for i,x in enumerate(col) if x['id']==path[1]),None)
        if len(path)==2:
            if value==MISSING:
                if idx is not None: col.pop(idx)
            elif idx is None: col.append(copy.deepcopy(value))
            else: col[idx]=copy.deepcopy(value)
            return
        if idx is None: raise ValueError('当前记录已删除，无法应用字段修改：'+str(path))
        target=col[idx]; keys=path[2:]
    else: target=m; keys=path
    for key in keys[:-1]: target=target.setdefault(key,{})
    if value==MISSING: target.pop(keys[-1],None)
    else: target[keys[-1]]=copy.deepcopy(value)

def merge(current,proposal,decisions,new_version):
    if digest(current)!=proposal['current_hash']: raise ValueError('提案已过期，重新执行三方比较')
    if not new_version or new_version==current['project']['version']: raise ValueError('新版本不能为空或与当前相同')
    if set(decisions)!={x['id'] for x in proposal['changes']}: raise ValueError('每项变更须有且仅有一个明确决定')
    if any(x not in {'current','edited'} for x in decisions.values()): raise ValueError('决定只能为current或edited')
    result=copy.deepcopy(current); touched=set(); changed_tests=set()
    for c in proposal['changes']:
        path=c['path']
        if not path or (path[0] not in COLLECTIONS and (len(path)!=2 or path[0]!='project' or path[1] not in {'title','purpose','domains','application','owner'})): raise ValueError('不支持的变更路径')
        if decisions[c['id']]=='edited':
            _set(result,path,c['edited']); touched.update(c['impact'])
            if path[0]=='records': touched.add(path[1])
            if path[0]=='tests' and (len(path)==2 or path[2] not in {'result','evidence'}):changed_tests.add(path[1])
    if any(r['kind'] in {'information_unit','constraint'} for r in result['records']):result['schema_version']='1.1'
    # Added/changed dependencies are part of the resulting model too.
    touched.update(impacts(result,touched))
    for r in result['records']:
        if r['id'] in touched and r['status']!='deprecated': r['status']='candidate'
    for t in result['tests']:
        if t['id'] in changed_tests or touched & set(t.get('record_ids',[])): t['result']='not_run'; t.pop('evidence',None)
    for d in result.get('decisions',[]):
        invalidated=touched & set(d.get('affects',[]))
        if invalidated:
            d.setdefault('invalidated_affects',[]).extend(sorted(invalidated))
            d['affects']=[r for r in d['affects'] if r not in invalidated]
            if not d['affects']:d['status']='superseded'
    result['project']['version']=new_version; result['project']['status']='draft'
    result.setdefault('revision_history',[]).append({'from_version':current['project']['version'],'to_version':new_version,'proposal_hash':digest(proposal),'choices':decisions})
    errors=[x for x in validate(result) if x['severity']=='error']
    if errors: raise ValueError('合并后模型不合法：'+str(errors))
    return result
