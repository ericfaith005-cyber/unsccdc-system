// 🛡️ UNSCCDC INDESTRUCTIBLE GUARD v2.0
const CACHE_NAME = 'unsccdc-sovereign-vault';
const Hub_FILES = [
    '/',
    '/api/home/',
    '/static/css/unsccdc_prestige.css',
    '/static/icons/hub_logo.png',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css'
];

// 1. 📥 FORCED INSTALLATION
self.addEventListener('install', (event) => {
    self.skipWaiting(); // 💎 Force activation immediately!
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log("Registry Files Locked in Vault 🗿");
            return cache.addAll(Hub_FILES);
        })
    );
});

// 2. ⚡ ACTIVATION: Claim the phone's browser
self.addEventListener('activate', (event) => {
    event.waitUntil(clients.claim()); 
});

// 3. 📡 THE Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub Hub STRATEGY
// "Cache First, Fallback to Network"
// This ensures the system opens INSTANTLY even if the signal is 0%
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            // Return cached file OR try to get fresh one if online
            return response || fetch(event.request);
        })
    );
});