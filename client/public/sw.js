// Service Worker for Abyssal Assets PWA
// Handles caching, offline support, background sync, and push notifications

const CACHE_NAME = 'abyssal-assets-v1'
const STATIC_CACHE = 'abyssal-static-v1'
const DYNAMIC_CACHE = 'abyssal-dynamic-v1'
const API_CACHE = 'abyssal-api-v1'

// Assets to cache immediately on install
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.webmanifest',
  '/icon-192.svg',
  '/icon-512.svg',
  '/favicon.svg',
]

// Cache strategies
const CACHE_STRATEGIES = {
  // Cache first - for static assets
  cacheFirst: async (request: Request, cacheName: string) => {
    const cache = await caches.open(cacheName)
    const cached = await cache.match(request)
    if (cached) return cached

    try {
      const response = await fetch(request)
      if (response.ok) {
        cache.put(request, response.clone())
      }
      return response
    } catch {
      return new Response('Offline', { status: 503 })
    }
  },

  // Network first - for API calls
  networkFirst: async (request: Request, cacheName: string, timeout = 5000) => {
    const cache = await caches.open(cacheName)
    
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), timeout)
      
      const response = await fetch(request, { signal: controller.signal })
      clearTimeout(timeoutId)
      
      if (response.ok) {
        cache.put(request, response.clone())
      }
      return response
    } catch {
      const cached = await cache.match(request)
      if (cached) return cached
      return new Response(JSON.stringify({ error: 'Offline', offline: true }), {
        headers: { 'Content-Type': 'application/json' },
        status: 503,
      })
    }
  },

  // Stale while revalidate - for game assets
  staleWhileRevalidate: async (request: Request, cacheName: string) => {
    const cache = await caches.open(cacheName)
    const cached = await cache.match(request)

    const fetchPromise = fetch(request).then((response) => {
      if (response.ok) {
        cache.put(request, response.clone())
      }
      return response
    }).catch(() => cached)

    return cached || fetchPromise
  },
}

// Install - cache static assets
self.addEventListener('install', (event: ExtendableEvent) => {
  console.log('[SW] Installing...')
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      console.log('[SW] Caching static assets')
      return cache.addAll(STATIC_ASSETS)
    }).then(() => {
      console.log('[SW] Static assets cached')
      return self.skipWaiting()
    })
  )
})

// Activate - clean old caches
self.addEventListener('activate', (event: ExtendableEvent) => {
  console.log('[SW] Activating...')
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => ![STATIC_CACHE, DYNAMIC_CACHE, API_CACHE].includes(name))
          .map((name) => {
            console.log('[SW] Deleting old cache:', name)
            return caches.delete(name)
          })
      )
    }).then(() => {
      console.log('[SW] Activated')
      return self.clients.claim()
    })
  )
})

// Fetch - handle requests with appropriate strategy
self.addEventListener('fetch', (event: FetchEvent) => {
  const { request } = event
  const url = new URL(request.url)

  // Skip non-GET requests
  if (request.method !== 'GET') return

  // Skip chrome-extension, etc.
  if (!url.protocol.startsWith('http')) return

  // Determine cache strategy based on request
  if (isStaticAsset(url)) {
    event.respondWith(
      CACHE_STRATEGIES.cacheFirst(request, STATIC_CACHE)
    )
  } else if (isApiRequest(url)) {
    event.respondWith(
      CACHE_STRATEGIES.networkFirst(request, API_CACHE)
    )
  } else if (isGameAsset(url)) {
    event.respondWith(
      CACHE_STRATEGIES.staleWhileRevalidate(request, DYNAMIC_CACHE)
    )
  } else {
    // Default: network first with cache fallback
    event.respondWith(
      CACHE_STRATEGIES.networkFirst(request, DYNAMIC_CACHE)
    )
  }
})

