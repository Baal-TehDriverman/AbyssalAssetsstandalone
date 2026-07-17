import { Scene } from 'phaser'

interface AssetEntry {
  key: string
  url: string
  type: 'image' | 'spritesheet' | 'tilemap' | 'tilemapTiledJSON' | 'audio' | 'text'
  frameConfig?: { frameWidth: number; frameHeight: number }
  tileWidth?: number
  tileHeight?: number
}

export class PreloadScene extends Scene {
  private progressBar!: Phaser.GameObjects.Graphics
  private progressBox!: Phaser.GameObjects.Graphics
  private loadingText!: Phaser.GameObjects.BitmapText
  private percentText!: Phaser.GameObjects.BitmapText
  private assetList: AssetEntry[] = []

  constructor() {
    super({ key: 'PreloadScene' })
  }

  init(): void {
    this.setupProgressUI()
    this.defineAssets()
  }

  private setupProgressUI(): void {
    const { width, height } = this.scale
    
    // Background
    this.add.rectangle(0, 0, width, height, 0x0a0a12).setOrigin(0)
    
    // Progress box
    this.progressBox = this.add.graphics()
    this.progressBox.fillStyle(0x1a1a2e, 1)
    this.progressBox.fillRoundedRect(width / 2 - 160, height / 2 - 20, 320, 40, 8)
    this.progressBox.lineStyle(2, 0x333333, 1)
    this.progressBox.strokeRoundedRect(width / 2 - 160, height / 2 - 20, 320, 40, 8)
    
    // Progress bar
    this.progressBar = this.add.graphics()
    
    // Loading text
    this.loadingText = this.add.bitmapText(
      width / 2,
      height / 2 - 70,
      'press-start',
      'LOADING LOCH...',
      24
    ).setOrigin(0.5).setTint(0xffd700)
    
    // Percent text
    this.percentText = this.add.bitmapText(
      width / 2,
      height / 2 + 40,
      'press-start-small',
      '0%',
      16
    ).setOrigin(0.5).setTint(0xe8d5c4)
    
    // Subtitle
    this.add.bitmapText(
      width / 2,
      height / 2 + 80,
      'press-start-small',
      'THE EXCHANGE AWAKENS',
      12
    ).setOrigin(0.5).setTint(0x666666)
  }

