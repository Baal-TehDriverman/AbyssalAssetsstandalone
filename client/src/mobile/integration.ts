// Mobile Integration Configuration for Abyssal Assets
// PWA + WebSocket mobile client for phone integration

export interface MobileConfig {
  // Server connection
  apiBaseUrl: string;
  wsBaseUrl: string;
  
  // Auth
  adminCredentials: {
    username: string;
    password: string;
    twoFactorEnabled: boolean;
  };
  
  // PWA settings
  pwa: {
    name: string;
    shortName: string;
    themeColor: string;
    backgroundColor: string;
    display: 'standalone' | 'fullscreen' | 'minimal-ui';
    orientation: 'portrait' | 'landscape';
    scope: string;
    startUrl: string;
  };
  
  // Push notifications
  push: {
    enabled: boolean;
    vapidPublicKey: string;
    topics: string[];
  };
  
  // Offline sync
  offline: {
    enabled: boolean;
    syncInterval: number; // minutes
    maxCacheSize: number; // MB
    criticalPaths: string[];
  };
  
  // Admin endpoints
  adminEndpoints: {
    dashboard: string;
    users: string;
    market: string;
    logs: string;
    commands: string;
  };
}

export const MOBILE_CONFIG: MobileConfig = {
  apiBaseUrl: 'https://api.abyssal-assets.com/api',
  wsBaseUrl: 'wss://api.abyssal-assets.com/ws',
  
  adminCredentials: {
    username: '', // Set via environment
    password: '', // Set via environment
    twoFactorEnabled: true,
  },
  
  pwa: {
    name: 'Abyssal Assets',
    shortName: 'Abyssal',
    themeColor: '#1a1a2e',
    backgroundColor: '#0a0a12',
    display: 'standalone',
    orientation: 'portrait',
    scope: '/',
    startUrl: '/mobile',
  },
  
  push: {
    enabled: true,
    vapidPublicKey: '', // Set via environment
    topics: ['market', 'dredge', 'clout', 'admin', 'world_event'],
  },
  
  offline: {
    enabled: true,
    syncInterval: 15,
    maxCacheSize: 100,
    criticalPaths: [
      '/api/auth/me',
      '/api/inventory',
      '/api/market',
      '/api/market/stats',
      '/api/leaderboard/clout',
      '/api/leaderboard/wealth',
    ],
  },
  
  adminEndpoints: {
    dashboard: '/api/admin/dashboard',
    users: '/api/admin/users',
    market: '/api/admin/market',
    logs: '/api/admin/logs',
    commands: '/api/admin/commands',
  },
};

// Service Worker Registration
export const registerSW = async (): Promise<ServiceWorkerRegistration | null> => {
  if ('serviceWorker' in navigator) {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/',
      });
      console.log('SW registered:', registration.scope);
      return registration;
    } catch (error) {
      console.error('SW registration failed:', error);
      return null;
    }
  }
  return null;
};

// Push Subscription
export const subscribePush = async (registration: ServiceWorkerRegistration): Promise<PushSubscription | null> => {
  try {
    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
  applicationServerKey: urlBase64ToUint8Array(MOBILE_CONFIG.push.vapidPublicKey) as unknown as BufferSource,
    });
    return subscription;
  } catch (error) {
    console.error('Push subscription failed:', error);
    return null;
  }
};

function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray as unknown as Uint8Array;
}

// Background Sync
export const registerBackgroundSync = async (registration: ServiceWorkerRegistration, tag: string): Promise<void> => {
  if ('sync' in registration) {
    try {
      await (registration as any).sync.register(tag);
      console.log('Background sync registered:', tag);
    } catch (error) {
      console.error('Background sync registration failed:', error);
    }
  }
};

// Network Status
export const setupNetworkMonitoring = (onOnline: () => void, onOffline: () => void): (() => void) => {
  const handleOnline = () => onOnline();
  const handleOffline = () => onOffline();
  
  window.addEventListener('online', handleOnline);
  window.addEventListener('offline', handleOffline);
  
  return () => {
    window.removeEventListener('online', handleOnline);
    window.removeEventListener('offline', handleOffline);
  };
};

// Admin Command Queue
export class AdminCommandQueue {
  private queue: Array<{ command: string; args: any[]; resolve: Function; reject: Function }> = [];
  private processing = false;
  
