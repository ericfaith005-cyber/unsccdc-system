// 🛡️ UNSCCDC INDESTRUCTIBLE GUARD v3.0
const CACHE_NAME = 'unsccdc-sovereign-vault-v1';
const Hub_FILES = [
    '/',
    '/api/home/',
    '/static/css/unsccdc_prestige.css',
    '/static/icons/hub_logo.png'
];

// 📥 1. FORCED INSTALLATION
self.addEventListener('install', (event) => {
    self.skipWaiting(); 
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(Hub_FILES);
        })
    );
});

// ⚡ 2. CLAIM THE BROWSER
self.addEventListener('activate', (event) => {
    event.waitUntil(clients.claim()); 
});

// 📡 3. THE Hub OFFLINE STRATEGY (Network First, then Cache)
self.addEventListener('fetch', (event) => {
    event.respondWith(
        fetch(event.request).catch(() => {
            return caches.match(event.request);
        })
    );
});