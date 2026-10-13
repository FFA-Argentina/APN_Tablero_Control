#!/usr/bin/env python3
"""Regenera data/datos.js a partir de los tres tableros de origen.

Uso:
    python3 tools/actualizar_datos.py \
        --accesos   ruta/al/tablero-accesos/index.html \
        --cobranzas ruta/al/tablero-cobranzas/index.html \
        --deuda     ruta/al/tablero-deuda/index.html

El script lee los datos incrustados en cada tablero, arma tres ciclos de doce
meses (octubre a septiembre) que terminan en el último mes disponible y
escribe data/datos.js, que la app carga como window.APN_DATOS.

Los textos de análisis de index.html (titulares, lecturas y conclusiones)
están redactados para el corte al 30/09/2026: si se actualizan los datos,
hay que revisarlos a mano.
"""
import argparse
import bisect
import collections
import datetime
import json
import os
import re
import sys

SEG = ('RP', 'NR', 'NP')
MES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']


def extraer(ruta, patron):
    """Devuelve el objeto JSON que sigue al patrón dentro del HTML."""
    texto = open(ruta, encoding='utf-8').read()
    m = re.search(patron, texto)
    if not m:
        sys.exit(f'No se encontraron datos en {ruta} (patrón {patron!r}).')
    obj, _ = json.JSONDecoder().raw_decode(texto[m.end():].lstrip())
    return obj


def etiqueta_ciclo(m0, m1):
    a0, n0 = m0.split('-'); a1, n1 = m1.split('-')
    return f'{MES[int(n0) - 1]} {a0[2:]}–{MES[int(n1) - 1]} {a1[2:]}'


