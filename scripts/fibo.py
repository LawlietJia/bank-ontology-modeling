"""Offline reference index. Preserve original RDF; search results are not bank approval."""
import json, sqlite3
from pathlib import Path
from model import file_hash, read, write

def build_index(root):
    from rdflib import Graph, URIRef, Literal, RDF, RDFS, OWL, SKOS
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    db=root/'index.sqlite';db.unlink(missing_ok=True)
    conn=sqlite3.connect(db)
    conn.execute('create table terms (iri text, label text, definition text, type text, maturity text, deprecated integer, example integer, file text, ontology text, parents text, domain text, range text, primary key(iri,file))')
    conn.execute('create index term_iri on terms(iri)')
    ontologies={};imported=set();failures=[];files=[];aliases={};edges={};release_roots=set();lexical=[];licenses=[]
    for sub in ['source','dependencies']:
        for p in sorted((root/sub).rglob('*')):
            if not p.is_file():continue
            rel=p.relative_to(root).as_posix()
            files.append({'path':rel,'sha256':file_hash(p),'bytes':p.stat().st_size})
            if p.suffix not in {'.rdf','.ttl','.owl'} or any(x in {'etc','.github','test','tests'} for x in p.relative_to(root/sub).parts):continue
            g=Graph()
            try:g.parse(p,format='turtle' if p.suffix=='.ttl' else 'xml')
            except Exception as exc:failures.append({'file':rel,'error':str(exc)});continue
            os=list(g.subjects(RDF.type,OWL.Ontology));ontology=str(os[0]) if os else ''
            maturity='ExternalReference' if sub=='dependencies' else 'Unknown'
            for o in os:
                ontologies[str(o)]=rel
                for v in g.objects(o,OWL.versionIRI):ontologies[str(v)]=rel
                for pred,value in g.predicate_objects(o):
                    if str(pred).endswith('hasMaturityLevel'):maturity=str(value).split('/')[-1].split('#')[-1]
            imported.update(str(x) for x in g.objects(None,OWL.imports))
            for o in os:
                edges[str(o)]={str(x) for x in g.objects(o,OWL.imports)}
                if sub=='source' and maturity=='Release':release_roots.add(str(o))
            for _,_,value in g:
                if isinstance(value,Literal) and getattr(value,'ill_typed',False):lexical.append({'file':rel,'value':str(value),'datatype':str(value.datatype)})
            if sub=='dependencies':
                declarations=[str(v) for s,pred,v in g if str(pred) in {'http://purl.org/dc/terms/license','http://purl.org/dc/elements/1.1/rights'}]
                licenses.append({'file':rel,'declarations':declarations})
            example=int('EXMP' in p.parts or 'example' in p.stem.lower())
            types={OWL.Class:'Class',RDFS.Class:'Class',OWL.ObjectProperty:'ObjectProperty',OWL.DatatypeProperty:'DatatypeProperty',OWL.AnnotationProperty:'AnnotationProperty',OWL.NamedIndividual:'NamedIndividual'}
            subjects={s for s in g.subjects(RDFS.label,None) if isinstance(s,URIRef)}
            for t in types:subjects.update(s for s in g.subjects(RDF.type,t) if isinstance(s,URIRef))
            for s in subjects:
                if s in os:continue
                st=list(g.objects(s,RDF.type));typ=next((types[t] for t in st if t in types),'Resource')
                labels=list(g.objects(s,RDFS.label)); label=next((str(x) for x in labels if x.language in {'en',None}),str(s).split('/')[-1])
                defs=list(g.objects(s,SKOS.definition)); definition=' | '.join(str(x) for x in defs)
                deprecated=int(any(str(x).lower() in {'true','1'} for x in g.objects(s,OWL.deprecated)))
                conn.execute('insert or replace into terms values (?,?,?,?,?,?,?,?,?,?,?,?)',(str(s),label,definition,typ,maturity,deprecated,example,rel,ontology,
                  json.dumps([str(x) for x in g.objects(s,RDFS.subClassOf) if isinstance(x,URIRef)]),
                  json.dumps([str(x) for x in g.objects(s,RDFS.domain)]),json.dumps([str(x) for x in g.objects(s,RDFS.range)])))
    resolutions=root/'import-resolutions.json'
    if resolutions.exists():
        for iri,entry in read(resolutions).items():
            if entry.get('file') in {x['path'] for x in files} and entry.get('evidence'):aliases[iri]=entry['file']
            else:failures.append({'file':'import-resolutions.json','error':'无效导入映射 '+iri})
    conn.commit()
    count=conn.execute('select count(*) from terms').fetchone()[0]
    maturity_counts=dict(conn.execute('select maturity,count(*) from terms group by maturity').fetchall());conn.close()
    missing=sorted(imported-set(ontologies)-set(aliases))
    reached=set();todo=list(release_roots)
    while todo:
        uri=todo.pop()
        if uri in reached:continue
        reached.add(uri);todo.extend(edges.get(uri,set())-reached)
    release_missing=sorted(reached-set(ontologies)-set(aliases))
    report={'term_rows':count,'ontology_identifiers':len(ontologies),'imports':len(imported),'unresolved_imports':missing,'release_unresolved_imports':release_missing,'parse_failures':failures,'maturity_counts':maturity_counts,'resolutions':aliases,'lexical_warnings':lexical,'complete':not missing and not failures}
    write(root/'coverage.json',report)
    write(root/'dependency-licenses.json',licenses)
    files.append({'path':'index.sqlite','sha256':file_hash(db),'bytes':db.stat().st_size})
    for name in ['coverage.json','upstream.json','dependency-sources.json','dependency-licenses.json','import-resolutions.json','DEPENDENCIES.md']:
        p=root/name
        if p.exists():files.append({'path':name,'sha256':file_hash(p),'bytes':p.stat().st_size})
    write(root/'manifest.json',{'format':'1.0','files':files,'coverage':report,'upstream':read(root/'upstream.json') if (root/'upstream.json').exists() else {}})
    return report

