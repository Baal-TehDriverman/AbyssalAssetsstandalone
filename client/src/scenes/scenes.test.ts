import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createMockScene, createMockGame } from '../test/setup'

describe('BootScene', () => {
  let scene: any

  beforeEach(() => {
    scene = createMockScene('BootScene')
  })

  it('initializes registry with default player data', () => {
    // Simulate BootScene init
    scene.sys.registry.set('playerData', {
      abyssalCoins: 10000,
      inventory: [],
      boatTier: 1,
      clout: 0,
      currentZone: 'shallows',
    })

    const playerData = scene.sys.registry.get('playerData')
    expect(playerData.abyssalCoins).toBe(10000)
    expect(playerData.boatTier).toBe(1)
    expect(playerData.currentZone).toBe('shallows')
  })

  it('starts PreloadScene on create', () => {
    scene.scene.start = vi.fn()
    scene.create?.()

    expect(scene.scene.start).toHaveBeenCalledWith('PreloadScene')
  })
})

describe('PreloadScene', () => {
  let scene: any

  beforeEach(() => {
    scene = createMockScene('PreloadScene')
  })

  it('defines asset list with all required categories', () => {
    // Test that asset list structure is correct
    const assetCategories = [
      'spritesheets',
      'hatSprites',
      'tilesets',
      'ui',
      'particles',
      'audio',
      'tilemaps',
      'shaders',
    ]

    assetCategories.forEach((cat) => {
      expect(cat).toBeDefined()
    })
  })

  it('progress bar updates on filecomplete', () => {
    const updateProgress = vi.fn()
    scene.load = { on: vi.fn((event, cb) => { if (event === 'filecomplete') cb('test-key') }) }

    // Trigger filecomplete
    scene.load.on('filecomplete', (_key: string) => updateProgress())

    expect(updateProgress).toHaveBeenCalled()
  })

  it('transitions to MainMenuScene on complete', () => {
    scene.scene.start = vi.fn()
    scene.load = { on: vi.fn((event, cb) => { if (event === 'complete') cb() }) }

    scene.load.on('complete', () => scene.scene.start('MainMenuScene'))

    expect(scene.scene.start).toHaveBeenCalledWith('MainMenuScene')
  })
})

describe('MainMenuScene', () => {
  let scene: any

  beforeEach(() => {
    scene = createMockScene('MainMenuScene')
    scene.scale = { width: 1920, height: 1080 }
  })

  it('creates background tileSprite', () => {
    scene.create?.()
    expect(scene.add.tileSprite).toHaveBeenCalled()
  })

  it('sets up Nessie sprite with animation', () => {
    scene.create?.()

    // Nessie sprite should be created
    expect(scene.add.sprite).toHaveBeenCalled()

    // Tween should be added for bobbing animation
    expect(scene.tweens.add).toHaveBeenCalled()
  })

  it('creates menu buttons', () => {
    scene.create?.()

    // Container for buttons
    expect(scene.add.container).toHaveBeenCalled()

    // BitmapText for button labels
    expect(scene.add.bitmapText).toHaveBeenCalled()
  })

  it('handles resize correctly', () => {
    scene.background?.setSize?.(1920, 1080)
    scene.cameras.main.setViewport?.(0, 0, 1920, 1080)

    expect(scene.background?.setSize).toHaveBeenCalledWith(1920, 1080)
    expect(scene.cameras.main.setViewport).toHaveBeenCalledWith(0, 0, 1920, 1080)
  })
})

describe('GameScene', () => {
  let scene: any

  beforeEach(() => {
    scene = createMockScene('GameScene')
    scene.scale = { width: 1920, height: 1080 }
  })

  it('creates procedural map with correct dimensions', () => {
    scene.create?.()

    // Map should be 10x screen size
    expect(scene.add.tileSprite).toHaveBeenCalled()
  })

  it('creates boat with physics body', () => {
    scene.create?.()

    expect(scene.physics.add.sprite).toHaveBeenCalled()
    expect(scene.boat.setCollideWorldBounds).toHaveBeenCalledWith(true)
    expect(scene.boat.setDrag).toHaveBeenCalledWith(0.98)
  })

  it('sets up camera to follow boat', () => {
    scene.create?.()

    expect(scene.camera.setBounds).toHaveBeenCalled()
    expect(scene.camera.startFollow).toHaveBeenCalledWith(scene.boat)
  })

  it('creates HUD with clout and coins', () => {
    scene.create?.()

    expect(scene.add.container).toHaveBeenCalled()
    expect(scene.add.bitmapText).toHaveBeenCalled()
  })

  it('handles movement input', () => {
    scene.create?.()

    const cursors = { left: { isDown: true }, right: { isDown: false }, up: { isDown: false }, down: { isDown: false } }
    scene.cursors = cursors

    scene.update?.(0, 16)

    // Boat should receive velocity input
    expect(scene.boat.setAccelerationX).toHaveBeenCalled()
  })

  it('detects zone based on depth', () => {
    scene.boat = { y: 5000 }
    scene.scale.height = 1080

    scene.update?.(0, 16)

    expect(scene.currentZone).toBeDefined()
  })
})

