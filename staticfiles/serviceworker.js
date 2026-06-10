// 🛡️ THE IMPERIAL SERVICE WORKER
const CACHE_NAME = 'unsccdc-v1';
const assetsToCache = [
    '/',
    '/static/css/unsccdc_prestige.css',
];

// Install Event
self.addEventListener('install', (event) => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(assetsToCache);
        })
    );
});

// Fetch Event (Allows app to open even with poor signal)
self.addEventListener('fetch', (event) => {
    event.respondWith(
        fetch(event.request).catch(() => {
            return caches.match(event.request);
        })
    );
});