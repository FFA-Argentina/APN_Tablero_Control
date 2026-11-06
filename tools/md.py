import json
T=json.load(open('tables.json'))
def nf(v,d=0):
    s=f"{abs(v):,.{d}f}".replace(',','X').replace('.',',').replace('X','.')
    return ('−' if v<0 and round(abs(v),d)!=0 else '')+s
pp=lambda x,d=1: nf(x*100,d)+'%'
C=['nov 23–oct 24','nov 24–oct 25','nov 25–oct 26']
out={}
# Tabla I
L=['| Indicador | '+' | '.join(C)+' | Var. i.a. | Var. trienal |','| --- | --: | --: | --: | --: | --: |']
for r in T['t1']: L.append(f"| {r['n']} | "+' | '.join(r['v'])+f" | {r['ia']} | {r['tri']} |")
out['t1']='\n'.join(L)
# Tabla II
L=['| Categoría | Tickets | Var. i.a. | Neto ($ M oct-26) | Var. i.a. | Neto por ticket ($ oct-26) | Comisión / percibido |','| --- | --: | --: | --: | --: | --: | --: |']
for r in T['t2']:
    b='**' if r.get('tot') else ''
    L.append('| '+' | '.join(f"{b}{x}{b}" for x in [r['n'],r['t'],r['tia'],r['neto'],r['nia'],r['npt'],r['cp']])+' |')
out['t2']='\n'.join(L)
# Tabla III
L=['| Dependencia | Tickets | Var. i.a. | Neto ($ M oct-26) | Var. i.a. | Var. trienal | No residentes (% tickets) | Neto por ticket ($) | Comisión / percibido |','| --- | --: | --: | --: | --: | --: | --: | --: | --: |']
for r in T['t3']:
    cp=r['cp']
    if r['com_raw'][2]/(r['com_raw'][2]+r['neto_raw'][2])<0.0005: cp='—'
    L.append('| '+' | '.join([r['n'],r['t'],r['tia'],r['neto'],r['nia'],r['ntri'],r['nrp'],r['npt'],cp])+' |')
out['t3']='\n'.join(L)
# Tabla IV
L=['| Universo ($ M oct-26) | '+' | '.join(C)+' | Var. i.a. | Var. trienal | US$ M (nov 25–oct 26) |','| --- | --: | --: | --: | --: | --: | --: |']
for r in T['t4']: L.append(f"| {r['n']} | "+' | '.join(r['v'])+f" | {r['ia']} | {r['tri']} | {r['usd']} |")
out['t4']='\n'.join(L)
def depT(rows,head):
    L=[f'| {head} | '+' | '.join(C)+' | Var. i.a. | Var. trienal | Participación |','| --- | --: | --: | --: | --: | --: | --: |']
    for r in rows: L.append(f"| {r['n']} | "+' | '.join(r['v'])+f" | {r['ia']} | {r['tri']} | {r['part']} |")
    tot=[sum(r['raw'][i] for r in rows) for i in range(3)]
    def vr(a,b): return ('+' if a/b>1 else '')+nf((a/b-1)*100,1)+'%'
    L.append('| **Total** | '+' | '.join(f"**{nf(x,1)}**" for x in tot)+f" | **{vr(tot[2],tot[1])}** | **{vr(tot[2],tot[0])}** | **100,0%** |")
    return '\n'.join(L)
out['t5']=depT(T['t5'],'Dependencia ($ M oct-26)')
L=['| Razón social | nov 25–oct 26 ($ M oct-26) | Var. i.a. | Var. trienal | Participación |','| --- | --: | --: | --: | --: |']
for r in T['t6']: L.append(f"| {r['n']} | {r['v2']} | {r['ia']} | {r['tri']} | {r['part']} |")
out['t6']='\n'.join(L)
# debt composition
d=T['deu']; B=d['bruta']
rows=[('Capital',d['cap']),('Intereses devengados',d['int']),('**Deuda bruta**',B),('Pagos a cuenta conciliados',-d['saf']),('**Deuda neta**',d['neta'])]
L=['| Concepto | $ M (31/10/2026) | US$ miles (a $ 1.550) | % de la deuda bruta |','| --- | --: | --: | --: |']
for n,v in rows:
    b='**' if n.startswith('**') else ''
    L.append(f"| {n} | {b}{nf(v/1e6,1)}{b} | {b}{nf(v/1550/1e3,0)}{b} | {b}{pp(v/B)}{b} |")