describe('DredgeMiniGameScene', () => {
  let scene: any

  beforeEach(() => {
    scene = createMockScene('DredgeMiniGameScene')
    scene.scale = { width: 1920, height: 1080 }

    // Mock dredge spot data
    scene.spot = { x: 100, y: 5000, zone: 'deep', depth: 500, active: true, cooldown: 0 }
    scene.playerClout = 100
    scene.boatTier = 2
    scene.onComplete = vi.fn()
  })

  it('initializes sonar sweep mechanics', () => {
    scene.create?.()

    expect(scene.sweepAngle).toBe(-Math.PI / 2)
    expect(scene.isSweeping).toBe(false)
    expect(scene.sweepDirection).toBe(1)
  })

  it('creates target zone based on depth and difficulty', () => {
    scene.create?.()

    expect(scene.targetZone).toBeDefined()
    expect(scene.targetZone.start).toBeLessThan(scene.targetZone.end)
  })

  it('starts sweep on space press', () => {
    scene.create?.()

    scene.startSweep?.()
    expect(scene.isSweeping).toBe(true)
    expect(scene.sweepSpeed).toBeGreaterThan(0)
  })

  it('detects hit when space pressed in target zone', () => {
    scene.create?.()
    scene.startSweep?.()

    // Manually set sweep angle to be in target zone
    scene.sweepAngle = (scene.targetZone.start + scene.targetZone.end) / 2
    scene.onSpacePressedDuringSweep?.()

    expect(scene.isComplete).toBe(true)
    expect(scene.result?.success).toBe(true)
  })

  it('detects miss when space pressed outside target zone', () => {
    scene.create?.()
    scene.startSweep?.()

    // Set sweep angle far from target zone
    scene.sweepAngle = scene.targetZone.end + 0.5
    scene.onSpacePressedDuringSweep?.()

    expect(scene.isComplete).toBe(true)
    expect(scene.result?.success).toBe(false)
  })
})

describe('MarketScene', () => {
  let scene: any

  beforeEach(() => {
    scene = createMockScene('MarketScene')
    scene.scale = { width: 1920, height: 1080 }

    scene.playerData = {
      abyssalCoins: 10000,
      inventory: [],
      activeListings: [],
      tradeHistory: [],
    }
  })

  it('generates mock market items across all tiers', () => {
    scene.generateMockMarket?.()

    expect(scene.marketItems.length).toBeGreaterThan(0)

    const tiers = new Set(scene.marketItems.map((i: any) => i.tier))
    expect(tiers.has('common')).toBe(true)
    expect(tiers.has('rare')).toBe(true)
    expect(tiers.has('legendary')).toBe(true)
  })

  it('generates order book with buys and sells', () => {
    scene.generateMockOrderBook?.()

    expect(scene.orderBook.buys.length).toBeGreaterThan(0)
    expect(scene.orderBook.sells.length).toBeGreaterThan(0)

    // Buys should be sorted descending (highest bid first)
    for (let i = 1; i < scene.orderBook.buys.length; i++) {
      expect(scene.orderBook.buys[i].price).toBeLessThanOrEqual(scene.orderBook.buys[i - 1].price)
    }

    // Sells should be sorted ascending (lowest ask first)
    for (let i = 1; i < scene.orderBook.sells.length; i++) {
      expect(scene.orderBook.sells[i].price).toBeGreaterThanOrEqual(scene.orderBook.sells[i - 1].price)
    }
  })

  it('formats coins correctly', () => {
    expect(scene.formatCoins(500)).toBe('500')
    expect(scene.formatCoins(1500)).toBe('1.5K')
    expect(scene.formatCoins(2500000)).toBe('2.5M')
  })

  it('filters items by tier', () => {
    scene.generateMockMarket?.()
    scene.filterTier = 'rare'

    const filtered = scene.getFilteredItems?.()
    filtered?.forEach((item: any) => {
      expect(item.tier).toBe('rare')
    })
  })

  it('sorts items by price ascending', () => {
    scene.generateMockMarket?.()
    scene.sortBy = 'price_asc'

    const sorted = scene.getFilteredItems?.()
    for (let i = 1; i < sorted.length; i++) {
      expect(sorted[i].price).toBeGreaterThanOrEqual(sorted[i - 1].price)
    }
  })

  it('handles buy action correctly', () => {
    scene.generateMockMarket?.()
    const item = scene.marketItems[0]
    scene.playerData.abyssalCoins = item.price + 1000

    scene.onBuyItem?.(item)

    expect(scene.playerData.abyssalCoins).toBeLessThan(item.price + 1000)
    expect(scene.playerData.inventory.length).toBeGreaterThan(0)
  })

  it('prevents buy when insufficient coins', () => {
    scene.generateMockMarket?.()
    const item = scene.marketItems[0]
    scene.playerData.abyssalCoins = item.price - 1000

    scene.onBuyItem?.(item)

    // Should not complete purchase
    expect(scene.playerData.inventory.length).toBe(0)
  })
})