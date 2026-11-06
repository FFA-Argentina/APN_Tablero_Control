"""Arma el tablero HTML «Tablero de control APN» a partir de raw.json / tables.json / deuda_pdf.json."""
import json, base64, collections
R = json.load(open('/home/claude/work/raw.json')); T = json.load(open('/home/claude/work/tables.json')); P = json.load(open('/home/claude/work/deuda_pdf.json'))
a = R['acc']; cb = R['cob']; dd = R['deu']
PDF = 'Tablero_de_control_APN_nov23-oct26.pdf'
DOC = 'https://claude.ai/code/artifact/e226b64b-3192-4e48-b264-88dfc2199861'

# ---------------- D
def dn(k):
    return {'Administración Central': 'Casa Central (pasaportes)', 'PN Los Glaciares': 'Glaciares'}.get(k, k.replace('PN ', ''))
MI = {m: i for i, m in enumerate(a['metrics'])}
MAP = {'t': 't', 'd': 'd', 'n': 'neto_cer', 'c': 'com_cer', 'i': 'ide_cer', 'nu': 'neto_usd', 'cu': 'com_usd', 'iu': 'ide_usd'}
acc = {'deps': [dn(k) for k in a['deps']], 'data': {}}
for k in a['deps']:
    acc['data'][dn(k)] = {sg: {kk: [round(x) for x in a['data'][k][sg][MI[m]]] for kk, m in MAP.items()} for sg in ('RP', 'NR', 'NP')}
LAB = {'ddjj': 'Concesionarios y permisionarios', 'pt': 'Prestadores turísticos', 'all_ex': 'Todos los pagos'}
cob = {}
for k in ('ddjj', 'pt', 'all_ex'):
    cob[k] = {'label': LAB[k], 'deps': {r['label']: {'cer': r['cer'][3:], 'usd': r['usd'][3:]} for r in cb['sets'][k]['dep']}}
RSN = {'Iguazu Argentina S.A.': 'Iguazú Argentina S.A.', 'Hielo Y Aventura Sa': 'Hielo y Aventura S.A.', 'La Gran Aventura Náutica Srl': 'La Gran Aventura Náutica S.R.L.', 'London Supply Sacifi': 'London Supply S.A.C.I.F.I.', 'Turisur Srl': 'Turisur S.R.L.', 'Marpatag Srl': 'Marpatag S.R.L.', 'Estancia Cristina Sa': 'Estancia Cristina S.A.', 'Espacio Sa': 'Espacio S.A.'}
rs = [{'n': RSN.get(r['label'], r['label']), 'cer': r['cer'][3:], 'usd': r['usd'][3:]} for r in cb['sets']['pt']['rs']]
# deuda
act = {r['n']: r for r in P['act_dep']}
deps = []
for r in T['t7']:
    deps.append({'n': r['n'], 'cap': round(r['cap']), 'int': round(r['int']), 'pac': round(r['saf']), 'gj': round(r['gj']), 'act': round(act[r['n']]['tot']) if r['n'] in act else 0, 'deud': r['deud'], 'comp': r['comp']})
Y = dd['years']; inc = collections.Counter()
for f in dd['facts']:
    prev = 0
    for j, v in enumerate(f[4]):
        inc[Y[f[3] + j]] += v - prev; prev = v
top = []
for r in T['top_dash'][:10]:
    top.append({'n': r['name'], 'dep': r['deps'][0], 'm': round(r['tot']), 'act': r['act']})
lab = ['Menos de $0,1 M', '$0,1 M a $1 M', '$1 M a $10 M', '$10 M a $100 M', '$100 M o más']
deuda = {'cap': 1023137107, 'int': 483851343, 'bruto': 1506988451, 'pac': T['deu']['saf'], 'neto': round(T['deu']['neta']), 'comprob': 11035, 'deudores': 3904, 'usd': 1550,
         'years': [y if y != 'oct-26' else '2026 (a oct)' for y in Y], 'origen': [round(inc[y]) for y in Y], 'dep': deps, 'top10': top,
         'tramos': [{'t': l, 'n': t['n'], 'm': round(t['tot'])} for l, t in zip(lab, T['tramos'])],
         'act': {'monto': 389407564, 'n': 390}, 'gj': {'monto': 27107198, 'n': 39, 'comp': 60}, 'multi': 58}
