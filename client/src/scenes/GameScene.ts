import { Scene } from 'phaser'

export class GameScene extends Scene {
  private boat!: Phaser.Physics.Arcade.Sprite
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys
  private wasd!: Record<string, Phaser.Input.Keyboard.Key>
  private map!: Phaser.Tilemaps.Tilemap
  private backgroundLayer!: Phaser.Tilemaps.TilemapLayer
  private collisionLayer!: Phaser.Tilemaps.TilemapLayer
  private camera!: Phaser.Cameras.Scene2D.Camera
  private hud!: Phaser.GameObjects.Container
  private cloutText!: Phaser.GameObjects.BitmapText
  private coinsText!: Phaser.GameObjects.BitmapText
  private zoneText!: Phaser.GameObjects.BitmapText
  private dredgePrompt!: Phaser.GameObjects.Container
  private isNearDredgeSpot: boolean = false
  private currentZone: string = 'shallows'
  private clout: number = 0
  private coins: number = 0
  private nessie!: Phaser.GameObjects.Sprite
  private ambientMusic!: Phaser.Sound.BaseSound
  // @ts-ignore - assigned in createParticles()
  private _bubbles!: Phaser.GameObjects.Particles.ParticleEmitter

  constructor() {
    super({ key: 'GameScene' })
  }

  create(): void {
    const { width, height } = this.scale

    // === CAMERA ===
    this.camera = this.cameras.main
    this.camera.setBounds(0, 0, width * 10, height * 10)
    this.camera.setRoundPixels(true)

    // === MAP ===
    this.createMap()

    // === NESSIE (background) ===
    this.nessie = this.add.sprite(width * 5, height * 5, 'nessie')
      .setScale(2)
      .setAlpha(0.3)
      .setBlendMode(Phaser.BlendModes.SCREEN)
      .setDepth(-10)

    // Subtle Nessie animation
    this.tweens.add({
      targets: this.nessie,
      x: width * 5 + 200,
      y: height * 5 - 100,
      duration: 15000,
      ease: 'Sine.easeInOut',
      yoyo: true,
      repeat: -1,
    })

    // === PLAYER & BOAT ===
    this.createPlayer()

    // === CAMERA FOLLOW ===
    this.camera.startFollow(this.boat, true, 0.1, 0.1)
    this.camera.setZoom(1.5)

    // === HUD ===
    this.createHUD()

    // === DREDGE PROMPT ===
    this.createDredgePrompt()

    // === PARTICLES ===
    this.createParticles()

    // === CAUSTICS ===
    this.setupCaustics()

    // === INPUT ===
    this.setupInput()

    // === ZONE DETECTION ===
    this.setupZoneDetection()

    // === AMBIENT MUSIC ===
    this.playAmbientMusic()

    // === NETWORK ===
    this.setupNetwork()

    // === RESIZE ===
    this.scale.on('resize', this.handleResize, this)
  }

  private createMap(): void {
    // Create a large procedural map
    const mapWidth = this.scale.width * 10
    const mapHeight = this.scale.height * 10
    const tileSize = 32

    this.map = this.make.tilemap({
      tileWidth: tileSize,
      tileHeight: tileSize,
      width: mapWidth / tileSize,
      height: mapHeight / tileSize,
    })

    // Add tileset images - assert non-null since we generated the assets
    const tileset = this.map.addTilesetImage('tiles-shallows', 'tiles-shallows', 32, 32, 0, 0)!
    const deepTileset = this.map.addTilesetImage('tiles-deep', 'tiles-deep', 32, 32, 0, 0)!

    // Create layers - assert non-null
    this.backgroundLayer = this.map.createBlankLayer('Background', tileset, 0, 0)!
    const deepLayer = this.map.createBlankLayer('Deep', deepTileset, 0, 0)!

    // Procedural generation
    this.generateTerrain(this.backgroundLayer, 'shallows')
    if (deepLayer) {
      this.generateTerrain(deepLayer, 'deep')

      // Set collision on deep layer
      deepLayer.setCollisionByExclusion([-1])

      this.collisionLayer = deepLayer
    }

    // World bounds
    this.physics.world.setBounds(0, 0, mapWidth, mapHeight)
  }

