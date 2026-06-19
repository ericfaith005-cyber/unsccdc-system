// 🛡️ UNSCCDC GLOBAL GUARDIAN v4.0 (OFFLINE SYSTEM REBIRTH)
const CACHE_NAME = 'unsccdc-system-v4';

// 1. 📥 Install: Save the foundation
self.addEventListener('install', (event) => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll([
                '/',
                '/api/home/',
                '/static/css/unsccdc_prestige.css',
                '/static/icons/hub_logo.png'
            ]);
        })
    );
});

// 2. ⚡ Activate: Claim control
self.addEventListener('activate', (event) => {
    event.waitUntil(clients.claim());
});

// 3. 📡 Fetch: THE OFFLINE Hub Hub Hub Hub Hub Hub STRATEGY
self.addEventListener('fetch', (event) => {
    // Only handle GET requests (standard page views)
    if (event.request.method !== 'GET') return;

    event.respondWith(
        fetch(event.request)
            .then((response) => {
                // If we have internet, save a copy of this page to the vault
                const resClone = response.clone();
                caches.open(CACHE_NAME).then((cache) => {
                    cache.put(event.request, resClone);
                });
                return response;
            })
            .catch(() => {
                // If internet fails, look in the vault for this specific URL
                return caches.match(event.request).then((cachedResponse) => {
                    return cachedResponse || caches.match('/'); // Fallback to Home
                });
            })
    );
});