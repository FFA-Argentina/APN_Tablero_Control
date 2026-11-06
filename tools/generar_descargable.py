#!/usr/bin/env python3
"""Regenera descargas/tablero-de-control-apn.html a partir de index.html,
data/datos.js y el PDF de informe/.

El descargable es un único archivo HTML que funciona sin servidor ni conexión:
lleva los datos adentro y el PDF incrustado, de modo que los botones
«Informe PDF» lo abren directamente.

Uso, desde la raíz del repositorio:
    python3 tools/generar_descargable.py
"""
import base64
import pathlib
import re

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDA = RAIZ / 'descargas' / 'tablero-de-control-apn.html'


def main():
    html = (RAIZ / 'index.html').read_text(encoding='utf-8')
    datos = (RAIZ / 'data' / 'datos.js').read_text(encoding='utf-8')

    m = re.search(r'window\.D = (\{.*\});', datos, re.S)
    if not m:
        raise SystemExit('No se encontró «window.D = {...};» en data/datos.js')
    objeto = m.group(1)

    # PDF que enlazan los botones del tablero
    rutas = set(re.findall(r'<a[^>]*data-pdf[^>]*href="([^"]+)"', html))
    rutas |= set(re.findall(r'<a[^>]*href="([^"]+\.pdf)"[^>]*data-pdf', html))
    if len(rutas) != 1:
        raise SystemExit(f'Se esperaba una sola ruta de PDF en los botones y hay: {sorted(rutas)}')
    ruta_pdf = rutas.pop()
    pdf = RAIZ / ruta_pdf
    nombre_pdf = pdf.name
    b64 = base64.b64encode(pdf.read_bytes()).decode()

    # Quitar lo propio de la app instalable
    html = re.sub(r'<meta name="theme-color"[^>]*>\n?', '', html)
    html = re.sub(r'<link rel="(manifest|icon|apple-touch-icon)"[^>]*>\n?', '', html)
    html = re.sub(r'<meta name="apple-mobile-web-app-[^"]*"[^>]*>\n?', '', html)
    html = re.sub(r'<div id="upd".*?</div>\n?', '', html, flags=re.S)
    html = re.sub(r"<script>\nif\('serviceWorker' in navigator\).*?</script>\n?", '', html, flags=re.S)

    # Datos adentro del archivo
    html = html.replace('<script src="data/datos.js"></script>\n<script>\nconst D = window.D;',
                        '<script>\nconst D = ' + objeto + ';', 1)
    if 'window.D' in html:
        raise SystemExit('No se pudo incrustar data/datos.js en el descargable')

    # Los botones apuntan al nombre del PDF y lo abren desde el archivo incrustado
    html = html.replace('href="' + ruta_pdf + '"', 'href="' + nombre_pdf + '"')
    script_pdf = (
        '<script>\n/* PDF incrustado: los botones abren el informe sin conexión ni servidor */\n(function(){\n'
        'const PDF_B64="' + b64 + '";\n'
        "let url=null;function u(){if(!url){const s=atob(PDF_B64),a=new Uint8Array(s.length);"
        "for(let i=0;i<s.length;i++)a[i]=s.charCodeAt(i);"
        "url=URL.createObjectURL(new Blob([a],{type:'application/pdf'}));}return url;}\n"
        "document.querySelectorAll('a[data-pdf]').forEach(a=>{a.addEventListener('click',e=>{e.preventDefault();"
        "const w=window.open(u(),'_blank');if(!w){const l=document.createElement('a');l.href=u();"
        "l.download='" + nombre_pdf + "';document.body.appendChild(l);l.click();l.remove();}});});\n"
        '})();\n</script>\n'
    )
    html = html.replace('</body>', script_pdf + '</body>', 1)

    SALIDA.parent.mkdir(exist_ok=True)
    SALIDA.write_text(html, encoding='utf-8')
    print(f'{SALIDA.relative_to(RAIZ)}: {SALIDA.stat().st_size / 1024:.0f} KB')


if __name__ == '__main__':
    main()