  private generateTerrain(layer: Phaser.Tilemaps.TilemapLayer, zone: string): void {
    const width = layer.width
    const height = layer.height

    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        // Perlin-style noise for terrain
        const noise = this.noise2D(x * 0.1, y * 0.1) * 0.5 + this.noise2D(x * 0.05, y * 0.05) * 0.5

        let tileIndex = 0
        if (zone === 'shallows') {
          // Shallows: mostly sand (0), some rocks (1-3), rare coral (4-6)
          if (noise > 0.7) tileIndex = Phaser.Math.Between(1, 3)
          else if (noise > 0.9) tileIndex = Phaser.Math.Between(4, 6)
        } else {
          // Deep: mostly dark water (0), some trenches (7-9), vents (10-12)
          if (noise < 0.2) tileIndex = Phaser.Math.Between(7, 9)
          else if (noise > 0.95) tileIndex = Phaser.Math.Between(10, 12)
        }

        if (tileIndex > 0) {
          layer.putTileAt(tileIndex, x, y)
        }
      }
    }
  }

  private noise2D(x: number, y: number): number {
    // Simple 2D noise
    const n = Math.sin(x * 12.9898 + y * 78.233) * 43758.5453
    return n - Math.floor(n)
  }

  private createPlayer(): void {
    const centerX = this.scale.width * 5
    const centerY = this.scale.height * 5

    // Boat sprite
    this.boat = this.physics.add.sprite(centerX, centerY, 'boat-basic')
      .setScale(1)
      .setCollideWorldBounds(true)
      .setDamping(true)
      .setDrag(0.98)
      .setMaxVelocity(300)

    // Player sprite (on boat) - hidden while on boat, used for future disembark logic
    // @ts-ignore - intentionally unused until disembark feature
    const _player = this.physics.add.sprite(centerX, centerY - 20, 'player')
      .setScale(1)
      .setDepth(10)
      .setVisible(false)

    // Collision
    this.physics.add.collider(this.boat, this.collisionLayer)

    // Boat animation
    this.anims.create({
      key: 'boat-idle',
      frames: this.anims.generateFrameNumbers('boat-basic', { start: 0, end: 3 }),
      frameRate: 4,
      repeat: -1,
    })
    this.boat.play('boat-idle')
  }

  private createHUD(): void {
    this.hud = this.add.container(20, 20).setScrollFactor(0).setDepth(100)

    // Background panel
    const bg = this.add.graphics()
    bg.fillStyle(0x0a0a12, 0.9)
    bg.fillRoundedRect(-10, -10, 280, 120, 12)
    bg.lineStyle(2, 0xffd700, 1)
    bg.strokeRoundedRect(-10, -10, 280, 120, 12)
    this.hud.add(bg)

    // Clout
    this.cloutText = this.add.bitmapText(0, 0, 'press-start-small', `RESONANCE: ${this.formatNumber(this.clout)}`, 14)
      .setTint(0x00ff88)
    this.hud.add(this.cloutText)

    // Coins
    this.coinsText = this.add.bitmapText(0, 25, 'press-start-small', `SOUL COINS: ${this.formatNumber(this.coins)}`, 14)
      .setTint(0xffd700)
    this.hud.add(this.coinsText)

    // Zone
    this.zoneText = this.add.bitmapText(0, 50, 'press-start-small', `ZONE: ${this.currentZone.toUpperCase()}`, 14)
      .setTint(0x00ff88)
    this.hud.add(this.zoneText)

    // Resonance bar
    this.createResonanceBar()

    // Player avatar
    this.add.sprite(-120, 55, 'player').setScale(0.5).setDepth(1)
  }

  private createResonanceBar(): void {
    const bg = this.add.graphics()
    bg.fillStyle(0x1a1a2e, 1)
    bg.fillRoundedRect(-10, 75, 260, 20, 6)
    bg.lineStyle(1, 0x333, 1)
    bg.strokeRoundedRect(-10, 75, 260, 20, 6)
    this.hud.add(bg)

    // Fill based on clout percentage to next tier
    const nextTierThreshold = this.getNextTierThreshold()
    const progress = Math.min(this.clout / nextTierThreshold, 1)
    
    const fill = this.add.graphics()
    fill.fillStyle(0x00ff88, 1)
    fill.fillRoundedRect(-8, 77, 256 * progress, 16, 4)
    this.hud.add(fill)

    this.add.bitmapText(0, 78, 'press-start-small', `${this.clout} / ${nextTierThreshold}`, 10)
      .setOrigin(0.5, 0).setPosition(120, 78).setTint(0x888888)
  }

  private getNextTierThreshold(): number {
    if (this.clout < 100) return 100
    if (this.clout < 1000) return 1000
    if (this.clout < 10000) return 10000
    if (this.clout < 100000) return 100000
    if (this.clout < 1000000) return 1000000
    return 1000000
  }

  private createDredgePrompt(): void {
    const { width, height } = this.scale
    this.dredgePrompt = this.add.container(width / 2, height - 100).setScrollFactor(0).setDepth(100).setVisible(false)

    const bg = this.add.graphics()
    bg.fillStyle(0x0a0a12, 0.95)
    bg.fillRoundedRect(-150, -30, 300, 60, 12)
    bg.lineStyle(2, 0xffd700, 1)
    bg.strokeRoundedRect(-150, -30, 300, 60, 12)

    const text = this.add.bitmapText(0, 0, 'press-start', 'PRESS [E] TO EXTRACT', 18)
      .setOrigin(0.5)
      .setTint(0xffd700)

    this.dredgePrompt.add([this.add.graphics().fillStyle(0x1a1a2e, 1).fillRoundedRect(-150, -30, 300, 60, 12), text])
  }

  private createParticles(): void {
    // Water bubbles
    this._bubbles = this.add.particles(0, 0, 'particle-bubble', {
      x: { min: 0, max: this.scale.width * 10 },
      y: this.scale.height * 10 + 50,
      lifespan: { min: 8000, max: 15000 },
      speedY: { min: -50, max: -20 },
      speedX: { min: -10, max: 10 },
      scale: { start: 0.3, end: 0 },
      alpha: { start: 0.3, end: 0 },
      frequency: 100,
      blendMode: 'ADD',
    })

    // Ambient mist
    this.add.particles(0, this.scale.height * 5, 'particle-mist', {
      x: { min: 0, max: this.scale.width * 10 },
      y: { min: 0, max: this.scale.height * 10 },
      lifespan: { min: 10000, max: 20000 },
      speedX: { min: -5, max: 5 },
      speedY: { min: -5, max: 5 },
      scale: { start: 1, end: 0 },
      alpha: { start: 0.05, end: 0 },
      frequency: 300,
    })
  }

  private setupCaustics(): void {
    const caustics = this.add.rectangle(0, 0, this.scale.width * 10, this.scale.height * 10, 0x001133)
      .setOrigin(0)
      .setAlpha(0.2)
      .setDepth(-5)
    
    // Simple caustics animation
    this.tweens.add({
      targets: caustics,
      alpha: { from: 0.1, to: 0.3 },
      duration: 3000,
      ease: 'Sine.easeInOut',
      yoyo: true,
      repeat: -1,
    })
  }

  private setupInput(): void {
    this.cursors = this.input.keyboard!.createCursorKeys()
    this.wasd = this.input.keyboard!.addKeys('W,A,S,D,E,I,M') as Record<string, Phaser.Input.Keyboard.Key>
  }

  private setupZoneDetection(): void {
    // Check zone based on Y position (depth)
    this.events.on('update', () => {
      const boatY = this.boat.y
      const maxDepth = this.scale.height * 10
      const depthRatio = boatY / maxDepth

      let newZone = 'shallows'
      if (depthRatio > 0.9) newZone = 'trench'
      else if (depthRatio > 0.7) newZone = 'abyssal'
      else if (depthRatio > 0.5) newZone = 'deep'
      else if (depthRatio > 0.3) newZone = 'standard'

      if (newZone !== this.currentZone) {
        this.currentZone = newZone
        this.zoneText.setText(`ZONE: ${newZone.toUpperCase()}`)
        this.onZoneChange(newZone)
      }

      // Check dredge spot proximity
      this.checkDredgeSpot()
    })
  }

  private onZoneChange(zone: string): void {
    const zoneColors: Record<string, number> = {
      shallows: 0x00ff88,
      standard: 0x00ffff,
      deep: 0x0088ff,
      abyssal: 0x8800ff,
      trench: 0xff00ff,
    }
    this.zoneText.setTint(zoneColors[zone] || 0x00ff88)
    
    // Show zone transition notification
    this.showNotification(`ENTERING: ${zone.toUpperCase()}`, zoneColors[zone])
  }

  private showNotification(message: string, color: number): void {
    const { width, height } = this.scale
    const notif = this.add.container(width / 2, height * 0.15).setScrollFactor(0).setDepth(200)

    const bg = this.add.graphics()
    bg.fillStyle(0x0a0a12, 0.95)
    bg.fillRoundedRect(-150, -20, 300, 40, 8)
    bg.lineStyle(2, color, 1)
    bg.strokeRoundedRect(-150, -20, 300, 40, 8)

    const textObj = this.add.bitmapText(0, 0, 'press-start', message, 16).setOrigin(0.5).setTint(color)

    notif.add([bg, textObj])

    this.tweens.add({
      targets: notif,
      alpha: 0,
      y: height * 0.1,
      duration: 3000,
      ease: 'Power2',
      onComplete: () => notif.destroy(),
    })
  }

  private checkDredgeSpot(): void {
    // Every 500px there's a dredge spot
    const spotX = Math.round(this.boat.x / 500) * 500
    const spotY = Math.round(this.boat.y / 500) * 500
    const distance = Phaser.Math.Distance.Between(this.boat.x, this.boat.y, spotX, spotY)
    
    const wasNear = this.isNearDredgeSpot
    this.isNearDredgeSpot = distance < 80
    
    if (this.isNearDredgeSpot !== wasNear) {
      this.dredgePrompt.setVisible(this.isNearDredgeSpot)
      if (this.isNearDredgeSpot) {
        // Pulse animation
        this.tweens.add({
          targets: this.dredgePrompt,
          scale: { from: 1, to: 1.05 },
          duration: 800,
          ease: 'Sine.easeInOut',
          yoyo: true,
          repeat: -1,
        })
      } else {
        this.tweens.killTweensOf(this.dredgePrompt)
        this.dredgePrompt.setScale(1)
      }
    }
  }

  private setupNetwork(): void {
    // WebSocket connection for multiplayer (placeholder for future implementation)
    // this.socket = io('http://localhost:8000', { transports: ['websocket'] })
    // this.socket.on('playerJoined', (_data: any) => { /* Add other player */ })
    // this.socket.on('playerLeft', (_id: string) => { /* Remove player */ })
    // this.socket.on('marketUpdate', (_data: any) => { /* Update market prices */ })
    // this.socket.on('cloutUpdate', (_data: any) => { this.clout = _data.clout; this.coins = _data.coins; })
  }

  private playAmbientMusic(): void {
    const zoneMusic: Record<string, string> = {
      shallows: 'music-shallows',
      standard: 'music-standard',
      deep: 'music-deep',
      abyssal: 'music-abyssal',
      trench: 'music-trench',
    }
    const musicKey = zoneMusic[this.currentZone] || 'music-shallows'
    this.ambientMusic = this.sound.add(musicKey, { loop: true, volume: 0.25 })
    this.ambientMusic.play()
  }

  update(_time: number, _delta: number): void {
    if (!this.boat || !this.boat.body) return

    // === MOVEMENT ===
    const acceleration = 50
    
    let vx = 0, vy = 0
    
    if (this.cursors.left?.isDown || this.wasd.A?.isDown) vx = -1
    if (this.cursors.right?.isDown || this.wasd.D?.isDown) vx = 1
    if (this.cursors.up?.isDown || this.wasd.W?.isDown) vy = -1
    if (this.cursors.down?.isDown || this.wasd.S?.isDown) vy = 1

    // Normalize diagonal
    if (vx !== 0 && vy !== 0) {
      vx *= 0.7071
      vy *= 0.7071
    }

    this.boat.setAcceleration(vx * acceleration, vy * acceleration)

    // === DREDGING ===
    if (Phaser.Input.Keyboard.JustDown(this.wasd.E) && this.isNearDredgeSpot) {
      this.startDredging()
    }

    // === UI TOGGLES ===
    if (Phaser.Input.Keyboard.JustDown(this.wasd.I)) {
      this.toggleInventory()
    }
    if (Phaser.Input.Keyboard.JustDown(this.wasd.M)) {
      this.scene.launch('MarketScene')
    }

    // === CAMERA ZOOM ===
    if (this.wasd.M?.isDown) {
      this.camera.setZoom(1)
    } else {
      this.camera.setZoom(1.5)
    }

    // === HUD UPDATE ===
    this.cloutText.setText(`RESONANCE: ${this.formatNumber(this.clout)}`)
    this.coinsText.setText(`SOUL COINS: ${this.formatNumber(this.coins)}`)
  }

  private startDredging(): void {
    // Launch dredge mini-game scene
    this.scene.pause()
    this.scene.launch('DredgeMiniGameScene', { 
      zone: this.currentZone,
      playerClout: this.clout,
      boatLevel: 1, // TODO: boat upgrades
    })
  }

  private toggleInventory(): void {
    // TODO: Inventory scene
    console.log('Inventory toggle')
  }

  private formatNumber(num: number): string {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
    return num.toString()
  }

  private handleResize(gameSize: Phaser.Structs.Size): void {
    this.hud?.setPosition(20, 20)
    this.dredgePrompt?.setPosition(gameSize.width / 2, gameSize.height - 100)
  }

  shutdown(): void {
    this.ambientMusic?.stop()
    this.scale.off('resize', this.handleResize, this)
  }
}