  private defineAssets(): void {
    // === SPRITESHEETS ===
    this.assetList.push(
      { key: 'player', url: 'sprites/player.png', type: 'spritesheet', frameConfig: { frameWidth: 64, frameHeight: 64 } },
      { key: 'boat-basic', url: 'sprites/boats/basic.png', type: 'spritesheet', frameConfig: { frameWidth: 128, frameHeight: 64 } },
      { key: 'boat-upgraded', url: 'sprites/boats/upgraded.png', type: 'spritesheet', frameConfig: { frameWidth: 128, frameHeight: 64 } },
      { key: 'nessie', url: 'sprites/nessie.png', type: 'spritesheet', frameConfig: { frameWidth: 512, frameHeight: 256 } },
    )

    // === HAT SPRITES (by tier) ===
    const hatTiers = [
      { tier: 'noob', items: ['soggy-visor', 'plastic-horns', 'wet-cardboard'] },
      { tier: 'common', items: ['wool-beanie', 'fisherman-cap', 'kelp-crown'] },
      { tier: 'uncommon', items: ['kelp-top-hat', 'sub-captain-cap', 'coral-tiara'] },
      { tier: 'rare', items: ['admiral-bicorn', 'pearl-fedora', 'seaweed-sombrero'] },
      { tier: 'epic', items: ['plundered-captain-cap', 'kraken-ink-stetson', 'abyssal-crown'] },
      { tier: 'legendary', items: ['surgeons-photograph', 'neptunes-trident-helm'] },
      { tier: 'mythic', items: ['nessies-crown', 'original-monster-hat'] },
    ]

    hatTiers.forEach(({ tier, items }) => {
      items.forEach(item => {
        this.assetList.push({
          key: `hat-${item}`,
          url: `sprites/hats/${tier}/${item}.png`,
          type: 'image',
        })
      })
    })

    // === TILESETS ===
    this.assetList.push(
      { key: 'tiles-shallows', url: 'tilesets/shallows.png', type: 'tilemap', tileWidth: 32, tileHeight: 32 },
      { key: 'tiles-standard', url: 'tilesets/standard.png', type: 'tilemap', tileWidth: 32, tileHeight: 32 },
      { key: 'tiles-deep', url: 'tilesets/deep.png', type: 'tilemap', tileWidth: 32, tileHeight: 32 },
      { key: 'tiles-abyssal', url: 'tilesets/abyssal.png', type: 'tilemap', tileWidth: 32, tileHeight: 32 },
      { key: 'tiles-trench', url: 'tilesets/trench.png', type: 'tilemap', tileWidth: 32, tileHeight: 32 },
    )

    // === UI ===
    this.assetList.push(
      { key: 'ui-panel', url: 'ui/panel.png', type: 'image' },
      { key: 'ui-button', url: 'ui/button.png', type: 'image' },
      { key: 'ui-slot', url: 'ui/slot.png', type: 'image' },
      { key: 'ui-rarity-glow', url: 'ui/rarity_glow.png', type: 'image' },
      { key: 'cursor', url: 'ui/cursor.png', type: 'image' },
    )

    // === PARTICLES ===
    this.assetList.push(
      { key: 'particle-bubble', url: 'particles/bubble.png', type: 'image' },
      { key: 'particle-sparkle', url: 'particles/sparkle.png', type: 'image' },
      { key: 'particle-mist', url: 'particles/mist.png', type: 'image' },
      { key: 'particle-rarity-common', url: 'particles/rarity_white.png', type: 'image' },
      { key: 'particle-rarity-uncommon', url: 'particles/rarity_green.png', type: 'image' },
      { key: 'particle-rarity-rare', url: 'particles/rarity_blue.png', type: 'image' },
      { key: 'particle-rarity-epic', url: 'particles/rarity_purple.png', type: 'image' },
      { key: 'particle-rarity-legendary', url: 'particles/rarity_gold.png', type: 'image' },
      { key: 'particle-rarity-mythic', url: 'particles/rarity_cosmic.png', type: 'image' },
    )

    // === AUDIO ===
    this.assetList.push(
      { key: 'sfx-dredge-start', url: 'audio/sfx/dredge_start.ogg', type: 'audio' },
      { key: 'sfx-dredge-pull', url: 'audio/sfx/dredge_pull.ogg', type: 'audio' },
      { key: 'sfx-dredge-success', url: 'audio/sfx/dredge_success.ogg', type: 'audio' },
      { key: 'sfx-dredge-fail', url: 'audio/sfx/dredge_fail.ogg', type: 'audio' },
      { key: 'sfx-craft', url: 'audio/sfx/craft.ogg', type: 'audio' },
      { key: 'sfx-craft-success', url: 'audio/sfx/craft_success.ogg', type: 'audio' },
      { key: 'sfx-trade', url: 'audio/sfx/trade.ogg', type: 'audio' },
      { key: 'sfx-market-buy', url: 'audio/sfx/market_buy.ogg', type: 'audio' },
      { key: 'sfx-market-sell', url: 'audio/sfx/market_sell.ogg', type: 'audio' },
      { key: 'sfx-clout-gain', url: 'audio/sfx/clout_gain.ogg', type: 'audio' },
      { key: 'sfx-nessie-roar', url: 'audio/sfx/nessie_roar.ogg', type: 'audio' },
      { key: 'sfx-water-ambient', url: 'audio/ambient/water.ogg', type: 'audio' },
      { key: 'music-shallows', url: 'audio/music/shallows.ogg', type: 'audio' },
      { key: 'music-deep', url: 'audio/music/deep.ogg', type: 'audio' },
      { key: 'music-trench', url: 'audio/music/trench.ogg', type: 'audio' },
      { key: 'music-abyssal', url: 'audio/music/abyssal.ogg', type: 'audio' },
    )

    // === TILEMAPS ===
    this.assetList.push(
      { key: 'map-shallows', url: 'maps/shallows.json', type: 'tilemapTiledJSON' },
      { key: 'map-standard', url: 'maps/standard.json', type: 'tilemapTiledJSON' },
      { key: 'map-deep', url: 'maps/deep.json', type: 'tilemapTiledJSON' },
      { key: 'map-trench', url: 'maps/trench.json', type: 'tilemapTiledJSON' },
      { key: 'map-abyssal', url: 'maps/abyssal.json', type: 'tilemapTiledJSON' },
    )

    // === SHADERS ===
    this.assetList.push(
      { key: 'shader-water', url: 'shaders/water.glsl', type: 'text' },
      { key: 'shader-rarity-glow', url: 'shaders/rarity_glow.glsl', type: 'text' },
      { key: 'shader-caustics', url: 'shaders/caustics.glsl', type: 'text' },
      { key: 'shader-mythic-distort', url: 'shaders/mythic_distort.glsl', type: 'text' },
    )
  }

  preload(): void {
    let loaded = 0
    const total = this.assetList.length

    this.assetList.forEach(asset => {
      try {
        switch (asset.type) {
          case 'image':
            this.load.image(asset.key, asset.url)
            break
          case 'spritesheet':
            this.load.spritesheet(asset.key, asset.url, asset.frameConfig!)
            break
          case 'tilemap':
            this.load.image(asset.key, asset.url)
            break
          case 'tilemapTiledJSON':
            this.load.tilemapTiledJSON(asset.key, asset.url)
            break
          case 'audio':
            this.load.audio(asset.key, asset.url)
            break
          case 'text':
            this.load.text(asset.key, asset.url)
            break
        }
      } catch (e) {
        console.warn(`Failed to queue asset ${asset.key}:`, e)
      }
    })

    this.load.on('filecomplete', (_key: string) => {
      loaded++
      const progress = loaded / total
      this.updateProgress(progress)
    })

    this.load.on('loaderror', (file: any) => {
      console.warn(`Failed to load: ${file.key}`)
      loaded++
      this.updateProgress(loaded / total)
    })

    this.load.on('complete', () => {
      this.scene.start('MainMenuScene')
    })

  }

  private updateProgress(progress: number): void {
    const { width, height } = this.scale
    
    // Update progress bar
    this.progressBar.clear()
    this.progressBar.fillStyle(0xffd700, 1)
    this.progressBar.fillRoundedRect(width / 2 - 150, height / 2 - 13, 300 * progress, 24, 6)
    
    // Update percent text
    this.percentText.setText(`${Math.round(progress * 100)}%`)
    
    // Update loading text occasionally
    if (progress > 0.9) {
      this.loadingText.setText('SURFACING...')
    } else if (progress > 0.7) {
      this.loadingText.setText('DIVING DEEPER...')
    } else if (progress > 0.4) {
      this.loadingText.setText('SCANNING DEPTHS...')
    }
  }
}