D = {'F': 1, 'months': a['meses'], 'cycles': ['nov 23–oct 24', 'nov 24–oct 25', 'nov 25–oct 26'], 'acc': acc, 'cob': cob, 'rs': rs, 'deuda': deuda, 'usdDeuda': 1550}

# ---------------- JS
js = open('/home/claude/work/old/js.txt', encoding='utf-8').read()
REP = [
    ("if(u&&['ars','cer','usd'].includes(u)) S.unit=u;", "if(u&&['ars','usd'].includes(u)) S.unit=u;"),
    ("const UN={ars:{lab:'millones de $ de sep-26',short:'$ M sep-26'},cer:{lab:'millones de unidades CER',short:'M u. CER'},usd:{lab:'millones de US$',short:'US$ M'}};",
     "const UN={ars:{lab:'millones de $ de oct-26',short:'$ M oct-26'},usd:{lab:'millones de US$',short:'US$ M'}};"),
    ("/* moneda: los importes base vienen en unidades CER (o USD) */", "/* moneda: los importes base vienen en pesos constantes de oct-26 (CER) o en USD */"),
    ("Deuda exigible al 30/09/2026", "Deuda exigible al 31/10/2026"),
    ("document.getElementById('unitnote').textContent = 'Flujos por ciclo en '+UN[S.unit].lab+(S.unit==='cer'?' (como en los tableros); la deuda, en pesos nominales.':S.unit==='usd'?'; la deuda, a $1.550 por dólar.':'; la deuda, en pesos nominales al cierre.');",
     "document.getElementById('unitnote').textContent = 'Flujos por ciclo en '+UN[S.unit].lab+(S.unit==='usd'?'; la deuda, a $1.550 por dólar.':'; la deuda, en pesos nominales al 31/10/2026.');"),
    ("d.years[i].replace(' (a sep)','').replace(/^20/,\"'\") : d.years[i].replace(' (a sep)','')", "d.years[i].replace(' (a oct)','').replace(/^20/,\"'\") : d.years[i].replace(' (a oct)','')"),
    ("' · 2026 hasta septiembre'", "' · 2026 hasta octubre'"),
    ("Total 34 dependencias", "Total 33 dependencias"),
    ("'Ver las 34 dependencias'", "'Ver las 33 dependencias'"),
    ("{h:S.unit==='usd'?'Neto/ticket (US$)':S.unit==='cer'?'Neto/ticket (u. CER)':'Neto/ticket ($)'", "{h:S.unit==='usd'?'Neto/ticket (US$)':'Neto/ticket ($)'"),
]
for o, n in REP:
    assert o in js, o[:60]
    js = js.replace(o, n)
js = js.replace("<b class=\"num\">", "<b class=\"num\">")

