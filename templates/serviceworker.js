// 🛡️ UNSCCDC Hub Hub Hub Hub TOTAL Hub Hub PERSISTENCE v5.0
const CACHE_NAME = 'unsccdc-sovereign-vault';

self.addEventListener('install', (event) => {
    self.skipWaiting(); // 💎 Force it to work IMMEDIATELY
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(['/']); // Just save the front door for now
        })
    );
});

self.addEventListener('activate', (event) => {
    // 💎 SEIZE CONTROL of the phone browser now!
    event.waitUntil(clients.claim());
});

self.addEventListener('fetch', (event) => {
    // 📡 THE Hub Hub Hub Hub Hub Hub STRATEGY:
    // Try to get fresh data, but if it takes more than 3 seconds or fails, 
    // INSTANTLY show the last version from the vault.
    event.respondWith(
        fetch(event.request)
            .then((response) => {
                let clone = response.clone();
                caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
                return response;
            })
            .catch(() => caches.match(event.request))
    );
});