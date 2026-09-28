"""Command interface; all business decisions remain explicit model records."""
import argparse, json, sys
from pathlib import Path
from model import read, write, validate

def main():
    p=argparse.ArgumentParser(description='银行业务本体本地工具：解析、验证、交付、修订和FIBO检索。不会自动生成或批准业务语义。')
    sub=p.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('ingest');a.add_argument('input');a.add_argument('--out',required=True);a.add_argument('--dialect');a.add_argument('--ocr',action='store_true');a.add_argument('--language',default='chi_sim+eng')
    a=sub.add_parser('validate');a.add_argument('model');a.add_argument('--out')
    a=sub.add_parser('export');a.add_argument('model');a.add_argument('--out',required=True)
    a=sub.add_parser('review-workbook');a.add_argument('workbook');a.add_argument('--current',required=True);a.add_argument('--out',required=True)
    a=sub.add_parser('word-opinions');a.add_argument('input');a.add_argument('--out',required=True)
    a=sub.add_parser('merge');a.add_argument('current');a.add_argument('proposal');a.add_argument('--decisions',required=True);a.add_argument('--version',required=True);a.add_argument('--out',required=True)
    default=str(Path(__file__).resolve().parents[1]/'references/fibo')
    for command in ['fibo-search','fibo-describe','fibo-build','fibo-verify']:
        a=sub.add_parser(command);a.add_argument('--root',default=default)
        if command=='fibo-search':a.add_argument('query');a.add_argument('--limit',type=int,default=20);a.add_argument('--include-unstable',action='store_true')
        if command=='fibo-describe':a.add_argument('iri')
    a=p.parse_args();out=None;status=0
    if a.cmd=='ingest':
        from ingest import ingest
        out=ingest(a.input,a.dialect,a.ocr,a.language)
    elif a.cmd=='validate':
        out={'issues':validate(read(a.model),Path(a.model).resolve().parent)};status=int(any(x['severity']=='error' for x in out['issues']))
    elif a.cmd=='export':
        from deliver import export
        out=export(read(a.model),a.out,Path(a.model).resolve().parent)
        print(json.dumps(out,ensure_ascii=False,indent=2));return 0
    elif a.cmd=='review-workbook':
        from deliver import read_workbook
        from revisions import propose
        base,edited=read_workbook(a.workbook);out=propose(base,edited,read(a.current))
    elif a.cmd=='word-opinions':
        from ingest import word_opinions
        out=word_opinions(a.input)
    elif a.cmd=='merge':
        from revisions import merge
        out=merge(read(a.current),read(a.proposal),read(a.decisions),a.version)
    else:
        import fibo
        if a.cmd=='fibo-search':out=fibo.search(a.root,a.query,a.limit,a.include_unstable)
        elif a.cmd=='fibo-describe':out=fibo.describe(a.root,a.iri)
        elif a.cmd=='fibo-build':out=fibo.build_index(a.root)
        else:out=fibo.verify(a.root);status=int(not out['ok'])
    if getattr(a,'out',None):
        if Path(a.out).exists():raise ValueError('不覆盖已有结果，请使用新输出路径')
        write(a.out,out);print(json.dumps({'output':a.out,'exit_status':status},ensure_ascii=False))
    else:print(json.dumps(out,ensure_ascii=False,indent=2))
    return status

if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,ImportError) as exc:
        print(str(exc),file=sys.stderr);sys.exit(2)