def search(root,query,limit=20,include_unstable=False):
    db=Path(root)/'index.sqlite'
    if not db.exists():raise ValueError('FIBO索引不存在，请先执行fibo-build')
    c=sqlite3.connect('file:'+str(db.resolve())+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
    terms=query.split();where=[];args=[]
    for term in terms:
        where.append('(lower(label) like ? or lower(iri) like ? or lower(definition) like ?)');args += ['%'+term.lower()+'%']*3
    if not include_unstable:where.append("maturity in ('Release','ExternalReference') and deprecated=0 and example=0 and type in ('Class','ObjectProperty','DatatypeProperty','AnnotationProperty')")
    result=[dict(r) for r in c.execute('select * from terms where '+(' and '.join(where) or '1')+' order by case when lower(label)=? then 0 else 1 end,label limit ?',args+[query.lower(),max(1,min(limit,200))])]
    c.close();return result

def describe(root,iri):
    from rdflib import Graph, URIRef, BNode
    root=Path(root);c=sqlite3.connect('file:'+str((root/'index.sqlite').resolve())+'?mode=ro',uri=True)
    files=[r[0] for r in c.execute('select file from terms where iri=?',(iri,))];c.close()
    if not files:raise ValueError('参考包不存在该IRI')
    data=[]
    for f in files:
        g=Graph().parse(root/f,format='turtle' if f.endswith('.ttl') else 'xml');todo=[URIRef(iri)];seen=set();triples=[]
        while todo:
            s=todo.pop()
            if s in seen:continue
            seen.add(s)
            for t in g.triples((s,None,None)):
                triples.append([x.n3() for x in t])
                if isinstance(t[2],BNode):todo.append(t[2])
        data.append({'file':f,'triples':triples})
    return {'iri':iri,'assertions':data,'note':'原始公理需结合导入和银行业务语义解释；检索不等于采用或批准。'}

def verify(root):
    root=Path(root);m=read(root/'manifest.json');bad=[]
    for entry in m['files']:
        p=root/entry['path']
        if not p.is_file() or file_hash(p)!=entry['sha256']:bad.append(entry['path'])
    known={e['path'] for e in m['files']}
    extra=[p.relative_to(root).as_posix() for sub in ['source','dependencies'] for p in (root/sub).rglob('*') if p.is_file() and p.relative_to(root).as_posix() not in known]
    return {'ok':not bad and not extra and m['coverage']['complete'],'integrity_ok':not bad and not extra,'changed_or_missing':bad,'unmanifested':extra,'dependency_complete':m['coverage']['complete'],'release_dependency_complete':not m['coverage'].get('release_unresolved_imports',m['coverage']['unresolved_imports']) and not m['coverage']['parse_failures']}