# ---------------- CSS
css = open('/home/claude/work/old/css.txt', encoding='utf-8').read()
css = css.replace('</style>', """
/* encabezado institucional y acceso al PDF */
.head-row{display:grid;grid-template-columns:auto minmax(0,1fr);gap:18px;align-items:center}
.brand{width:74px;height:74px;border-radius:50%;background:#fff;display:grid;place-items:center;overflow:hidden;flex:none}
.brand img{width:100%;height:100%;object-fit:contain;display:block}
@media(max-width:520px){.brand{width:56px;height:56px}}
.head-actions{display:flex;flex-wrap:wrap;gap:10px}
.pdf-btn{display:inline-flex;align-items:center;gap:8px;background:var(--forest);color:var(--on-forest);border:1.5px solid var(--forest);border-radius:2px;padding:9px 13px;font-size:12.5px;font-weight:700;text-decoration:none;line-height:1}
.pdf-btn:hover{background:var(--forest-2);border-color:var(--forest-2)}
.pdf-btn:focus-visible,.doc-link:focus-visible{outline:2px solid var(--amber);outline-offset:2px}
.pdf-btn svg{width:12px;height:14px}
nav.toc a.pdf-link{color:var(--forest)}
/* informes de origen */
.sources{display:grid;gap:8px;padding-block:14px 4px}
.sources .lbl{font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);font-weight:700}
.src-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
@media(max-width:760px){.src-grid{grid-template-columns:minmax(0,1fr)}}
.src{display:grid;gap:3px;background:var(--panel);border:1px solid var(--line);border-radius:2px;padding:10px 13px;color:var(--ink);text-decoration:none;min-width:0}
.src:hover{border-color:var(--forest);background:var(--panel-2)}
.src:focus-visible,.sec-link:focus-visible{outline:2px solid var(--amber);outline-offset:2px}
.src b{font-size:13.5px;color:var(--forest)}
.src span{font-size:12px;color:var(--muted)}
.src b::after{content:" ↗";font-weight:400}
.sec-link{justify-self:start;font-size:12.5px;font-weight:600;color:var(--forest);text-decoration:none;border-bottom:1.5px solid var(--amber)}
</style>""")

logo = base64.b64encode(open('/home/claude/work/assets/logo.png', 'rb').read()).decode()
t2 = T['t2']

