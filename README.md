# Tablero de control · APN

Tablero de control de la Administración de Parques Nacionales (Dirección Nacional de Uso Público · Dirección de Concesiones) para el trienio **octubre 2023 – septiembre 2026**. Reúne:

- **Accesos:** tickets, días de visita, ingreso neto de comisiones, comisiones a tercerizadoras e ingreso teórico, por categoría de visitante y por dependencia.
- **Cobranzas:** cobranza mensual a prestadores en tres universos (concesionarios y permisionarios, prestadores turísticos y todos los pagos), por dependencia y por razón social.
- **Deuda:** stock de deuda exigible de prestadores turísticos al 30/09/2026, con su composición, antigüedad, concentración, habilitación vigente y gestión judicial.
- **Indicadores cruzados:** la deuda frente a la cobranza anual por dependencia.

Es una **aplicación web progresiva (PWA)**: se abre en cualquier navegador, se instala en Android e iOS como una app y, una vez abierta, funciona sin conexión.

## Contenido del repositorio

```
├── index.html                  Tablero de control (la app)
├── manifest.webmanifest        Manifiesto de la PWA: nombre, íconos, colores
├── sw.js                       Service worker: uso sin conexión y aviso de versión nueva
├── data/datos.js               Datos del tablero (generados, no editar a mano)
├── fonts/                      Tipografía Archivo (licencia OFL, ver OFL-Archivo.txt)
├── icons/                      Logo, íconos de la app y favicon
├── informe/                    Tablero de control en PDF (22 láminas)
├── descargas/                  Tablero de control en un único archivo HTML descargable
├── tools/
│   ├── actualizar_datos.py     Regenera data/datos.js desde los tres tableros de origen
│   └── generar_descargable.py  Regenera descargas/tablero-de-control-apn.html
└── .github/workflows/pages.yml Publicación automática en GitHub Pages
```

## Publicar en GitHub Pages

1. Crear el repositorio en GitHub y subir estos archivos a la rama `main`:
   ```bash
   git init
   git add .
   git commit -m "Tablero de control APN · trienio 2023-2026"
   git branch -M main
   git remote add origin https://github.com/<usuario-u-organización>/<repositorio>.git
   git push -u origin main
   ```
2. En GitHub, entrar a **Settings → Pages** y, en **Build and deployment → Source**, elegir **GitHub Actions**.
3. Cada `push` a `main` publica el sitio. La dirección queda a la vista en la pestaña **Actions** y en **Settings → Pages**, con la forma `https://<usuario-u-organización>.github.io/<repositorio>/`.

GitHub Pages sirve el sitio por HTTPS, que es requisito para instalar la PWA y para el funcionamiento sin conexión. Todas las rutas son relativas, así que la app funciona igual en un subdirectorio, en un dominio propio o en otro servidor web institucional.

> **Privacidad.** El tablero incluye nombres de deudores, algunos de ellos personas humanas. En un repositorio público esos datos quedan visibles para cualquiera, también en el historial de versiones. Si más adelante se decide restringirlo, hay que pasar el repositorio a privado (GitHub Pages desde un repositorio privado requiere un plan pago) o quitar la tabla de mayores deudores de `data/datos.js` y de `informe/`.

## Instalar la app en el teléfono

**Android (Chrome, Edge o Samsung Internet).** Abrir la dirección del sitio, tocar el menú ⋮ y elegir **Instalar app** (o **Agregar a la pantalla principal**). El ícono queda junto a las demás apps y se abre a pantalla completa.

**iPhone y iPad (Safari).** Abrir la dirección en Safari, tocar **Compartir** (el cuadrado con la flecha) y elegir **Agregar a inicio**. Desde iOS 16.4 también puede hacerse desde Chrome o Edge con la misma opción del menú Compartir.

**Computadora (Chrome o Edge).** El ícono de instalación aparece en la barra de direcciones.

Una vez abierta por primera vez, la app guarda una copia completa (tablero, datos, informe PDF y versión descargable) y funciona sin conexión.

