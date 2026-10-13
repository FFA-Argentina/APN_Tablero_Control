#!/usr/bin/env python3
"""Genera descargas/tablero-de-control-apn.html: el tablero de control en un único archivo.

Incrusta en index.html los datos (data/datos.js), la tipografía, el logo y el
informe en PDF, y quita lo que sólo tiene sentido en la app publicada (service
worker, manifiesto y enlace de descarga). El resultado se abre con doble clic,
sin conexión y sin servidor, en cualquier navegador de escritorio o del
teléfono; los botones «Informe PDF» abren el PDF incrustado en una pestaña nueva.

Uso:
    python3 tools/generar_descargable.py
"""
import base64
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, 'descargas', 'tablero-de-control-apn.html')

# Abre el PDF incrustado: lo decodifica una sola vez y lo muestra en una pestaña nueva.
ABRIR_PDF = """<script>
(function(){
  var nodo=document.getElementById('informe-pdf-b64'), url=null;
  if(!nodo) return;
  function pdfUrl(){
    if(url) return url;
    var bin=atob(nodo.textContent.replace(/\\s+/g,'')), n=bin.length, u=new Uint8Array(n);
    for(var i=0;i<n;i++) u[i]=bin.charCodeAt(i);
    url=URL.createObjectURL(new Blob([u],{type:'application/pdf'}));
    return url;
  }
  document.querySelectorAll('a[data-pdf]').forEach(function(a){
    a.addEventListener('click',function(e){
      e.preventDefault();
      var t=document.createElement('a');
      t.href=pdfUrl(); t.target='_blank'; t.rel='noopener';
      document.body.appendChild(t); t.click(); t.remove();
    });
  });
})();
</script>
"""


def leer(rel, binario=False):
    with open(os.path.join(RAIZ, rel), 'rb' if binario else 'r', **({} if binario else {'encoding': 'utf-8'})) as fh:
        return fh.read()


def b64(rel):
    return base64.b64encode(leer(rel, True)).decode()


def quitar(html, patron, obligatorio=True):
    nuevo, n = re.subn(patron, '', html, flags=re.S)
    if obligatorio and not n:
        sys.exit(f'No se encontró en index.html: {patron}')
    return nuevo


def main():
    html = leer('index.html')
    datos = leer('data/datos.js')

    # ruta del PDF: la que usan los botones del tablero
    m = re.search(r'<a [^>]*data-pdf[^>]*href="([^"]+\.pdf)"', html) or re.search(r'<a [^>]*href="([^"]+\.pdf)"[^>]*data-pdf', html)
    if not m:
        sys.exit('index.html no tiene enlaces al informe PDF con el atributo data-pdf.')
    ruta_pdf = m.group(1)
    if not os.path.exists(os.path.join(RAIZ, ruta_pdf)):
        sys.exit(f'No existe el PDF {ruta_pdf}.')
    nombre_pdf = os.path.basename(ruta_pdf)

    # datos incrustados en lugar del archivo externo
    html = html.replace('<script src="data/datos.js"></script>', '<script>\n' + datos.replace('</script', '<\\/script') + '</script>', 1)
    # tipografía y logo como data URI
    html = html.replace('url(fonts/archivo-latin.woff2)', 'url(data:font/woff2;base64,' + b64('fonts/archivo-latin.woff2') + ')')
    html = html.replace('url(fonts/archivo-latin-ext.woff2)', 'url(data:font/woff2;base64,' + b64('fonts/archivo-latin-ext.woff2') + ')')
    html = html.replace('src="icons/logo-apn.png"', 'src="data:image/png;base64,' + b64('icons/logo-apn.png') + '"')
    html = html.replace('href="icons/favicon.ico"', 'href="data:image/png;base64,' + b64('icons/icon-192.png') + '"', 1)
    # botones del PDF: abren la copia incrustada
    html = html.replace(f'href="{ruta_pdf}"', f'href="#informe-pdf" data-nombre="{nombre_pdf}"')
    # lo que sólo sirve en la app publicada
    html = quitar(html, r'<link rel="manifest"[^>]*>\n?')
    html = quitar(html, r'<link rel="icon" type="image/png"[^>]*>\n?')
    html = quitar(html, r'<link rel="apple-touch-icon"[^>]*>\n?')
    html = quitar(html, r'<link rel="preload"[^>]*>\n?')
    html = quitar(html, r'\s*<a class="doc-link" id="dl-html".*?</a>')
    html = quitar(html, r'<div class="upd noprint".*?</div>\n?')
    html = quitar(html, r'<script>\n/\* PWA:.*?</script>\n?')
    html = html.replace('<meta name="apple-mobile-web-app-capable" content="yes">\n', '')
    # el PDF va al final del documento, fuera de la vista
    pdf = '<script type="application/octet-stream" id="informe-pdf-b64">' + b64(ruta_pdf) + '</script>\n'
    html = html.replace('</body>', pdf + ABRIR_PDF + '</body>', 1)

    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, 'w', encoding='utf-8') as fh:
        fh.write(html)
    print(f'Listo: {SALIDA} ({len(html.encode()) / 1024:.0f} KB, con {nombre_pdf} incrustado)')


if __name__ == '__main__':
    main()
