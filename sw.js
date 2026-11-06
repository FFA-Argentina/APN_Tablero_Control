/* Service worker del Tablero de control APN.
   Cambiar VERSION en cada publicación: quien tenga la app instalada verá el aviso de versión nueva. */
const VERSION = 'tablero-apn-2026-10-31g';
const ARCHIVOS = [
  './',
  'index.html',
  'data/datos.js',
  'manifest.webmanifest',
  'informe/Tablero_de_control_APN_nov23-oct26.pdf',
  'icons/icon-192.png',
  'icons/icon-512.png',
  'icons/logo.png'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(ARCHIVOS)));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('message', e => {
  if (e.data === 'skipWaiting') self.skipWaiting();
});

/* Primero la red (para ver siempre la última publicación); sin conexión, la copia guardada. */
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) {
    // Tipografía de Google Fonts: copia guardada si existe, si no la red.
    e.respondWith(
      caches.match(req).then(r => r || fetch(req).then(res => {
        const copia = res.clone();
        caches.open(VERSION).then(c => c.put(req, copia));
        return res;
      }))
    );
    return;
  }
  e.respondWith(
    fetch(req).then(res => {
      if (res.ok) {
        const copia = res.clone();
        caches.open(VERSION).then(c => c.put(req, copia));
      }
      return res;
    }).catch(() => caches.match(req).then(r => r || caches.match('index.html')))
  );
});
