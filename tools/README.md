# Actualización del Tablero de control APN

Corte actual: **31/10/2026** · ciclos nov–oct (nov 23–oct 24, nov 24–oct 25, nov 25–oct 26) · flujos en pesos de octubre de 2026 (CER de los tableros) · deuda en pesos nominales y USD a $ 1.550.

Insumos (en `src/`, fuera del repositorio): los tres tableros HTML de origen (`accesos.html`, `cobranzas.html`, `deuda.html`), el `informe-deudas-31oct26.pdf` y los informes de accesos y cobranzas en PDF.

Orden de ejecución (Python 3, `reportlab`, `Pillow`, `fontTools`; fuentes Lato en `fonts/`):

1. `extract.py` — lee los datos incrustados (`window.__DATA__`, `const DATA`, `const PAYERS`) → `raw.json`.
2. `compute.py` — agrega por ciclo, dependencia, categoría y deudor → `agg.json`.
3. `pdftotext -layout informe-deudas-31oct26.pdf informe-deudas-31oct26.txt` y `parse_deuda_pdf.py` — importes exactos (con centavos) de las tablas de deuda → `deuda_pdf.json`.
4. `build.py` y `md.py` — tablas del informe → `tables.json`, `md.json`.
5. `pdf_build.py` — PDF de 24 láminas → `informe/`.
6. `dash_build.py` — tablero HTML; luego se separan `data/datos.js`, `index.html` y `descargas/tablero-de-control-apn.html` (PDF incrustado).

Para un nuevo corte: actualizar rutas, fechas de corte, `cycles` y los textos de lectura de `pdf_build.py` / `dash_build.py`, y cambiar el nombre de caché en `sw.js`.