function isStaticAsset(url: URL): boolean {
  return url.pathname === '/' ||
         url.pathname.endsWith('.html') ||
         url.pathname.endsWith('.js') ||
         url.pathname.endsWith('.css') ||
         url.pathname.endsWith('.svg') ||
         url.pathname.endsWith('.png') ||
         url.pathname.endsWith('.jpg') ||
         url.pathname.endsWith('.woff2') ||
         url.pathname === '/manifest.webmanifest'
}

function isApiRequest(url: URL): boolean {
  return url.pathname.startsWith('/api/') ||
         url.pathname.startsWith('/ws') ||
         url.hostname.includes('localhost:8000') ||
         url.hostname.includes('127.0.0.1:8000')
}

function isGameAsset(url: URL): boolean {
  return url.pathname.includes('/assets/') ||
         url.pathname.includes('/sprites/') ||
         url.pathname.includes('/audio/') ||
         url.pathname.includes('/tilesets/')
}

// Background Sync - handle offline actions
self.addEventListener('sync', (event: SyncEvent) => {
  console.log('[SW] Background sync:', event.tag)
  
  if (event.tag === 'sync-market-orders') {
    event.waitUntil(syncMarketOrders())
  } else if (event.tag === 'sync-dredge-results') {
    event.waitUntil(syncDredgeResults())
  } else if (event.tag === 'sync-inventory') {
    event.waitUntil(syncInventory())
  }
})

async function syncMarketOrders(): Promise<void> {
  try {
    const orders = await getStoredData('pending-market-orders')
    if (!orders?.length) return

    for (const order of orders) {
      try {
        const response = await fetch('/api/market/orders', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(order),
        })
        if (response.ok) {
          await removeStoredData('pending-market-orders', order.id)
        }
      } catch (error) {
        console.error('[SW] Failed to sync order:', order.id, error)
      }
    }
  } catch (error) {
    console.error('[SW] syncMarketOrders failed:', error)
  }
}

async function syncDredgeResults(): Promise<void> {
  try {
    const results = await getStoredData('pending-dredge-results')
    if (!results?.length) return

    for (const result of results) {
      try {
        const response = await fetch('/api/dredge/results', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(result),
        })
        if (response.ok) {
          await removeStoredData('pending-dredge-results', result.id)
        }
      } catch (error) {
        console.error('[SW] Failed to sync dredge result:', result.id, error)
      }
    }
  } catch (error) {
    console.error('[SW] syncDredgeResults failed:', error)
  }
}

async function syncInventory(): Promise<void> {
  try {
    const items = await getStoredData('pending-inventory-changes')
    if (!items?.length) return

    for (const item of items) {
      try {
        const response = await fetch('/api/inventory/sync', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(item),
        })
        if (response.ok) {
          await removeStoredData('pending-inventory-changes', item.id)
        }
      } catch (error) {
        console.error('[SW] Failed to sync inventory:', item.id, error)
      }
    }
  } catch (error) {
    console.error('[SW] syncInventory failed:', error)
  }
}

// Periodic Background Sync
self.addEventListener('periodicsync', (event: ExtendableEvent & { tag: string }) => {
  console.log('[SW] Periodic sync:', event.tag)
  
  if (event.tag === 'market-data-refresh') {
    event.waitUntil(refreshMarketData())
  }
})

async function refreshMarketData(): Promise<void> {
  try {
    const response = await fetch('/api/market/snapshot', {
      headers: { 'Accept': 'application/json' },
    })
    
    if (response.ok) {
      const data = await response.json()
      // Broadcast to all clients
      const clients = await self.clients.matchAll()
      clients.forEach((client) => {
        client.postMessage({
          type: 'MARKET_DATA_UPDATE',
          data,
        })
      })
      console.log('[SW] Market data refreshed')
    }
  } catch (error) {
    console.error('[SW] Market data refresh failed:', error)
  }
}