  async execute(command: string, ...args: any[]): Promise<any> {
    return new Promise((resolve, reject) => {
      this.queue.push({ command, args, resolve, reject });
      this.processQueue();
    });
  }
  
  private async processQueue(): Promise<void> {
    if (this.processing || this.queue.length === 0) return;
    this.processing = true;
    
    while (this.queue.length > 0) {
      const { command, args, resolve, reject } = this.queue.shift()!;
      try {
        const result = await this.sendCommand(command, args);
        resolve(result);
      } catch (error) {
        reject(error);
      }
      
      // Rate limiting
      await new Promise(r => setTimeout(r, 100));
    }
    
    this.processing = false;
  }
  
  private async sendCommand(command: string, args: any[]): Promise<any> {
    const response = await fetch(`${MOBILE_CONFIG.apiBaseUrl}${MOBILE_CONFIG.adminEndpoints.commands}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${await this.getAuthToken()}`,
      },
      body: JSON.stringify({ command, args }),
    });
    
    if (!response.ok) throw new Error(`Command failed: ${response.statusText}`);
    return response.json();
  }
  
  private async getAuthToken(): Promise<string> {
    return localStorage.getItem('admin_token') || '';
  }
}

export const adminQueue = new AdminCommandQueue();

// Mobile-specific UI adjustments
export const setupMobileUI = (): void => {
  // Prevent zoom on input focus (iOS)
  const style = document.createElement('style');
  style.textContent = `
    @media screen and (max-width: 768px) {
      input, select, textarea { font-size: 16px !important; }
    }
    /* Prevent pull-to-refresh on game canvas */
    canvas { touch-action: none; }
    /* Safe area insets for notched phones */
    .safe-area-top { padding-top: env(safe-area-inset-top); }
    .safe-area-bottom { padding-bottom: env(safe-area-inset-bottom); }
    .safe-area-left { padding-left: env(safe-area-inset-left); }
    .safe-area-right { padding-right: env(safe-area-inset-right); }
  `;
  document.head.appendChild(style);
  
  // Prevent overscroll bounce
  document.body.style.overscrollBehavior = 'none';
  
  // Fullscreen on orientation change
  window.addEventListener('orientationchange', () => {
    setTimeout(() => {
      window.scrollTo(0, 0);
    }, 100);
  });
};

// Touch gestures for game
export const setupTouchGestures = (canvas: HTMLCanvasElement): void => {
  let touchStart: { x: number; y: number } | null = null;
  
  canvas.addEventListener('touchstart', (e: TouchEvent) => {
    const touch = e.touches[0];
    touchStart = { x: touch.clientX, y: touch.clientY };
  }, { passive: true });
  
  canvas.addEventListener('touchmove', (e: TouchEvent) => {
    if (!touchStart) return;
    const touch = e.touches[0];
    const dx = touch.clientX - touchStart.x;
    const dy = touch.clientY - touchStart.y;
    
    // Emit movement event
    canvas.dispatchEvent(new CustomEvent('touchdrag', {
      detail: { dx, dy, x: touch.clientX, y: touch.clientY }
    }));
    
    touchStart = { x: touch.clientX, y: touch.clientY };
  }, { passive: true });
  
  canvas.addEventListener('touchend', () => {
    touchStart = null;
  });
};

// Battery status monitoring
export const setupBatteryMonitoring = (onLowBattery: (level: number) => void): void => {
  if ('getBattery' in navigator) {
    (navigator as any).getBattery().then((battery: any) => {
      const check = () => {
        if (battery.level < 0.2 && !battery.charging) {
          onLowBattery(battery.level);
        }
      };
      battery.addEventListener('levelchange', check);
      battery.addEventListener('chargingchange', check);
      check();
    });
  }
};

// Visibility change handler (pause/resume game)
export const setupVisibilityHandler = (onPause: () => void, onResume: () => void): (() => void) => {
  const handleVisibilityChange = () => {
    if (document.hidden) {
      onPause();
    } else {
      onResume();
    }
  };
  
  document.addEventListener('visibilitychange', handleVisibilityChange);
  return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
};

// Export all
export default {
  MOBILE_CONFIG,
  registerSW,
  subscribePush,
  registerBackgroundSync,
  setupNetworkMonitoring,
  AdminCommandQueue,
  adminQueue,
  setupMobileUI,
  setupTouchGestures,
  setupBatteryMonitoring,
  setupVisibilityHandler,
};