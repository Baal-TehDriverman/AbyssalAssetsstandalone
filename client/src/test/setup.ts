// @ts-nocheck
// Vitest global setup for Abyssal Assets tests
import { beforeAll, afterAll, vi } from 'vitest'

// Mock Phaser globally for unit tests
beforeAll(() => {
  // Phaser.Game mock
  global.Phaser = {
    Game: vi.fn().mockImplementation(() => ({
      scene: { scenes: [] },
      scale: { resize: vi.fn() },
      events: { on: vi.fn(), off: vi.fn(), emit: vi.fn() },
      physics: { add: {} },
      cameras: { main: { setBounds: vi.fn(), setViewport: vi.fn(), fadeOut: vi.fn() } },
      time: { addEvent: vi.fn(() => ({ remove: vi.fn() })), removeEvent: vi.fn() },
      tweens: { add: vi.fn() },
      add: {
        graphics: vi.fn(() => ({
          fillStyle: vi.fn().mockReturnThis(),
          fillRect: vi.fn().mockReturnThis(),
          fillRoundedRect: vi.fn().mockReturnThis(),
          clear: vi.fn().mockReturnThis(),
          lineStyle: vi.fn().mockReturnThis(),
          strokeRoundedRect: vi.fn().mockReturnThis(),
          setDepth: vi.fn().mockReturnThis(),
          setScrollFactor: vi.fn().mockReturnThis(),
          setOrigin: vi.fn().mockReturnThis(),
        })),
        sprite: vi.fn(() => ({
          setScale: vi.fn().mockReturnThis(),
          setAlpha: vi.fn().mockReturnThis(),
          setDepth: vi.fn().mockReturnThis(),
          setBlendMode: vi.fn().mockReturnThis(),
          setPosition: vi.fn().mockReturnThis(),
          play: vi.fn().mockReturnThis(),
          setVisible: vi.fn().mockReturnThis(),
          setOrigin: vi.fn().mockReturnThis(),
        })),
        tileSprite: vi.fn(() => ({
          setOrigin: vi.fn().mockReturnThis(),
          setScrollFactor: vi.fn().mockReturnThis(),
          setAlpha: vi.fn().mockReturnThis(),
          setBlendMode: vi.fn().mockReturnThis(),
        })),
        rectangle: vi.fn(() => ({
          setOrigin: vi.fn().mockReturnThis(),
          setAlpha: vi.fn().mockReturnThis(),
          setSize: vi.fn().mockReturnThis(),
        })),
        container: vi.fn(() => ({
          setDepth: vi.fn().mockReturnThis(),
          setScrollFactor: vi.fn().mockReturnThis(),
          setVisible: vi.fn().mockReturnThis(),
          setPosition: vi.fn().mockReturnThis(),
          add: vi.fn().mockReturnThis(),
          removeAll: vi.fn().mockReturnThis(),
          setScale: vi.fn().mockReturnThis(),
        })),
        bitmapText: vi.fn(() => ({
          setOrigin: vi.fn().mockReturnThis(),
          setTint: vi.fn().mockReturnThis(),
          setDepth: vi.fn().mockReturnThis(),
          setScrollFactor: vi.fn().mockReturnThis(),
          setText: vi.fn().mockReturnThis(),
          setCenterAlign: vi.fn().mockReturnThis(),
          setPosition: vi.fn().mockReturnThis(),
        })),
        particles: vi.fn(() => ({})),
        graphics: vi.fn(() => ({
          fillStyle: vi.fn().mockReturnThis(),
          fillRoundedRect: vi.fn().mockReturnThis(),
          lineStyle: vi.fn().mockReturnThis(),
          strokeRoundedRect: vi.fn().mockReturnThis(),
          clear: vi.fn().mockReturnThis(),
          setDepth: vi.fn().mockReturnThis(),
          setScrollFactor: vi.fn().mockReturnThis(),
        })),
      },
      physics: {
        add: {
          sprite: vi.fn(() => ({
            setScale: vi.fn().mockReturnThis(),
            setCollideWorldBounds: vi.fn().mockReturnThis(),
            setDamping: vi.fn().mockReturnThis(),
            setDrag: vi.fn().mockReturnThis(),
            setMaxVelocity: vi.fn().mockReturnThis(),
            setDepth: vi.fn().mockReturnThis(),
            setVisible: vi.fn().mockReturnThis(),
            setPosition: vi.fn().mockReturnThis(),
          })),
          collider: vi.fn(),
        },
      },
      anims: {
        create: vi.fn(),
        generateFrameNumbers: vi.fn(() => []),
      },
      input: {
        on: vi.fn(),
        keyboard: {
          on: vi.fn(),
          createCursorKeys: vi.fn(() => ({
            left: { isDown: false, isUp: true },
            right: { isDown: false, isUp: true },
            up: { isDown: false, isUp: true },
            down: { isDown: false, isUp: true },
            space: { isDown: false, isUp: true },
          })),
          addKey: vi.fn(() => ({ isDown: false, isUp: true })),
        },
      },
      sound: {
        add: vi.fn(() => ({
          play: vi.fn().mockReturnThis(),
          stop: vi.fn().mockReturnThis(),
          setVolume: vi.fn().mockReturnThis(),
          setLoop: vi.fn().mockReturnThis(),
        })),
      },
      scale: {
        width: 1920,
        height: 1080,
        on: vi.fn(),
        off: vi.fn(),
      },
      events: { on: vi.fn() },
      registry: { set: vi.fn(), get: vi.fn() },
      scene: {
        isActive: vi.fn(() => true),
        start: vi.fn(),
        stop: vi.fn(),
      },
    })),
    Scene: class MockScene {
      constructor(config?: { key?: string }) {
        this.sys = {
          config: config || { key: 'MockScene' },
          game: global.Phaser.Game(),
          canvas: document.createElement('canvas'),
          textures: { get: vi.fn(() => ({ getSourceImage: vi.fn() })) },
        }
        this.add = global.Phaser.Game().add
        this.physics = global.Phaser.Game().physics
        this.anims = global.Phaser.Game().anims
        this.input = global.Phaser.Game().input
        this.sound = global.Phaser.Game().sound
        this.scale = global.Phaser.Game().scale
        this.cameras = global.Phaser.Game().cameras
        this.time = global.Phaser.Game().time
        this.tweens = global.Phaser.Game().tweens
        this.events = { on: vi.fn(), off: vi.fn(), emit: vi.fn() }
        this.registry = global.Phaser.Game().registry
        this.children = { add: vi.fn(), remove: vi.fn() }
        this.make = { graphics: vi.fn(() => global.Phaser.Game().add.graphics()) }
      }
      sys: any
      add: any
      physics: any
      anims: any
      input: any
      sound: any
      scale: any
      cameras: any
      time: any
      tweens: any
      events: any
      registry: any
      children: any
      make: any
    },
    WEBGL: 1,
    CANVAS: 0,
    Scale: { RESIZE: 2, CENTER_BOTH: 1 },
    BlendModes: { NORMAL: 0, ADD: 1, SCREEN: 2, MULTIPLY: 3 },
    Math: {
      Clamp: (value: number, min: number, max: number) => Math.max(min, Math.min(max, value)),
      Between: (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min,
      FloatBetween: (min: number, max: number) => Math.random() * (max - min) + min,
    },
    GameObjects: {
      Graphics: class {},
      Container: class {},
      BitmapText: class {},
      Sprite: class {},
      Rectangle: class {},
      TileSprite: class {},
      Particles: {
        ParticleEmitter: class {},
      },
    },
    Physics: { Arcade: { Sprite: class {} } },
    Tilemaps: { Tilemap: class {}, TilemapLayer: class {} },
    Cameras: { Scene2D: { Camera: class {} } },
    Sound: { BaseSound: class {} },
    Structs: { Size: class {} },
    Input: { Keyboard: { CursorKeys: {} } },
    Time: { TimerEvent: class {} },
    Tweens: { Tween: class {} },
    Types: { Core: { GameConfig: {} } },
  }

  // Mock window/game globals
  global.window = {
    ...global.window,
    innerWidth: 1920,
    innerHeight: 1080,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    document: {
      ...global.document,
      readyState: 'complete',
      getElementById: vi.fn(() => ({ classList: { add: vi.fn() } })),
      createElement: vi.fn(() => ({
        style: {},
        getContext: vi.fn(),
        width: 1920,
        height: 1080,
      })),
    },
  } as any

  global.HTMLCanvasElement = vi.fn().mockImplementation(() => ({
    width: 1920,
    height: 1080,
    getContext: vi.fn(() => ({
      fillRect: vi.fn(),
      clearRect: vi.fn(),
      drawImage: vi.fn(),
    })),
  })) as any

  // Performance.now mock
  global.performance = {
    now: vi.fn(() => Date.now()),
  } as any
})

afterAll(() => {
  vi.restoreAllMocks()
})

// Test utilities
export const createMockScene = (key = 'TestScene') => {
  return new global.Phaser.Scene({ key })
}

export const createMockGame = () => {
  return new global.Phaser.Game({} as any)
}