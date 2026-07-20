import 'phaser'
import { BootScene } from './scenes/BootScene'
import { PreloadScene } from './scenes/PreloadScene'
import { MainMenuScene } from './scenes/MainMenuScene'
import { GameScene } from './scenes/GameScene'
import { DredgeMiniGameScene } from './scenes/DredgeMiniGameScene'
import { MarketScene } from './scenes/MarketScene'
import { registerServiceWorker } from './sw-registration'

// Vite/ImportMeta type declaration
declare global {
  interface Window {
    game: Phaser.Game
    __ABYSSAL_DEBUG__: boolean
    __LILITH_SUDO_777__: boolean
    __SEPHIROTIC_RESONANCE__: string
  }
  interface ImportMeta {
    env: {
      readonly DEV: boolean
      readonly PROD: boolean
      readonly MODE: string
      readonly BASE_URL: string
      [key: string]: string | boolean | undefined
    }
  }
}

const config: Phaser.Types.Core.GameConfig = {
  type: Phaser.WEBGL,
  parent: 'game-container',
  width: window.innerWidth,
  height: window.innerHeight,
  scale: {
    mode: Phaser.Scale.RESIZE,
    autoCenter: Phaser.Scale.CENTER_BOTH,
    width: window.innerWidth,
    height: window.innerHeight,
  },
  physics: {
    default: 'arcade',
    arcade: {
      gravity: { x: 0, y: 0 },
      debug: import.meta.env.DEV,
    },
  },
  render: {
    antialias: false,
    pixelArt: true,
    roundPixels: true,
  },
  input: {
    gamepad: true,
    keyboard: true,
  },
  audio: {
    disableWebAudio: false,
  },
  scene: [
    BootScene,
    PreloadScene,
    MainMenuScene,
    GameScene,
    DredgeMiniGameScene,
    MarketScene,
  ],
  backgroundColor: '#0a0a12',
  dom: {
    createContainer: true,
  },
  callbacks: {
    postBoot: () => {
      document.getElementById('loading')?.classList.add('hidden')
      // Register Service Worker after game boots
      if (!import.meta.env.DEV || location.hostname === 'localhost' || location.hostname === '127.0.0.1') {
        registerServiceWorker()
      }
    },
  },
}

// LILITH SOVEREIGN CORE (SUDO 777)
window.__LILITH_SUDO_777__ = true;
window.__SEPHIROTIC_RESONANCE__ = "Δ∞ − 1 = 0";
console.log("%c[MSN-777] Frontend Sovereign Cyberpunk Client Booting...", "color: #ff003c; font-weight: bold; font-size: 14px;");
console.log(`%c[LILITH] SUDO ENABLED | Resonance: ${window.__SEPHIROTIC_RESONANCE__}`, "color: #00ffcc;");

class AbyssalAssetsGame extends Phaser.Game {
  constructor(config: Phaser.Types.Core.GameConfig) {
    super(config)
    this.events.on('resize', this.handleResize, this)
    window.addEventListener('resize', () => this.handleResize())
  }

  private handleResize(): void {
    const width = window.innerWidth
    const height = window.innerHeight
    this.scale.resize(width, height)
    this.scene.scenes.forEach((scene) => {
      if (scene.scene.isActive()) {
        scene.cameras.main.setViewport(0, 0, width, height)
      }
    })
  }
}

window.game = new AbyssalAssetsGame(config)
window.__ABYSSAL_DEBUG__ = import.meta.env.DEV