out['dcomp']='\n'.join(L)
# Tabla VII
L=['| Dependencia | Capital | Interés | Deuda total | % | % acum. | Deudores |','| --- | --: | --: | --: | --: | --: | --: |']
for r in T['t7']: L.append(f"| {r['n']} | {nf(r['cap'],2)} | {nf(r['int'],2)} | {nf(r['tot'],2)} | {pp(r['p'],2)} | {pp(r['pa'],2)} | {nf(r['deud'])} |")
L.append(f"| **TOTAL** | **{nf(d['cap'],2)}** | **{nf(d['int'],2)}** | **{nf(B,2)}** | **100,00%** |  | **3.904** |")
out['t7']='\n'.join(L)
# tramos
lab=['Menos de $ 0,1 M','$ 0,1 M a $ 1 M','$ 1 M a $ 10 M','$ 10 M a $ 100 M','$ 100 M o más']
L=['| Tramo de deuda por deudor | Deudores | Deuda ($ M) | % de la deuda |','| --- | --: | --: | --: |']
bt=sum(t['tot'] for t in T['tramos'])
for l,t in zip(lab,T['tramos']): L.append(f"| {l} | {nf(t['n'])} | {nf(t['tot']/1e6,1)} | {pp(t['tot']/bt)} |")
out['tram']='\n'.join(L)
# Tabla VIII
depof={r['name'].upper():r['deps'] for r in T['top_dash']}
names={'LATORRE CARLOS MARTIN':'Tierra del Fuego','ST PRODUCCIONES S.A.':'Nahuel Huapi','PANCORA S.A.':'Nahuel Huapi','LAGO HERMOSO S.A.':'Lanín','ESTABLECIMIENTO «LA LONJA»':'Nahuel Huapi','NUEVA COMPAÑÍA DE SABORES':'Iguazú','ESTANCIA MELIQUINA S.A.':'Lanín','EL MANSO S.R.L.':'Nahuel Huapi','GRUPO BFP S.R.L.':'Nahuel Huapi','VANIER NICOLAS OLIVER JAC':'Lanín'}
L=['| Razón social | Dependencia | Capital | Interés | % int. | Deuda total | % | % acum. | # |','| --- | --- | --: | --: | --: | --: | --: | --: | --: |']
for r in T['top']:
    if r['n'] in names:
        L.append(f"| {r['n']} | {names[r['n']]} | {nf(r['cap'],2)} | {nf(r['int'],2)} | {r['pint']}% | {nf(r['tot'],2)} | {r['p']}% | {r['pa']} | {r['k']} |")
    else:
        L.append(f"| **{r['n']}** |  | **{nf(r['cap'],2)}** | **{nf(r['int'],2)}** | **{r['pint']}%** | **{nf(r['tot'],2)}** | **{r['p']}%** |  | **{r['k']}** |")
out['t8']='\n'.join(L)
# Tabla IX
L=['| Dependencia | Neto de accesos ($ M oct-26) | Cobranza a prestadores ($ M oct-26) | Deuda exigible ($ M) | Intereses / deuda | Deuda de habilitados / deuda |','| --- | --: | --: | --: | --: | --: |']
for r in T['t9']: L.append(f"| {r['n']} | {'—' if r['neto'] is None else nf(r['neto'],1)} | {nf(r['cob'],1)} | {nf(r['deuda'],1)} | {pp(r['ints'])} | {pp(r['act'])} |")
out['t9']='\n'.join(L)
# Anexo A
L=['| Universo ($ M oct-26) | '+' | '.join(C)+' | Var. trienal | US$ M (nov 25–oct 26) | $ M corrientes (nov 25–oct 26) |','| --- | --: | --: | --: | --: | --: | --: |']
for r in T['anexA']: L.append(f"| {r['n']} | "+' | '.join(r['v'])+f" | {r['tri']} | {r['usd'][2]} | {r['corr'][2]} |")
out['anA']='\n'.join(L)
L=['| Dependencia ($ M oct-26) | '+' | '.join(C)+' | Var. trienal |','| --- | --: | --: | --: | --: |']
for r in T['anexB']: L.append(f"| {r['n']} | "+' | '.join(r['v'])+f" | {r['tri']} |")
out['anB']='\n'.join(L)
json.dump(out,open('md.json','w'),ensure_ascii=False,indent=0)
for k,v in out.items(): print('=====',k); print(v)
