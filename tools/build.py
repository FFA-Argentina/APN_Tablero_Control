import json, collections
R=json.load(open('raw.json')); A=json.load(open('agg.json')); P=json.load(open('deuda_pdf.json'))
acc=A['acc']; cob=A['cob']; deu=A['deu']
CYC=['nov 23–oct 24','nov 24–oct 25','nov 25–oct 26']
def nf(v,d=0):
    s=f"{abs(v):,.{d}f}".replace(',','X').replace('.',',').replace('X','.')
    return ('−' if v<0 and round(abs(v),d)!=0 else '')+s
def vr(new,base):
    if base is None or base<=0 or base<0.1*new: return None
    return (new/base-1)*100
def pc(v,d=1):
    if v is None: return 's/base'
    return ('+' if v>0.05 else '')+nf(v,d)+'%' if abs(v)>=0.05 else '0,0%'
def pp(x,d=1): return nf(x*100,d)+'%'
M=1e6
T={}
# ---------------- Tabla I
cp=cob['sets']['pt']['tot']; ca=cob['sets']['all_ex']['tot']
rows=[('Tickets de acceso (miles)',[x/1e3 for x in acc['t']],0),
('Días de visita (miles)',[x/1e3 for x in acc['d']],0),
('Ingresos netos de accesos ($ M oct-26)',[x/M for x in acc['neto_cer']],0),
('Comisiones a tercerizadoras ($ M oct-26)',[x/M for x in acc['com_cer']],0),
('Cobranza a prestadores turísticos ($ M oct-26)',[x/M for x in cp['cer']],0),
('Cobranza, todos los pagos ($ M oct-26)',[x/M for x in ca['cer']],0),
('Ingresos netos de accesos (US$ M)',[x/M for x in acc['neto_usd']],1),
('Cobranza a prestadores turísticos (US$ M)',[x/M for x in cp['usd']],1)]
T['t1']=[{'n':n,'v':[nf(x,d) for x in v],'raw':v,'ia':pc(vr(v[2],v[1])),'tri':pc(vr(v[2],v[0]))} for n,v,d in rows]
# ---------------- Accesos detail
seg=acc['seg']; SEGN={'RP':'Residentes','NR':'No residentes','NP':'Vehículos y adicionales'}
t2=[]
for k in ('RP','NR','NP'):
    s=seg[k]; t=s['t']; n=[x/M for x in s['neto_cer']]; c=[x/M for x in s['com_cer']]
    t2.append({'n':SEGN[k],'t':nf(t[2]),'tia':pc(vr(t[2],t[1])),'neto':nf(n[2]),'nia':pc(vr(n[2],n[1])),'npt':nf(n[2]*M/t[2]),'npt_prev':n[1]*M/t[1],'npt_raw':n[2]*M/t[2],'cp':pp(c[2]/(c[2]+n[2])),'ide':s['ide_cer'][2]/M,'neto_raw':n,'t_raw':t})
tt=acc['t']; tn=[x/M for x in acc['neto_cer']]; tc=[x/M for x in acc['com_cer']]
t2.append({'n':'Total','t':nf(tt[2]),'tia':pc(vr(tt[2],tt[1])),'neto':nf(tn[2]),'nia':pc(vr(tn[2],tn[1])),'npt':nf(tn[2]*M/tt[2]),'npt_prev':tn[1]*M/tt[1],'npt_raw':tn[2]*M/tt[2],'cp':pp(tc[2]/(tc[2]+tn[2])),'tot':True})
T['t2']=t2
DEPN={'Administración Central':'Casa Central (pasaportes)','PN Los Glaciares':'Glaciares'}
def dn(k): return DEPN.get(k,k.replace('PN ',''))
t3=[]
for k,v in acc['dep'].items():
    t=v['t']
    if t[2]==0: continue
    n=[x/M for x in v['neto_cer']]; c=[x/M for x in v['com_cer']]
    nr=acc['dep_seg'][k]['NR']['t'][2]
    t3.append({'n':dn(k),'t':nf(t[2]),'tia':pc(vr(t[2],t[1])),'neto':nf(n[2],1),'nia':pc(vr(n[2],n[1])),'ntri':pc(vr(n[2],n[0])),'nrp':pp(nr/t[2]),'npt':nf(n[2]*M/t[2]),'cp':pp(c[2]/(c[2]+n[2])) if c[2]>0.01 else '—','neto_raw':n,'t_raw':t,'com_raw':c,'usd':[x/M for x in v['neto_usd']]})