html = f"""<title>Tablero de control APN</title>
<meta name="description" content="Accesos, cobranzas y deuda de la Administración de Parques Nacionales en los ciclos nov 23–oct 24, nov 24–oct 25 y nov 25–oct 26, con deuda al 31/10/2026.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@75..100,400..800&display=swap">
{css}

<div class="wrap">
<header class="top">
  <div class="head-row">
    <div class="brand"><img alt="Logo de la Administración de Parques Nacionales" src="data:image/png;base64,{logo}"></div>
    <div class="head-body">
      <div class="eyebrow">Administración de Parques Nacionales<br><span>Dirección Nacional de Uso Público · Dirección de Concesiones</span></div>
      <h1>Tablero de control APN – <em>accesos, cobranzas y deuda, noviembre 2023 a octubre 2026</em></h1>
    </div>
  </div>
  <div class="head-body" style="margin-top:12px">
    <p class="sub">Desplazando el cursor sobre los gráficos se observa el detalle mensual; haciendo clic en la lista de series se aíslan las categorías de visitante o se abre una dependencia. Los controles permiten cambiar la moneda, la medida de accesos y el universo de cobranza, y cada tabla se ordena desde su encabezado.</p>
    <div class="meta"><span><b>3.708.182</b> tickets en el último ciclo</span><span><b>11</b> dependencias con venta</span><span><b>3.904</b> deudores</span><span><b>33</b> dependencias con deuda</span><span>Corte: <b>31/10/2026</b></span></div>
    <div class="head-actions noprint">
      <a class="pdf-btn" data-pdf href="{PDF}" target="_blank" rel="noopener"><svg viewBox="0 0 12 14" aria-hidden="true"><path d="M1 1h6l4 4v8H1z" fill="none" stroke="currentColor" stroke-width="1.3"/><path d="M7 1v4h4" fill="none" stroke="currentColor" stroke-width="1.3"/></svg>Informe PDF · 24 láminas</a>
      <a class="doc-link" href="{DOC}" target="_blank" rel="noopener"><svg viewBox="0 0 12 14" aria-hidden="true"><path d="M1 1h6l4 4v8H1z" fill="none" stroke="currentColor" stroke-width="1.3"/><path d="M7 1v4h4" fill="none" stroke="currentColor" stroke-width="1.3"/></svg>Informe consolidado <span class="dl-sub">Documento editable</span></a>
    </div>
    <p class="printonly note">Flujos en millones de pesos de octubre de 2026 (CER); deuda en pesos nominales al 31/10/2026.</p>
  </div>
</header>

<div class="sources noprint" aria-label="Informes de origen">
  <div class="lbl">Informes de origen · tableros completos con su informe PDF</div>
  <div class="src-grid">
    <a class="src" href="https://ffa-argentina.github.io/APN_Estadistica_Accesos/" target="_blank" rel="noopener"><b>Accesos</b><span>Evolución mensual por dependencia · nov 2023 – oct 2026</span></a>
    <a class="src" href="https://ffa-argentina.github.io/ingresos-APN/" target="_blank" rel="noopener"><b>Cobranzas</b><span>Operadores turísticos, ingresos reales · ago 2023 – oct 2026</span></a>
    <a class="src" href="https://ffa-argentina.github.io/APN_Informe_Deudores/" target="_blank" rel="noopener"><b>Deudas</b><span>Deuda exigible de prestadores turísticos · al 31/10/2026</span></a>
  </div>
</div>

<nav class="toc" aria-label="Secciones">
  <div class="ctl"><span class="lbl">Secciones</span><div class="links"><a href="#resumen">Resumen</a><a href="#accesos">Accesos</a><a href="#cobranzas">Cobranzas</a><a href="#deuda">Deuda</a><a href="#cruzados">Cruzados</a><a href="#conclusiones">Conclusiones</a><a href="#metodologia">Metodología</a><a class="pdf-link" data-pdf href="{PDF}" target="_blank" rel="noopener">Informe PDF ↗</a></div></div>
  <div class="ctl"><span class="lbl" id="unit-l">Unidad</span><div class="seg" role="group" aria-labelledby="unit-l" id="unit">
    <button data-u="ars" aria-pressed="true">$ de oct-26</button><button data-u="usd" aria-pressed="false">Dólares</button>
  </div></div>
</nav>

<section class="sec" id="resumen">
  <div class="sec-head"><div class="eyebrow">Resumen</div><h2>Cifras del trienio</h2><p>En tres ciclos la APN vendió 8,6% más accesos, pero en el último cobró menos en términos reales por boletería (−11,0% interanual) y a prestadores (−11,1%). La deuda exigible de prestadores al 31/10/2026 equivale al 5,6% de la cobranza anual a prestadores.</p><p class="muted" id="unitnote"></p></div>
  <div class="kpis" id="kpis"></div>
  <ul class="findings">
    <li><b>Accesos.</b> Tickets de no residentes +24,6% interanual y residentes −16,1%. El neto por ticket de no residentes bajó 25,3% en pesos constantes, y eso explica la caída del ingreso neto.</li>
    <li><b>Comisiones.</b> Las tercerizadoras retuvieron el 49,0% de lo percibido en el último ciclo (44,9% en el anterior), casi lo mismo que el ingreso neto que quedó para la APN. En Iguazú, el 61,7%.</li>
    <li><b>Cobranzas.</b> La cobranza a prestadores cayó en los tres ciclos (−18,6% en el trienio), con Tierra del Fuego en −52,8% y Glaciares en −27,4%.</li>
    <li><b>Deuda.</b> $1.507,0 M brutos y $1.317,9 M netos (−4,4% frente a septiembre); el 78,9% del capital se originó en 2025–2026. Nahuel Huapi concentra el 42,2% y sólo el 25,8% es de prestadores con habilitación vigente.</li>
  </ul>
</section>

<section class="sec" id="accesos">
  <div class="sec-head"><div class="eyebrow">1 · Accesos</div><h2>Más visitas, menos ingreso real por visita</h2>
  <p>Los tickets crecieron 8,6% en el trienio y los días de visita 41,5%, pero el ingreso neto real del último ciclo quedó 11,0% debajo del anterior: la tarifa no acompañó la inflación y las comisiones subieron.</p><a class="sec-link noprint" href="https://ffa-argentina.github.io/APN_Estadistica_Accesos/" target="_blank" rel="noopener">Abrir el tablero de accesos ↗</a></div>
  <div class="panel">
    <div class="controls">
      <div class="ctl"><span class="lbl" id="am-l">Medida</span><div class="seg" id="amet" role="group" aria-labelledby="am-l">
        <button data-m="t" aria-pressed="true">Tickets</button><button data-m="d" aria-pressed="false">Días de visita</button><button data-m="n" aria-pressed="false">Ingreso neto</button><button data-m="c" aria-pressed="false">Comisiones</button><button data-m="i" aria-pressed="false">Teórico</button></div></div>
      <div class="ctl"><label for="adep">Dependencia</label><select id="adep"></select></div>
    </div>
    <div class="grid">
      <div class="chartcard"><div class="chart-head"><h3 class="chart-title" id="a-title"></h3><span class="chart-unit" id="a-unit"></span></div><div class="chart" id="achart"></div></div>
      <aside class="serbox"><div class="lbl">Series · categorías</div><div class="serlist" id="aser"></div><p class="hint">Clic para quitar o sumar una categoría; las barras se apilan con las activas. Valores del ciclo nov 25–oct 26.</p></aside>
    </div>
    <div class="tablebox"><table id="acyc"></table></div>
  </div>
  <div class="panel">
    <div class="panel-head"><h3>Por dependencia · nov 25–oct 26</h3><p class="noprint">Clic en un encabezado para ordenar.</p></div>
    <div class="tablebox"><table id="adeps"></table></div>
    <p class="note">Los Alerces y Casa Central se incorporaron al registro durante el primer ciclo: su variación trienal figura como s/base. Lago Puelo y Laguna Blanca sólo registraron ventas residuales en 2023–2024. En Glaciares cambió el agente de cobro en mayo de 2025. La comisión de Iguazú conviene validarla con el contrato de la tercerizadora.</p>
  </div>
</section>

<section class="sec" id="cobranzas">
  <div class="sec-head"><div class="eyebrow">2 · Cobranzas</div><h2>La cobranza a prestadores cae tres ciclos seguidos</h2>
  <p>En pesos constantes la cobranza a prestadores turísticos pasó de $33.248 M a $27.049 M de oct-26 (−18,6%). La caída se repite en los tres universos; en dólares sube porque el tipo de cambio aumentó menos que la inflación.</p><a class="sec-link noprint" href="https://ffa-argentina.github.io/ingresos-APN/" target="_blank" rel="noopener">Abrir el tablero de cobranzas ↗</a></div>
  <div class="panel">
    <div class="controls">
      <div class="ctl"><span class="lbl" id="cu-l">Universo</span><div class="seg" id="cuniv" role="group" aria-labelledby="cu-l">
        <button data-k="ddjj" aria-pressed="false">Concesionarios y permisionarios</button><button data-k="pt" aria-pressed="true">Prestadores turísticos</button><button data-k="all_ex" aria-pressed="false">Todos los pagos</button></div></div>
    </div>
    <div class="grid">
      <div class="chartcard"><div class="chart-head"><h3 class="chart-title" id="c-title"></h3><span class="chart-unit"><i class="sw" style="background:var(--bar)"></i>Mensual · <i class="sw" style="background:var(--amber);height:3px;vertical-align:3px"></i>Media móvil de 3 meses</span></div><div class="chart" id="cchart"></div></div>
      <aside class="serbox"><div class="lbl">Series · dependencias</div><div class="serlist" id="cser"></div><p class="hint">Clic en una dependencia para abrir su serie; clic de nuevo vuelve al total. Valores del ciclo nov 25–oct 26.</p></aside>
    </div>
    <div class="cycbox" id="ccyc"></div>
  </div>
  <div class="stack">
    <div class="panel"><div class="panel-head"><h3 id="cdep-title">Por dependencia</h3></div><div class="tablebox"><table id="cdeps"></table></div></div>
    <div class="panel"><div class="panel-head"><h3>Principales pagadores · prestadores turísticos</h3></div><div class="tablebox"><table id="crs"></table></div>
    <p class="note">Iguazú Argentina S.A. aporta el 29,3% y los diez primeros, el 86,7%. Nueve de los diez pagan menos que en nov 23–oct 24.</p></div>
  </div>
</section>

<section class="sec" id="deuda">
  <div class="sec-head"><div class="eyebrow">3 · Deuda exigible al 31/10/2026</div><h2>Deuda reciente, concentrada y mayormente de no habilitados</h2>
  <p>La deuda de prestadores suma $1.507,0 M brutos y $1.317,9 M netos de pagos a cuenta, entre 3.904 deudores de 33 dependencias. Frente a septiembre la neta cae 4,4%, sobre todo por la salida de Marpatag S.R.L. ($55,8 M). Se expresa en pesos nominales al cierre o en dólares a $1.550.</p><a class="sec-link noprint" href="https://ffa-argentina.github.io/APN_Informe_Deudores/" target="_blank" rel="noopener">Abrir el tablero de deudas ↗</a></div>
  <div class="two">
    <div class="panel"><div class="panel-head"><h3>Composición</h3></div><div class="tablebox"><table id="dkpi"></table></div>
      <p class="note">El 88,3% de los pagos a cuenta conciliados corresponde a Nahuel Huapi; el resto, sobre todo a Glaciares, Los Alerces y Tierra del Fuego.</p></div>
    <div class="panel"><div class="panel-head"><h3>El 78,9% del capital se originó en 2025 y 2026</h3><p id="dsub">Capital impago según año de origen del comprobante · $ M nominales · 2026 hasta octubre</p></div><div class="chart" id="dchart"></div></div>
  </div>
  <div class="panel">
    <div class="panel-head"><h3>Por dependencia</h3><p>Cinco dependencias concentran el 91,8% de la deuda.</p></div>
    <div class="tablebox"><table id="ddeps"></table></div>
    <button class="more" id="dmore" type="button">Ver las 33 dependencias</button>
    <p class="note">La suma de deudores por dependencia (3.964) supera el total (3.904) porque 58 deudores tienen saldo en más de una dependencia.</p>
  </div>
  <div class="two">
    <div class="panel"><div class="panel-head"><h3>Diez mayores deudores · 36,2% de la deuda</h3></div><div class="tablebox"><table id="dtop"></table></div></div>
    <div class="panel"><div class="panel-head"><h3>Concentración por tramo</h3></div><div class="tablebox"><table id="dtram"></table></div>
      <p class="note">Habilitación vigente: 390 deudores, $389,4 M (25,8%), con intereses del 18,8% de su saldo. Gestión judicial: 39 deudores y 60 comprobantes, $27,1 M (1,8%), con 75,5% de intereses. Ninguno de los diez mayores deudores está en gestión judicial.</p></div>
  </div>
</section>

<section class="sec" id="cruzados">
  <div class="sec-head"><div class="eyebrow">4 · Indicadores cruzados</div><h2>Relación entre volumen de la deuda y de las cobranzas</h2>
  <p>Para el conjunto de la APN la deuda equivale al 5,6% de la cobranza anual a prestadores. En Lanín llega al 31,6% y en El Palmar, Lago Puelo, Los Alerces y Nahuel Huapi supera el 13%. En Iguazú y Glaciares, donde se concentra la cobranza, es marginal.</p></div>
  <div class="stack">
    <div class="panel"><div class="panel-head"><h3>Deuda sobre cobranza a prestadores</h3><p>Deuda al 31/10/2026 sobre cobranza nov 25–oct 26, en %</p></div><div class="chart" id="xchart"></div></div>
    <div class="panel"><div class="panel-head"><h3>Flujos y stock por dependencia</h3></div><div class="tablebox"><table id="xtab"></table></div>
      <p class="note">Flujos del ciclo nov 25–oct 26 en la moneda elegida; deuda al cierre. En Lanín y Tierra del Fuego casi toda la deuda es de prestadores sin habilitación vigente.</p></div>
  </div>
</section>

<section class="sec" id="conclusiones">
  <div class="sec-head"><div class="eyebrow">5 · Conclusiones</div><h2>Alertas para la gestión</h2></div>
  <ol class="concl">
    <li><b>Tarifas detrás de la inflación.</b> El neto por ticket cayó 9,3% en el último ciclo (25,3% en no residentes); con tickets casi estables, la recaudación real de accesos bajó 11,0%.</li>
    <li><b>Peso de las comisiones.</b> Las tercerizadoras retienen el 49,0% de lo percibido, y en Iguazú el 61,7%: un costo equivalente al ingreso neto de la APN.</li>
    <li><b>Cobranza a prestadores en baja sostenida.</b> −18,6% real en el trienio, explicada sobre todo por Tierra del Fuego (−52,8%) y Glaciares (−27,4%).</li>
    <li><b>Deuda reciente y fuera de la palanca del permiso.</b> El 78,9% del capital se originó en 2025–2026 y el 74,2% de la deuda es de prestadores sin habilitación vigente. La gestión judicial cubre sólo el 1,8%.</li>
    <li><b>Focos por dependencia.</b> Lanín (deuda del 31,6% de su cobranza) y Nahuel Huapi (42,2% de la deuda total y 62,2% de la de habilitados) concentran el riesgo de cobro. Iguazú y Glaciares sostienen el 69,7% de la cobranza y el 72,6% del neto de accesos.</li>
  </ol>
</section>

<section class="sec" id="metodologia">
  <div class="sec-head"><div class="eyebrow">Metodología</div><h2>Cómo leer estos números</h2></div>
  <div class="method">
    <p><b>Ciclos.</b> Doce meses de noviembre a octubre, contados hacia atrás desde el 31/10/2026. «i.a.» compara el último ciclo con el anterior y «trienal», el último con el primero. Si el ciclo base no llega a la décima parte del comparado, la variación se informa como s/base.</p>
    <p><b>Moneda.</b> «$ de oct-26» son los pesos constantes de los tableros de origen: cada importe diario se multiplica por el cociente entre el CER del 31/10/2026 (862,80) y el CER del día. Dólares: accesos y cobranzas a la cotización de cada día (blue hasta el 12/12/2023 y oficial minorista vendedor desde el 13/12/2023); deuda a la paridad de referencia de $1.550.</p>
    <p><b>Universos de cobranza.</b> Concesionarios y permisionarios (42 razones sociales con declaración jurada) ⊂ prestadores turísticos ⊂ todos los pagos. Se excluyen los medios de pago electrónicos, registrados sólo hasta julio de 2025.</p>
    <p><b>Deuda.</b> Comprobantes vencidos al 31/10/2026 con saldo impago (liquidaciones, facturas, multas y notas de débito), con intereses a tasa activa del Banco de la Nación desde el vencimiento, en pesos nominales. La antigüedad se mide por el año de origen del capital hoy impago y no reconstruye el stock histórico. El cociente deuda/cobranza usa pesos de oct-26; el informe de cobranzas lo calcula en pesos corrientes y obtiene valores algo mayores.</p>
    <p><b>Accesos y cobranzas no se suman.</b> Provienen de sistemas distintos y «todos los pagos» puede incluir importes vinculados a accesos.</p>
  </div>
</section>

<footer><b>Fuente.</b> Elaboración consolidada sobre los tableros <a href="https://ffa-argentina.github.io/APN_Estadistica_Accesos/" target="_blank" rel="noopener">«Accesos · Evolución mensual por dependencia»</a>, <a href="https://ffa-argentina.github.io/ingresos-APN/" target="_blank" rel="noopener">«Cobranzas · Operadores turísticos · Ingresos reales (CER)»</a> y <a href="https://ffa-argentina.github.io/APN_Informe_Deudores/" target="_blank" rel="noopener">«Deuda de prestadores turísticos · 31/10/2026»</a>, de la Dirección Nacional de Uso Público y la Dirección de Concesiones, con información disponible en ReNaRI. <a data-pdf href="{PDF}" target="_blank" rel="noopener">Informe PDF ↗</a></footer>
</div>

<script>
const D = {json.dumps(D, ensure_ascii=False, separators=(',', ':'))};
{js}
</script>
"""
open('/home/claude/work/out/tablero.html', 'w', encoding='utf-8').write(html)
print(len(html))