// Push Notifications
self.addEventListener('push', (event: PushEvent) => {
  console.log('[SW] Push received:', event.data?.text())
  
  const data = event.data?.json() || { 
    title: 'Abyssal Assets',
    body: 'Something happened in the depths...',
    icon: '/icon-192.svg',
    badge: '/icon-192.svg',
    tag: 'abyssal-notification',
    data: {},
    actions: [
      { action: 'open', title: 'Open' },
      { action: 'dismiss', title: 'Dismiss' },
    ],
  }

  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: data.icon,
      badge: data.badge,
      tag: data.tag,
      data: data.data,
      actions: data.actions,
      requireInteraction: data.requireInteraction || false,
      vibrate: [100, 50, 100],
      timestamp: Date.now(),
    })
  )
})

self.addEventListener('notificationclick', (event: NotificationEvent) => {
  event.notification.close()

  if (event.action === 'dismiss') return

  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      // Try to focus existing window
      for (const client of clientList) {
        if (client.url.includes(self.location.origin) && 'focus' in client) {
          return client.focus()
        }
      }
      // Open new window
      if (self.clients.openWindow) {
        return self.clients.openWindow(event.notification.data?.url || '/')
      }
    })
  )
})

self.addEventListener('notificationclose', (event: NotificationEvent) => {
  console.log('[SW] Notification closed:', event.notification.tag)
})

// Message handling from clients
self.addEventListener('message', (event: ExtendableMessageEvent) => {
  const { type, data } = event.data || {}

  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting()
      break

    case 'STORE_MARKET_ORDER':
      storeData('pending-market-orders', data)
      break

    case 'STORE_DREDGE_RESULT':
      storeData('pending-dredge-results', data)
      break

    case 'STORE_INVENTORY_CHANGE':
      storeData('pending-inventory-changes', data)
      break

    case 'GET_CACHED_DATA':
      getCachedData(data.key).then((result) => {
        event.ports[0]?.postMessage({ type: 'CACHED_DATA', key: data.key, data: result })
      })
      break

    case 'CLEAR_CACHE':
      clearCache(data.cacheName)
      break

    default:
      console.log('[SW] Unknown message:', type)
  }
})

// IndexedDB helpers for offline storage
const DB_NAME = 'abyssal-offline'
const DB_VERSION = 1

function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION)
    
    request.onupgradeneeded = () => {
      const db = request.result
      if (!db.objectStoreNames.contains('offline-data')) {
        db.createObjectStore('offline-data', { keyPath: 'id', autoIncrement: true })
      }
    }
    
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

async function storeData(storeName: string, data: any): Promise<void> {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction('offline-data', 'readwrite')
    const store = tx.objectStore('offline-data')
    store.add({ storeName, data, timestamp: Date.now() })
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
}

async function getStoredData(storeName: string): Promise<any[]> {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction('offline-data', 'readonly')
    const store = tx.objectStore('offline-data')
    const request = store.getAll()
    request.onsuccess = () => {
      const results = request.result.filter((item) => item.storeName === storeName)
      resolve(results.map((r) => ({ ...r.data, __id: r.id })))
    }
    request.onerror = () => reject(request.error)
  })
}

async function removeStoredData(storeName: string, id: number): Promise<void> {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction('offline-data', 'readwrite')
    const store = tx.objectStore('offline-data')
    // Need to find by storeName first, then delete by id
    const indexRequest = store.getAll()
    indexRequest.onsuccess = () => {
      const items = indexRequest.result.filter((item) => item.storeName === storeName)
      const target = items.find((item) => item.data.id === id || item.id === id)
      if (target) {
        store.delete(target.id)
      }
      resolve()
    }
    indexRequest.onerror = () => reject(indexRequest.error)
  })
}

async function getCachedData(key: string): Promise<any> {
  const cache = await caches.open(DYNAMIC_CACHE)
  const response = await cache.match(key)
  return response?.json()
}

async function clearCache(cacheName?: string): Promise<void> {
  if (cacheName) {
    await caches.delete(cacheName)
  } else {
    const names = await caches.keys()
    await Promise.all(names.map((name) => caches.delete(name)))
  }
}

console.log('[SW] Abyssal Assets Service Worker loaded')