t3.sort(key=lambda r:-r['neto_raw'][2]); T['t3']=t3
# ---------------- Cobranzas
U={'ddjj':'Concesionarios y permisionarios (DDJJ)','pt':'**Prestadores turísticos**','all_ex':'Todos los pagos'}
T['t4']=[]
for k in ('ddjj','pt','all_ex'):
    s=cob['sets'][k]['tot']; v=[x/M for x in s['cer']]
    T['t4'].append({'n':U[k],'v':[nf(x) for x in v],'raw':v,'ia':pc(vr(v[2],v[1])),'tri':pc(vr(v[2],v[0])),'usd':nf(s['usd'][2]/M,1),'usd_raw':[x/M for x in s['usd']]})
COBN={'Otras dependencias':'Otras dependencias'}
def cdeps(k):
    rs=[]; tot=sum(r['cer'][2] for r in cob['sets'][k]['dep'])
    for r in cob['sets'][k]['dep']:
        v=[x/M for x in r['cer']]
        rs.append({'n':r['label'],'v':[nf(x,1) for x in v],'raw':v,'ia':pc(vr(v[2],v[1])),'tri':pc(vr(v[2],v[0])),'part':pp(r['cer'][2]/tot),'usd':[x/M for x in r['usd']]})
    other=[r for r in rs if r['n'].startswith('Otras')]; rest=[r for r in rs if not r['n'].startswith('Otras')]
    rest.sort(key=lambda r:-r['raw'][2]); return rest+other
T['t5']=cdeps('pt'); T['anexB']=cdeps('all_ex')
RSN={'Iguazu Argentina S.A.':'Iguazú Argentina S.A.','Hielo Y Aventura Sa':'Hielo y Aventura S.A.','La Gran Aventura Náutica Srl':'La Gran Aventura Náutica S.R.L.','Solo Patagonia S.A.':'Solo Patagonia S.A.','London Supply Sacifi':'London Supply S.A.C.I.F.I.','Tranex Turismo S.A.':'Tranex Turismo S.A.','Turisur Srl':'Turisur S.R.L.','Marpatag Srl':'Marpatag S.R.L.','Estancia Cristina Sa':'Estancia Cristina S.A.','Espacio Sa':'Espacio S.A.','Otros prestadores':'Otros prestadores'}
tot=sum(r['cer'][2] for r in cob['sets']['pt']['rs'])
t6=[]
for r in cob['sets']['pt']['rs']:
    v=[x/M for x in r['cer']]
    t6.append({'n':RSN.get(r['label'],r['label']),'v2':nf(v[2],1),'raw':v,'ia':pc(vr(v[2],v[1])),'tri':pc(vr(v[2],v[0])),'part':pp(r['cer'][2]/tot),'usd':[x/M for x in r['usd']]})
T['t6']=t6
# Anexo A: universes with/without electronic
T['anexA']=[]
for k,n in [('ddjj','Concesionarios y permisionarios'),('pt','Prestadores turísticos'),('all_ex','Todos los pagos, sin medios electrónicos'),('all_in','Todos los pagos, con medios electrónicos')]:
    s=cob['sets'][k]['tot']; v=[x/M for x in s['cer']]; c=[x/M for x in s['corr']]; u=[x/M for x in s['usd']]
    T['anexA'].append({'n':n,'v':[nf(x) for x in v],'tri':pc(vr(v[2],v[0])),'corr':[nf(x) for x in c],'usd':[nf(x,1) for x in u],'n_tx':s['n']})
# ---------------- Deuda
dt=deu['tot']
EX={'cap':1023137107.30,'int':483851343.37,'bruta':1506988450.67,'saf':189042166.0,'neta':1317946284.67}
EX['saf']=EX['bruta']-1317946284.67  # neta from report rounding
T['deu']={'cap':EX['cap'],'int':EX['int'],'bruta':EX['bruta'],'saf':dt['saf'],'neta':EX['bruta']-dt['saf'],'usd':1550,'comp':11035,'deud':3904,'deps':33}
# deudores per dep
ddash=deu['dep']
t7=[]; acum=0
for r in P['dep']:
    acum+=r['tot']; d=ddash[r['n']]
    t7.append({'n':r['n'],'cap':r['cap'],'int':r['int'],'tot':r['tot'],'p':r['tot']/EX['bruta'],'pa':acum/EX['bruta'],'deud':d['deud'],'comp':d['comp'],'saf':d['saf'],'gj':d['gj']})
