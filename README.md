# Tablero de control APN

Accesos, cobranzas y deuda de la Administración de Parques Nacionales en los ciclos nov 2023 – oct 2024, nov 2024 – oct 2025 y nov 2025 – oct 2026, con la deuda al 31/10/2026.

Es una aplicación web progresiva (PWA): se abre en cualquier navegador, se instala en Android e iOS como una app y, una vez abierta, funciona sin conexión.

## Contenido del repositorio

```
├── index.html                  Tablero (la app)
├── manifest.webmanifest        Manifiesto de la PWA: nombre, íconos, colores
├── sw.js                       Service worker: uso sin conexión y aviso de versión nueva
├── data/datos.js               Datos del tablero
├── icons/                      Logo e íconos de la app
├── informe/                    Tablero de control en PDF (24 láminas)
├── descargas/                  Tablero en un único archivo HTML descargable, con el PDF adentro
├── tools/
│   └── generar_descargable.py  Regenera descargas/tablero-de-control-apn.html
└── .github/workflows/pages.yml Publicación automática en GitHub Pages
```

## Informes de origen

- Accesos: https://ffa-argentina.github.io/APN_Estadistica_Accesos/
- Cobranzas: https://ffa-argentina.github.io/ingresos-APN/
- Deudas: https://ffa-argentina.github.io/APN_Informe_Deudores/

## Actualizar el repositorio

1. Copiar el contenido de este zip sobre la carpeta del repositorio, reemplazando los archivos existentes. Los archivos que el zip no trae (por ejemplo, otros scripts de `tools/`) quedan como están.
2. Subir los cambios:
   ```bash
   git add .
   git commit -m "Tablero de control APN · corte 31/10/2026"
   git push
   ```
3. GitHub Actions publica el sitio solo. Si es la primera publicación, en **Settings → Pages → Build and deployment → Source** hay que elegir **GitHub Actions**.

Cada publicación cambia `VERSION` en `sw.js`. Así, quien tenga la app instalada ve el aviso «Hay una versión más reciente del tablero» y puede actualizarla con un toque.

## Regenerar el descargable

Si cambian `index.html`, `data/datos.js` o el PDF, se regenera el archivo único con:

```bash
python3 tools/generar_descargable.py
```

## Instalar la app en el teléfono

- **Android (Chrome, Edge o Samsung Internet):** abrir la dirección del sitio y elegir **Instalar app** o **Agregar a pantalla de inicio** en el menú.
- **iPhone o iPad (Safari):** abrir la dirección, tocar **Compartir** y luego **Agregar a pantalla de inicio**.

> **Privacidad.** El tablero incluye nombres de deudores, algunos de ellos personas humanas. En un repositorio público esos datos quedan visibles para cualquiera, también en el historial de versiones.