def main():
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--accesos', required=True)
    ap.add_argument('--cobranzas', required=True)
    ap.add_argument('--deuda', required=True)
    ap.add_argument('--salida', default=os.path.join(raiz, 'data', 'datos.js'))
    ap.add_argument('--json', help='además, guarda el mismo contenido como JSON')
    a = ap.parse_args()

    A = extraer(a.accesos, r'window\.__DATA__\s*=')
    C = extraer(a.cobranzas, r'const\s+DATA\s*=')
    D = extraer(a.deuda, r'const\s+DATA\s*=')

    # ---------- ventana de 36 meses ----------
    M = A['metrics']
    meses = A['meses'][-36:]
    off_a = len(A['meses']) - 36
    if len(meses) < 36:
        sys.exit('El tablero de accesos tiene menos de 36 meses.')
    try:
        off_c = C['months'].index(meses[0])
    except ValueError:
        sys.exit(f'El tablero de cobranzas no incluye el mes {meses[0]}.')
    if C['months'][off_c + 35] != meses[-1]:
        sys.exit('Los tableros de accesos y cobranzas no terminan en el mismo mes.')
    ciclos = [etiqueta_ciclo(meses[12 * c], meses[12 * c + 11]) for c in range(3)]
    r0 = lambda l: [round(x) for x in l]

    # ---------- factor CER: CER promedio implícito del último mes ----------
    i = off_a + 35; j = off_c + 35
    corr_a = sum(A['data'][d][g][M.index(k)][i] for d in A['deps'] for g in SEG for k in ('neto', 'com', 'ide'))
    cer_a = sum(A['data'][d][g][M.index(k + '_cer')][i] for d in A['deps'] for g in SEG for k in ('neto', 'com', 'ide'))
    corr_c = sum(r['corr'][j] for r in C['sets']['all_in']['dep'])
    cer_c = sum(r['cer'][j] for r in C['sets']['all_in']['dep'])
    F = round((corr_a + corr_c) / (cer_a + cer_c), 1)

    # ---------- accesos ----------
    depmap = {'Administración Central': 'Casa Central (pasaportes)', 'PN Los Glaciares': 'Glaciares'}
    dn = lambda d: depmap.get(d, d.replace('PN ', ''))
    acc = {'deps': [], 'data': {}}
    for d in A['deps']:
        nombre = dn(d); acc['deps'].append(nombre); acc['data'][nombre] = {}
        for g in SEG:
            x = A['data'][d][g]
            col = lambda k: r0(x[M.index(k)][off_a:off_a + 36])
            acc['data'][nombre][g] = {'t': col('t'), 'd': col('d'), 'n': col('neto_cer'), 'c': col('com_cer'),
                                      'i': col('ide_cer'), 'nu': col('neto_usd'), 'cu': col('com_usd'), 'iu': col('ide_usd')}

    # ---------- cobranzas ----------
    lab = {'ddjj': 'Concesionarios y permisionarios', 'pt': 'Prestadores turísticos', 'all_ex': 'Todos los pagos'}
    cob = {}
    for sk in ('ddjj', 'pt', 'all_ex'):
        deps = {}
        for r in C['sets'][sk]['dep']:
            nm = r['label'] if r['name'] != 'OTRAS DEPENDENCIAS' else 'Otras dependencias'
            deps[nm] = {'cer': r0(r['cer'][off_c:off_c + 36]), 'usd': r0(r['usd'][off_c:off_c + 36])}
        cob[sk] = {'label': lab[sk], 'deps': deps}
    nombres = {'IGUAZU ARGENTINA S.A.': 'Iguazú Argentina S.A.', 'HIELO Y AVENTURA SA': 'Hielo y Aventura S.A.',
               'LA GRAN AVENTURA NÁUTICA SRL': 'La Gran Aventura Náutica S.R.L.', 'SOLO PATAGONIA S.A.': 'Solo Patagonia S.A.',
               'LONDON SUPPLY SACIFI': 'London Supply S.A.C.I.F.I.', 'TRANEX TURISMO S.A.': 'Tranex Turismo S.A.',
               'TURISUR SRL': 'Turisur S.R.L.', 'ESPACIO SA': 'Espacio S.A.', 'MARPATAG SRL': 'Marpatag S.R.L.',
               'ESTANCIA CRISTINA SA': 'Estancia Cristina S.A.', 'OTROS PRESTADORES': 'Otros prestadores'}
    rs = [{'n': nombres.get(r['name'], r['label']), 'cer': r0(r['cer'][off_c:off_c + 36]), 'usd': r0(r['usd'][off_c:off_c + 36])}
          for r in C['sets']['pt']['rs']]

    # ---------- deuda ----------
    Y = D['years']; Fc = D['facts']; deps = D['deps']; deud = D['deudores']
    cap = sum(f[4][-1] for f in Fc); it = sum(f[5][-1] for f in Fc)
    pac = sum(f[6] + f[7] for f in Fc)
    origen = [0] * len(Y)
    for f in Fc:
        prev = 0
        for k, v in enumerate(f[4]):
            origen[f[3] + k] += v - prev; prev = v
    bd = collections.defaultdict(lambda: {'cap': 0, 'int': 0, 'pac': 0, 'comp': 0, 'deud': set(), 'gj': 0, 'act': 0})
    for f in Fc:
        b = bd[deps[f[1]]]
        b['cap'] += f[4][-1]; b['int'] += f[5][-1]; b['pac'] += f[6] + f[7]; b['comp'] += f[8]; b['deud'].add(f[0])
        if f[2]: b['gj'] += f[4][-1] + f[5][-1]
        if deud[f[0]][1] == 1: b['act'] += f[4][-1] + f[5][-1]
    por_dep = sorted(bd.items(), key=lambda x: -(x[1]['cap'] + x[1]['int']))
    por_deudor = collections.defaultdict(float)
    for f in Fc: por_deudor[f[0]] += f[4][-1] + f[5][-1]
    orden = sorted(por_deudor.items(), key=lambda x: -x[1])
    multi = collections.defaultdict(set)
    for f in Fc: multi[f[0]].add(f[1])
    tramos = collections.defaultdict(lambda: [0, 0.0])
    for _, x in orden:
        k = bisect.bisect([1e5, 1e6, 1e7, 1e8], x); tramos[k][0] += 1; tramos[k][1] += x
    nombres_tramo = ['Menos de $0,1 M', '$0,1 M a $1 M', '$1 M a $10 M', '$10 M a $100 M', '$100 M o más']
    ult = Y[-1]
    if re.match(r'^[a-z]{3}-\d\d$', ult):
        ult = f'20{ult[-2:]} (a {ult[:3]})'
    act = [f for f in Fc if deud[f[0]][1] == 1]
    gj = [f for f in Fc if f[2]]
    deuda = {
        'cap': cap, 'int': it, 'bruto': cap + it, 'pac': pac, 'neto': cap + it - pac,
        'comprob': sum(f[8] for f in Fc), 'deudores': len(deud), 'usd': D['usd'],
        'years': Y[:-1] + [ult], 'origen': r0(origen),
        'dep': [{'n': k, **{x: round(v[x]) for x in ('cap', 'int', 'pac', 'gj', 'act')}, 'deud': len(v['deud']), 'comp': v['comp']}
                for k, v in por_dep],
        'top10': [{'n': deud[i][0], 'dep': ', '.join(sorted({deps[f[1]] for f in Fc if f[0] == i})), 'm': round(x),
                   'act': deud[i][1], 'gj': any(f[2] for f in Fc if f[0] == i)} for i, x in orden[:10]],
        'tramos': [{'t': nombres_tramo[k], 'n': tramos[k][0], 'm': round(tramos[k][1])} for k in sorted(tramos)],
        'act': {'monto': round(sum(f[4][-1] + f[5][-1] for f in act)), 'cap': round(sum(f[4][-1] for f in act)),
                'int': round(sum(f[5][-1] for f in act)), 'n': sum(1 for i, _ in orden if deud[i][1] == 1)},
        'gj': {'monto': round(sum(f[4][-1] + f[5][-1] for f in gj)), 'cap': round(sum(f[4][-1] for f in gj)),
               'int': round(sum(f[5][-1] for f in gj)), 'n': len({f[0] for f in gj}), 'comp': sum(f[8] for f in gj)},
        'conc': {str(k): sum(x for _, x in orden[:k]) / (cap + it) for k in (1, 5, 10, 20, 50, 100)},
        'multi': sum(1 for v in multi.values() if len(v) > 1),
    }

    datos = {'F': F, 'months': meses, 'cycles': ciclos, 'acc': acc, 'cob': cob, 'rs': rs, 'deuda': deuda,
             'usdDeuda': D['usd'], 'generado': datetime.date.today().isoformat()}
    os.makedirs(os.path.dirname(a.salida), exist_ok=True)
    cuerpo = json.dumps(datos, ensure_ascii=False, separators=(',', ':'))
    with open(a.salida, 'w', encoding='utf-8') as fh:
        fh.write('/* Generado por tools/actualizar_datos.py — no editar a mano */\nwindow.APN_DATOS = ' + cuerpo + ';\n')
    if a.json:
        open(a.json, 'w', encoding='utf-8').write(cuerpo)
    print(f'Listo: {a.salida}')
    print(f'  Ciclos: {", ".join(ciclos)} · factor CER {F} · {len(acc["deps"])} dependencias con accesos · '
          f'{deuda["deudores"]} deudores')


if __name__ == '__main__':
    main()