## Acceso al informe PDF

El tablero ofrece el informe en PDF desde dos lugares: el botón verde **Tablero de control · informe PDF** del encabezado y el enlace **Informe PDF ↗** de la barra de secciones, que queda fija al desplazarse. Ambos son enlaces con el atributo `data-pdf` que apuntan a `informe/Tablero_de_control_APN_2023-2026.pdf`:

- **En la app publicada** abren el PDF en una pestaña nueva. El service worker lo guarda, así que también abre sin conexión.
- **En el HTML descargable** el PDF va incrustado y los mismos botones lo abren en una pestaña nueva, sin conexión ni servidor.

## Versión descargable

`descargas/tablero-de-control-apn.html` es el tablero completo en un único archivo, con los datos, la tipografía, el logo y el informe PDF incrustados. Se puede enviar por correo, guardar en una carpeta compartida o abrir con doble clic, sin conexión y sin servidor. En la app se descarga desde el botón **Descargar el tablero · HTML** del encabezado. Pesa unos 820 KB porque incluye el PDF.

## Actualizar los datos

1. Generar los datos nuevos a partir de los tres tableros de origen:
   ```bash
   python3 tools/actualizar_datos.py \
     --accesos   ruta/al/tablero-de-accesos/index.html \
     --cobranzas ruta/al/tablero-de-cobranzas/index.html \
     --deuda     ruta/al/tablero-de-deuda/index.html
   ```
   El script toma los últimos 36 meses disponibles y arma tres ciclos de octubre a septiembre. También recalcula el factor CER del último mes, que convierte las unidades CER a pesos de ese mes. Sólo usa la biblioteca estándar de Python 3.8 o posterior.
2. Revisar en `index.html` los textos de análisis (titulares, lecturas, hallazgos y conclusiones). Están redactados para el corte al 30/09/2026 y no se recalculan solos.
3. Regenerar la versión descargable:
   ```bash
   python3 tools/generar_descargable.py
   ```
4. Si cambia el informe, reemplazar el PDF en `informe/`. Si cambia su nombre, actualizarlo en los dos enlaces con `data-pdf` de `index.html` y en la lista `ARCHIVOS` de `sw.js`. El generador del HTML descargable toma la ruta de esos enlaces e incrusta el PDF.
5. Cambiar `VERSION` en `sw.js` (por ejemplo `2026-12-31.1`). Así las apps ya instaladas muestran **«Hay una versión más reciente del tablero · Actualizar»**.
6. Hacer `commit` y `push`: GitHub Actions publica la versión nueva.

Para probar localmente antes de publicar:
```bash
python3 -m http.server 8000
# abrir http://localhost:8000
```

## Criterios de medición

- **Ciclos:** doce meses de octubre a septiembre. «Var. i.a.» compara el último ciclo con el anterior; «trienal», el último con el primero. Si el ciclo base no llega a la décima parte del siguiente, la variación figura como s/base.
- **Moneda:** «$ de sep-26» multiplica las unidades CER de los tableros (importe diario dividido por el CER del día) por 840,1, el CER promedio implícito de septiembre de 2026. «Unidades CER» muestra las cifras como en los tableros. En dólares, los accesos usan dólar blue hasta el 12/12/2023 y oficial desde el 13/12/2023, las cobranzas el tipo de cambio minorista vendedor del día y la deuda una paridad de referencia de $ 1.550.
- **Cobranzas:** se excluyen los medios de pago electrónicos, registrados sólo hasta julio de 2025.
- **Deuda:** comprobantes con saldo impago e intereses a tasa activa del Banco de la Nación, en pesos nominales al 30/09/2026.
- **Accesos y cobranzas no se suman:** provienen de sistemas distintos y pueden solaparse.

Fuente: elaboración propia sobre los tableros «Evolución mensual de accesos por dependencia», «Cobranzas · evolución mensual» y «Deuda exigible de prestadores turísticos», con información disponible en ReNaRI.
