import json, collections
R=json.load(open('raw.json'))
a=R['acc']; c=R['cob']; d=R['deu']; P=R['pay']
CYC=[(0,12),(12,24),(24,36)]
def var(x,b):
    if b is None or b==0 or b<0.1*x and False: return None
    return x/b-1
def vv(new,base):
    # s/base if base < 10% of next
    if base<=0 or base<0.1*new: return 's/base'
    return new/base-1
out={}
# ---------- ACCESOS
M={m:i for i,m in enumerate(a['metrics'])}
def asum(metric,deps=None,segs=('RP','NR','NP')):
    r=[]
    for s0,s1 in CYC:
        t=0
        for dep,dd in a['data'].items():
            if deps and dep not in deps: continue
            for sg in segs: t+=sum(dd[sg][M[metric]][s0:s1])
        r.append(t)
    return r
acc={}
for m in a['metrics']: acc[m]=asum(m)
acc['seg']={sg:{m:asum(m,segs=(sg,)) for m in a['metrics']} for sg in ('RP','NR','NP')}
acc['dep']={dep:{m:asum(m,deps=[dep]) for m in a['metrics']} for dep in a['deps']}
acc['dep_seg']={dep:{sg:{m:asum(m,deps=[dep],segs=(sg,)) for m in ('t','neto_cer','com_cer','ide_cer')} for sg in ('RP','NR','NP')} for dep in a['deps']}
# monthly totals for charts
acc['monthly']={m:[sum(sum(dd[sg][M[m]][i] for sg in dd) for dd in a['data'].values()) for i in range(36)] for m in ('t','neto_cer','com_cer','neto_usd')}
acc['meses']=a['meses']
out['acc']=acc
# ---------- COBRANZAS
cy=c['cycles']
def csum(arr): return [sum(arr[s:e+1]) for s,e in cy]
cob={'months':c['months'],'sets':{}}
for k,st in c['sets'].items():
    tot={f:[0]*len(c['months']) for f in ('cer','usd','corr','n')}
    for r in st['dep']:
        for f in tot: tot[f]=[x+y for x,y in zip(tot[f],r[f])]
    tot2={f:[0]*len(c['months']) for f in ('cer','usd','corr','n')}
    for r in st['rs']:
        for f in tot2: tot2[f]=[x+y for x,y in zip(tot2[f],r[f])]
    cob['sets'][k]={'tot':{f:csum(tot[f]) for f in tot},'tot_rs_check':csum(tot2['cer']),
        'monthly_cer':tot['cer'],
        'dep':[{'name':r['name'],'label':r['label'],'cer':csum(r['cer']),'usd':csum(r['usd']),'corr':csum(r['corr'])} for r in st['dep']],
        'rs':[{'name':r['name'],'label':r['label'],'cer':csum(r['cer']),'usd':csum(r['usd']),'corr':csum(r['corr'])} for r in st['rs']]}
out['cob']=cob
# ---------- DEUDA
Y=d['years']; L=len(Y)-1
deps=d['deps']; D=d['deudores']
dd={'deps':deps,'usd':d['usd'],'meta':d['meta'],'years':Y}
cap=sum(f[4][-1] for f in d['facts']); inte=sum(f[5][-1] for f in d['facts'])
safc=sum(f[6] for f in d['facts']); safi=sum(f[7] for f in d['facts'])
dd['tot']={'cap':cap,'int':inte,'bruta':cap+inte,'safCap':safc,'safInt':safi,'saf':safc+safi,'neta':cap+inte-safc-safi,'comp':sum(f[8] for f in d['facts'])}
bydep=collections.defaultdict(lambda:{'cap':0,'int':0,'saf':0,'act':0,'act_cap':0,'act_int':0,'gj':0,'deud':set(),'comp':0})
bydeud=collections.defaultdict(lambda:{'cap':0,'int':0,'deps':set(),'gj':0,'saf':0})
byyear=collections.defaultdict(lambda:{'cap':0,'int':0,'comp':0})
gj={'tot':0,'cap':0,'int':0,'comp':0,'deud':set()}
for f in d['facts']:
    di,pi,g,sy,ca,ia,sc,si,n=f
    C=ca[-1]; I=ia[-1]; act=D[di][1]
    b=bydep[deps[pi]]; b['cap']+=C; b['int']+=I; b['saf']+=sc+si; b['deud'].add(di); b['comp']+=n
    if act: b['act']+=C+I; b['act_cap']+=C; b['act_int']+=I
    if g: b['gj']+=C+I; gj['tot']+=C+I; gj['cap']+=C; gj['int']+=I; gj['comp']+=n; gj['deud'].add(di)
    u=bydeud[di]; u['cap']+=C; u['int']+=I; u['deps'].add(deps[pi]); u['saf']+=sc+si
    y=byyear[Y[sy]]; y['cap']+=C; y['int']+=I; y['comp']+=n
