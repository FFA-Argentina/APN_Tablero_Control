import re,json
t=open('/home/claude/work/informe-deudas-31oct26.txt',encoding='utf-8').read()
num=r'(\d{1,3}(?:\.\d{3})*,\d{2}|—)'
def pn(s): return 0.0 if s=='—' else float(s.replace('.','').replace(',','.'))
def block(start,end):
    i=t.index(start); j=t.index(end,i); return t[i:j]
res={}
# Tabla II (two pages)
b=block('TABLA II — 1 DE 2','TABLA III')
rows=[]
for m in re.finditer(r'^\s{2}([A-ZÁÉÍÓÚa-záéíóúñü][^\d\n]+?)\s{2,}'+num+r'\s+'+num+r'\s+'+num+r'\s+([\d,]+)%',b,re.M):
    n=m.group(1).strip()
    if n in('TOTAL',): continue
    rows.append({'n':n,'cap':pn(m.group(2)),'int':pn(m.group(3)),'tot':pn(m.group(4))})
res['dep']=rows
b=block('TABLA III','TABLA IV')
res['act_dep']=[{'n':m.group(1).strip(),'cap':pn(m.group(2)),'int':pn(m.group(3)),'tot':pn(m.group(4))} for m in re.finditer(r'^\s{2}([A-ZÁÉÍÓÚa-záéíóúñü][^\d\n]+?)\s{2,}'+num+r'\s+'+num+r'\s+'+num+r'\s+([\d,]+)%',b,re.M) if not m.group(1).strip().startswith('TOTAL')]
b=block('TABLA I\n','TABLA I — LECTURA')
res['top']=[{'n':m.group(1).strip(),'cap':pn(m.group(2)),'int':pn(m.group(3)),'pint':m.group(4),'tot':pn(m.group(5)),'p':m.group(6),'pa':m.group(7),'k':m.group(8)} for m in re.finditer(r'^\s{2}(\S[^\n]*?)\s{2,}'+num+r'\s+'+num+r'\s+([\d.,]+)%\s+'+num+r'\s+([\d,]+)%\s+([\d,]*%?)\s+([\d.]+)\s*$',b,re.M)]
json.dump(res,open('/home/claude/work/deuda_pdf.json','w'),ensure_ascii=False,indent=0)
print(len(res['dep']),sum(r['tot'] for r in res['dep']),len(res['act_dep']),sum(r['tot'] for r in res['act_dep']))
for r in res['top']: print(r)
