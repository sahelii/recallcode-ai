// Service Worker for RecallCode AI PWA
const CACHE_NAME = "recallcode-v1";
const urlsToCache = [
  "/",
  "/dashboard",
  "/problems",
  "/reviews",
  "/auth/login",
  "/auth/register",
];

// Install event - cache resources
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(urlsToCache);
    })
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener("fetch", (event) => {
  // Skip service worker for API calls and external resources
  if (event.request.url.includes('/api/') || 
      event.request.url.startsWith('chrome-extension://') ||
      !event.request.url.startsWith(self.location.origin)) {
    return;
  }
  
  event.respondWith(
    caches.match(event.request).then((response) => {
      // Return cached version or fetch from network
      return response || fetch(event.request).catch(() => {
        // Return offline page or fallback if fetch fails
        return new Response('Offline', { status: 503 });
      });
    })
  );
});

// Activate event - clean up old caches
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((cacheName) => cacheName !== CACHE_NAME)
          .map((cacheName) => caches.delete(cacheName))
      );
    })
  );
});

