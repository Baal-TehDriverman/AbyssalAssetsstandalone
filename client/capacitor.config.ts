import { CapacitorConfig } from '@capacitor/cli'

const config: CapacitorConfig = {
  appId: 'com.lilithsystems.abyssalassets',
  appName: 'Abyssal Assets',
  webDir: 'dist',
  bundledWebRuntime: false,
  server: {
    // Live-reload: point to your PC's LAN IP for development
    url: 'http://192.168.1.153:5173',
    cleartext: true,
    androidScheme: 'http',
  },
  android: {
    allowMixedContent: true,
    captureInput: true,
    webContentsDebuggingEnabled: true,
    backgroundColor: '#0a0a12',
    overrideUserAgent: 'AbyssalAssets/1.0 (Android; Mobile) Phaser/3.80',
    buildOptions: {
      keystorePath: undefined,
      keystorePassword: undefined,
      keystoreAlias: undefined,
      keystoreAliasPassword: undefined,
    },
  },
  ios: {
    contentInset: 'automatic',
    scrollEnabled: true,
    allowsLinkPreview: false,
    preferredContentMode: 'mobile',
    backgroundColor: '#0a0a12',
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      launchAutoHide: true,
      backgroundColor: '#0a0a12',
      androidSplashResourceName: 'splash',
      androidScaleType: 'CENTER_CROP',
      showSpinner: false,
    },
    StatusBar: {
      style: 'dark',
      backgroundColor: '#0a0a12',
      overlaysWebView: true,
    },
    Keyboard: {
      resize: 'body',
      style: 'dark',
      resizeOnFullScreen: true,
    },
    PushNotifications: {
      presentationOptions: ['badge', 'sound', 'alert'],
    },
    LocalNotifications: {
      smallIcon: 'ic_stat_abyssal',
      iconColor: '#f43f5e',
      sound: 'notification.mp3',
    },
    BackgroundTask: {
      taskName: 'com.lilithsystems.abyssalassets.background',
      interval: 15,
    },
    CapacitorHttp: {
      enabled: true,
    },
    Camera: {
      iosRequireFullScreen: false,
    },
    FilePicker: {
      types: ['application/json'],
    },
    Haptics: {},
    Device: {},
    App: {
      launchAutoHide: true,
    },
    Network: {},
    Browser: {
      presentationStyle: 'fullscreen',
    },
    Share: {},
    Clipboard: {},
    Storage: {
      iosDatabaseLocation: 'Library/Application Support',
    },
  },
}

export default config