T['t7']=t7
act={r['n']:r for r in P['act_dep']}
T['act_dep']=P['act_dep']
T['top']=P['top']
# deudores multi-dep
D=R['deu']['deudores']; per=collections.defaultdict(set)
for f in R['deu']['facts']: per[f[0]].add(f[1])
T['multi']=sum(1 for v in per.values() if len(v)>1); T['deud_sum']=sum(len(v) for v in per.values())
# top10 with deps/act from dashboard
T['top_dash']=deu['top'][:12]
T['tramos']=deu['tramos']; T['top10p']=deu['top10']/dt['bruta']; T['top100p']=deu['top100']/dt['bruta']
T['gj']=deu['gj']; T['act']=deu['act']
# origin capital
Y=R['deu']['years']; inc=collections.Counter()
for f in R['deu']['facts']:
    prev=0
    for j,v in enumerate(f[4]): inc[Y[f[3]+j]]+=v-prev; prev=v
grp=[('≤2020',Y[:7]),('2021',['2021']),('2022',['2022']),('2023',['2023']),('2024',['2024']),('2025',['2025']),('2026 (a oct)',['oct-26'])]
T['origen']=[{'y':g,'cap':sum(inc[y] for y in ys)} for g,ys in grp]
# ---------------- Cruzados
ACCK={'Lanín':'PN Lanín','El Palmar':'PN El Palmar','Lago Puelo':'PN Lago Puelo','Los Alerces':'PN Los Alerces','Nahuel Huapi':'PN Nahuel Huapi','Tierra del Fuego':'PN Tierra del Fuego','Glaciares':'PN Los Glaciares','Iguazú':'PN Iguazú','Talampaya':'PN Talampaya'}
cobpt={r['label']:r for r in cob['sets']['pt']['dep']}
t9=[]
for n,ak in ACCK.items():
    dep=next(r for r in t7 if r['n']==n); a_=act.get(n,{'tot':0})
    neto=acc['dep'][ak]['neto_cer'][2]/M
    cb=cobpt[n]['cer'][2]/M
    t9.append({'n':n,'neto':neto if neto>0.05 else None,'cob':cb,'deuda':dep['tot']/M,'ints':dep['int']/dep['tot'],'act':a_['tot']/dep['tot'],'ratio':dep['tot']/M/cb,'act_ratio':a_['tot']/M/cb})
t9.sort(key=lambda r:-r['ratio']); T['t9']=t9
T['ratio_tot']=EX['bruta']/M/(cp['cer'][2]/M); T['ratio_act']=389407564.36/M/(cp['cer'][2]/M)
T['ratio_corr_cobpdf']=EX['bruta']/cob['sets']['all_ex']['tot']['corr'][2]
json.dump(T,open('tables.json','w'),ensure_ascii=False,indent=1)
# print key items
for r in T['t1']: print(r['n'],r['v'],r['ia'],r['tri'])
for r in T['t2']: print(r['n'],r['t'],r['tia'],r['neto'],r['nia'],r['npt'],r['cp'], nf((r['npt_raw']/r['npt_prev']-1)*100,1))
for r in T['t3']: print(r['n'],r['t'],r['tia'],r['neto'],r['nia'],r['ntri'],r['nrp'],r['npt'],r['cp'])
for r in T['t4']: print(r)
for r in T['t5']: print(r['n'],r['v'],r['ia'],r['tri'],r['part'])
for r in T['t6']: print(r['n'],r['v2'],r['ia'],r['tri'],r['part'])
print('multi',T['multi'],T['deud_sum'])
print('origen',[(o['y'],round(o['cap']/1e6,1)) for o in T['origen']])
for r in T['t9']: print(r['n'],r['neto'],round(r['cob'],1),round(r['deuda'],1),pp(r['ints']),pp(r['act']),pp(r['ratio']/100*100/100*100/100) , round(r['ratio']*100,1), round(r['act_ratio']*100,1))
print('ratio',T['ratio_tot'],T['ratio_act'],T['ratio_corr_cobpdf'])
print(T['deu'])
for r in T['anexA']: print(r)
for r in T['anexB']: print(r['n'],r['v'],r['tri'])
