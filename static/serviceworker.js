// 🛡️ UNSCCDC SOVEREIGN SERVICE WORKER v1.2
const CACHE_NAME = 'unsccdc-national-cache-v1';
const STATIC_ASSETS = [
    '/',
    '/api/home/',
    '/static/css/unsccdc_prestige.css',
    '/static/icons/hub_logo.png',
    '/static/manifest.json'
];

// 1. 📥 INSTALLATION: Guarding the bricks
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(STATIC_ASSETS);
        })
    );
});

// 2. ⚡ FETCH: The 'Network First, then Cache' Strategy
// This ensures that if internet is there, we get fresh data. 
// If internet fails, we pull from the Sovereign Vault!
self.addEventListener('fetch', (event) => {
    event.respondWith(
        fetch(event.request).catch(() => {
            return caches.match(event.request);
        })
    );
});