dd['dep']={k:{'cap':v['cap'],'int':v['int'],'tot':v['cap']+v['int'],'saf':v['saf'],'act':v['act'],'act_cap':v['act_cap'],'act_int':v['act_int'],'gj':v['gj'],'deud':len(v['deud']),'comp':v['comp']} for k,v in bydep.items()}
dd['gj']={'tot':gj['tot'],'cap':gj['cap'],'int':gj['int'],'comp':gj['comp'],'deud':len(gj['deud'])}
dd['year']=dict(byyear)
rows=[]
for di,u in bydeud.items():
    rows.append({'name':D[di][0],'act':D[di][1],'cap':u['cap'],'int':u['int'],'tot':u['cap']+u['int'],'deps':sorted(u['deps'])})
rows.sort(key=lambda r:-r['tot'])
dd['top']=rows[:25]
dd['n_deud']=len(rows)
act=[r for r in rows if r['act']]
dd['act']={'n':len(act),'tot':sum(r['tot'] for r in act),'cap':sum(r['cap'] for r in act),'int':sum(r['int'] for r in act)}
# tramos
tr=[(0,1e5),(1e5,1e6),(1e6,1e7),(1e7,1e8),(1e8,1e18)]
dd['tramos']=[{'lo':lo,'hi':hi,'n':sum(1 for r in rows if lo<=r['tot']<hi),'tot':sum(r['tot'] for r in rows if lo<=r['tot']<hi)} for lo,hi in tr]
dd['top10']=sum(r['tot'] for r in rows[:10]); dd['top100']=sum(r['tot'] for r in rows[:100])
# yearly stock evolution (stock by year snapshot)
dd['stock_by_snapshot']=[{'y':Y[i],'cap':sum(f[4][i-f[3]] for f in d['facts'] if i>=f[3]),'int':sum(f[5][i-f[3]] for f in d['facts'] if i>=f[3])} for i in range(len(Y))]
out['deu']=dd
json.dump(out,open('agg.json','w'),ensure_ascii=False,default=list)
# ---- prints
print('ACC dep neto_cer'); 
for k,v in acc['dep'].items(): print(' ',k,[round(x/1e6,1) for x in v['neto_cer']],v['t'])
print('NR neto',[round(x/1e6) for x in acc['seg']['NR']['neto_cer']],'NP',[round(x/1e6) for x in acc['seg']['NP']['neto_cer']])
for k,s in cob['sets'].items():
    print('COB',k,[round(x/1e9,2) for x in s['tot']['cer']],'usd',[round(x/1e6,1) for x in s['tot']['usd']],'corr',[round(x/1e9,2) for x in s['tot']['corr']],'n',s['tot']['n'], 'rscheck',[round(x/1e9,2) for x in s['tot_rs_check']])
print('pt dep'); [print('  ',r['label'],[round(x/1e9,3) for x in r['cer']]) for r in cob['sets']['pt']['dep']]
print('pt rs'); [print('  ',r['label'],[round(x/1e9,3) for x in r['cer']]) for r in cob['sets']['pt']['rs']]
print('all_ex dep'); [print('  ',r['label'],[round(x/1e9,3) for x in r['cer']]) for r in cob['sets']['all_ex']['dep']]
print('DEU',dd['tot'], dd['n_deud'], dd['act'], dd['gj'])
for k,v in sorted(dd['dep'].items(),key=lambda x:-x[1]['tot'])[:12]: print('  ',k,round(v['tot']),round(v['act']),v['deud'],round(v['saf']))
for r in rows[:12]: print('  ',r['name'],r['act'],round(r['tot'],2),r['deps'])
print('tramos',dd['tramos'],dd['top10']/dd['tot']['bruta'],dd['top100']/dd['tot']['bruta'])
print('year',{k:(round(v['cap']/1e6,1),round(v['int']/1e6,1),v['comp']) for k,v in dd['year'].items()})
