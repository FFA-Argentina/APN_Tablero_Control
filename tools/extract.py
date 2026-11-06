import re, json, sys
def grab(path, pat):
    s=open(path,encoding='utf-8').read()
    m=re.search(pat,s)
    if not m: return None
    obj,_=json.JSONDecoder().raw_decode(s[m.end():])
    return obj
src='/home/claude/work/src/'
acc=grab(src+'accesos.html', r'window\.__DATA__\s*=\s*')
cob=grab(src+'cobranzas.html', r'const DATA\s*=\s*')
pay=grab(src+'cobranzas.html', r'const PAYERS\s*=\s*')
deu=grab(src+'deuda.html', r'const DATA\s*=\s*')
json.dump({'acc':acc,'cob':cob,'pay':pay,'deu':deu},open('/home/claude/work/raw.json','w'),ensure_ascii=False)
for k,v in [('acc',acc),('cob',cob),('deu',deu)]:
    print(k, type(v).__name__, list(v.keys()) if isinstance(v,dict) else len(v))
print('pay', type(pay).__name__, len(pay) if pay else None, pay[:2] if pay else None)
