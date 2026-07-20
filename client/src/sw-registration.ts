// Service Worker Registration for Abyssal Assets PWA

export async function registerServiceWorker(): Promise<ServiceWorkerRegistration | null> {
  if (!('serviceWorker' in navigator)) {
    console.log('[SW] Service Worker not supported')
    return null
  }

  // Only register on HTTPS or localhost
  const isSecure = location.protocol === 'https:' || 
                   location.hostname === 'localhost' || 
                   location.hostname === '127.0.0.1' ||
                   location.hostname === '0.0.0.0'

  if (!isSecure) {
    console.log('[SW] Skipping registration - not secure context')
    return null
  }

  try {
    const registration = await navigator.serviceWorker.register('/sw.js', {
      scope: '/',
    })

    console.log('[SW] Registered:', registration.scope)

    // Handle updates
    registration.addEventListener('updatefound', () => {
      const newWorker = registration.installing
      if (newWorker) {
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            // New version available
            console.log('[SW] New version available!')
            showUpdateAvailable()
          }
        })
      }
    })

    // Check for updates periodically
    setInterval(() => {
      registration.update().catch(console.error)
    }, 60 * 60 * 1000) // Every hour

    // Listen for messages from SW
    navigator.serviceWorker.addEventListener('message', (event) => {
      handleSWMessage(event.data)
    })

    return registration
  } catch (error) {
    console.error('[SW] Registration failed:', error)
    return null
  }
}

function showUpdateAvailable(): void {
  // Dispatch custom event for UI to handle
  window.dispatchEvent(new CustomEvent('sw-update-available'))
}

function handleSWMessage(data: any): void {
  if (!data?.type) return

  switch (data.type) {
    case 'MARKET_DATA_UPDATE':
      window.dispatchEvent(new CustomEvent('market-data-update', { detail: data.data }))
      break
    case 'SYNC_MARKET_ORDERS':
      window.dispatchEvent(new CustomEvent('sync-market-orders'))
      break
    case 'SYNC_DREDGE_RESULTS':
      window.dispatchEvent(new CustomEvent('sync-dredge-results'))
      break
    default:
      console.log('[SW] Unknown message:', data)
  }
}

// Request notification permission
export async function requestNotificationPermission(): Promise<NotificationPermission> {
  if (!('Notification' in window)) {
    console.log('[SW] Notifications not supported')
    return 'denied'
  }

  if (Notification.permission === 'granted') {
    return 'granted'
  }

  if (Notification.permission === 'denied') {
    return 'denied'
  }

  const permission = await Notification.requestPermission()
  console.log('[SW] Notification permission:', permission)
  return permission
}

// Subscribe to push notifications
export async function subscribeToPush(registration: ServiceWorkerRegistration): Promise<PushSubscription | null> {
  try {
    const vapidKey = import.meta.env.VITE_VAPID_PUBLIC_KEY as string | undefined
    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: vapidKey ? urlBase64ToUint8Array(vapidKey) as BufferSource : undefined,
    })
    console.log('[SW] Push subscription:', subscription)
    return subscription
  } catch (error) {
    console.error('[SW] Push subscription failed:', error)
    return null
  }
}

// Convert VAPID key
function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = window.atob(base64)
  const outputArray = new Uint8Array(rawData.length)
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i)
  }
  return outputArray
}

// Check for periodic background sync support
export function supportsPeriodicSync(): boolean {
  return 'serviceWorker' in navigator && 'periodicSync' in (navigator.serviceWorker as any)
}

// Register periodic sync for market data
export async function registerPeriodicSync(registration: ServiceWorkerRegistration): Promise<void> {
  if (!supportsPeriodicSync()) return

  try {
    // @ts-expect-error - periodicSync not in TypeScript lib
    await registration.periodicSync.register('market-data-refresh', {
      minInterval: 15 * 60 * 1000, // 15 minutes
    })
    console.log('[SW] Periodic sync registered')
  } catch (error) {
    console.error('[SW] Periodic sync registration failed:', error)
  }
}

// Trigger background sync for offline actions
export async function triggerBackgroundSync(tag: string): Promise<void> {
  const registration = await navigator.serviceWorker.ready
  try {
    await (registration as any).sync.register(tag)
    console.log('[SW] Background sync triggered:', tag)
  } catch (error) {
    console.error('[SW] Background sync failed:', error)
  }
}

export default { registerServiceWorker, requestNotificationPermission, subscribeToPush, triggerBackgroundSync }