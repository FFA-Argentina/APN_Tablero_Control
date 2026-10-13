/* Service worker del tablero de control APN.
   Cambiar VERSION en cada publicación: la app avisa «Hay una versión más reciente del tablero». */
const VERSION = '2026-09-30.4';
const CACHE = 'apn-tablero-' + VERSION;
const ARCHIVOS = [
  './',
  'index.html',
  'manifest.webmanifest',
  'data/datos.js',
  'fonts/archivo-latin.woff2',
  'fonts/archivo-latin-ext.woff2',
  'icons/logo-apn.png',
  'icons/icon-192.png',
  'icons/icon-512.png',
  'icons/maskable-512.png',
  'icons/apple-touch-icon.png',
  'icons/favicon.ico',
  'informe/Tablero_de_control_APN_2023-2026.pdf',
  'descargas/tablero-de-control-apn.html'
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ARCHIVOS)));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => (k.startsWith('apn-tablero-') || k.startsWith('apn-consolidado-')) && k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('message', (e) => {
  if (e.data === 'SKIP_WAITING') self.skipWaiting();
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) return;
  /* Páginas: primero la red (para ver la última versión) y, sin conexión, la copia guardada. */
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req)
        .then((r) => { const copia = r.clone(); caches.open(CACHE).then((c) => c.put(req, copia)); return r; })
        .catch(() => caches.match(req).then((r) => r || caches.match('index.html')))
    );
    return;
  }
  /* Resto de los archivos: copia guardada y, si falta, la red. */
  e.respondWith(
    caches.match(req).then((r) => r || fetch(req).then((resp) => {
      if (resp.ok) { const copia = resp.clone(); caches.open(CACHE).then((c) => c.put(req, copia)); }
      return resp;
    }))
  );
});
