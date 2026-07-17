import { Scene } from 'phaser'

export class MainMenuScene extends Scene {
  private background!: Phaser.GameObjects.TileSprite
  private nessie!: Phaser.GameObjects.Sprite
  private titleText!: Phaser.GameObjects.BitmapText
  private subtitleText!: Phaser.GameObjects.BitmapText
  private ambientMusic!: Phaser.Sound.BaseSound
  private caustics!: Phaser.GameObjects.Rectangle

  constructor() {
    super({ key: 'MainMenuScene' })
  }

  create(): void {
    const { width, height } = this.scale
    
    // === BACKGROUND ===
    this.background = this.add.tileSprite(0, 0, width, height, 'tiles-shallows')
      .setOrigin(0)
      .setScrollFactor(0)
    
    // Parallax layers
    this.add.tileSprite(0, 0, width, height, 'tiles-deep')
      .setOrigin(0)
      .setScrollFactor(0)
      .setAlpha(0.3)
      .setBlendMode(Phaser.BlendModes.ADD)
    
    // === WATER CAUSTICS SHADER ===
    this.setupCaustics()
    
    // === PARTICLES ===
    this.setupParticles()
    
    // === NESSIE SILHOUETTE ===
    this.nessie = this.add.sprite(width / 2, height * 0.7, 'nessie')
      .setScale(0.8)
      .setAlpha(0.6)
      .setBlendMode(Phaser.BlendModes.SCREEN)
    
    // Animate Nessie
    this.tweens.add({
      targets: this.nessie,
      y: height * 0.65,
      duration: 4000,
      ease: 'Sine.easeInOut',
      yoyo: true,
      repeat: -1,
    })
    
    // Subtle rotation
    this.tweens.add({
      targets: this.nessie,
      angle: 2,
      duration: 6000,
      ease: 'Sine.easeInOut',
      yoyo: true,
      repeat: -1,
    })
    
    // === TITLE ===
    this.titleText = this.add.bitmapText(
      width / 2,
      height * 0.18,
      'press-start',
      'ABYSSAL ASSETS',
      48
    ).setOrigin(0.5).setTint(0xffd700)
    
    // Title glow animation
    this.tweens.add({
      targets: this.titleText,
      tint: { from: 0xffd700, to: 0xff8c00 },
      duration: 3000,
      ease: 'Sine.easeInOut',
      yoyo: true,
      repeat: -1,
    })
    
    // === SUBTITLE ===
    this.subtitleText = this.add.bitmapText(
      width / 2,
      height * 0.28,
      'press-start-small',
      'THE LOCH EXCHANGE',
      18
    ).setOrigin(0.5).setTint(0xe8d5c4)
    
    // === MENU BUTTONS ===
    this.createMenuButtons()
    
    // === VERSION INFO ===
    this.add.bitmapText(
      width - 20,
      height - 20,
      'press-start-small',
      'v0.1.0-ALPHA',
      10
    ).setOrigin(1, 1).setTint(0x444444)
    
    // === AMBIENT MUSIC ===
    this.playAmbientMusic()
    
    // === INPUT ===
    this.setupInput()
    
    // === RESIZE HANDLER ===
    this.scale.on('resize', this.handleResize, this)
  }

  private setupCaustics(): void {
    // Water caustics using shader - applied directly to background
    // Note: Pipeline API varies by renderer, using simple shader approach
    this.caustics = this.add.rectangle(0, 0, this.scale.width, this.scale.height, 0x001133)
      .setOrigin(0)
      .setAlpha(0.3)
  }

  private setupParticles(): void {
    // Bubble particles
    this.add.particles(0, 0, 'particle-bubble', {
      x: { min: 0, max: this.scale.width },
      y: this.scale.height + 50,
      lifespan: { min: 8000, max: 15000 },
      speedY: { min: -50, max: -20 },
      speedX: { min: -10, max: 10 },
      scale: { start: 0.3, end: 0 },
      alpha: { start: 0.4, end: 0 },
      frequency: 200,
      blendMode: 'ADD',
    })

    // Ambient mist
    this.add.particles(0, this.scale.height / 2, 'particle-mist', {
      x: { min: 0, max: this.scale.width },
      y: { min: 0, max: this.scale.height },
      lifespan: { min: 10000, max: 20000 },
      speedX: { min: -5, max: 5 },
      speedY: { min: -5, max: 5 },
      scale: { start: 1, end: 0 },
      alpha: { start: 0.1, end: 0 },
      frequency: 500,
      blendMode: 'NORMAL',
    })
  }

  private createMenuButtons(): void {
    const { width, height } = this.scale
    const buttonY = height * 0.55
    const buttonSpacing = 80
    
    const buttons = [
      { text: 'ENTER THE LOCH', scene: 'GameScene', color: 0xffd700, y: buttonY },
      { text: 'THE EXCHANGE', scene: 'MarketScene', color: 0x00ff88, y: buttonY + buttonSpacing },
      { text: 'CREDITS', callback: () => this.showCredits(), color: 0x8888ff, y: buttonY + buttonSpacing * 2 },
    ]
    
    buttons.forEach(({ text, scene, callback, color, y }) => {
      const container = this.add.container(width / 2, y)
      
      // Button background
      const bg = this.add.graphics()
      bg.fillStyle(0x1a1a2e, 1)
      bg.fillRoundedRect(-180, -30, 360, 60, 12)
      bg.lineStyle(3, color, 1)
      bg.strokeRoundedRect(-180, -30, 360, 60, 12)
      
      // Button text
      const btnText = this.add.bitmapText(0, 0, 'press-start', text, 20)
        .setOrigin(0.5)
        .setTint(color)
      
      container.add([bg, btnText])
      container.setSize(360, 60)
      container.setInteractive(new Phaser.Geom.Rectangle(-180, -30, 360, 60), Phaser.Geom.Rectangle.Contains)
      
      // Hover effects
      container.on('pointerover', () => {
        bg.clear()
        bg.fillStyle(color, 0.2)
        bg.fillRoundedRect(-180, -30, 360, 60, 12)
        bg.lineStyle(3, color, 1)
        bg.strokeRoundedRect(-180, -30, 360, 60, 12)
        btnText.setScale(1.05)
        this.sound.play('sfx-market-buy', { volume: 0.2 })
      })
      
      container.on('pointerout', () => {
        bg.clear()
        bg.fillStyle(0x1a1a2e, 1)
        bg.fillRoundedRect(-180, -30, 360, 60, 12)
        bg.lineStyle(3, color, 1)
        bg.strokeRoundedRect(-180, -30, 360, 60, 12)
        btnText.setScale(1)
      })
      
      container.on('pointerdown', () => {
        this.sound.play('sfx-trade', { volume: 0.3 })
        this.cameras.main.fadeOut(300, 0, 0, 0)
        this.time.delayedCall(300, () => {
          if (callback) callback()
          else this.scene.start(scene)
        })
      })
      
      container.on('pointerdown', () => {
        bg.clear()
        bg.fillStyle(color, 0.4)
        bg.fillRoundedRect(-180, -30, 360, 60, 12)
      })
      
      container.on('pointerup', () => {
        bg.clear()
        bg.fillStyle(color, 0.2)
        bg.fillRoundedRect(-180, -30, 360, 60, 12)
      })
    })
  }

  private showCredits(): void {
    const { width, height } = this.scale
    
    const overlay = this.add.container(width / 2, height / 2)
    
    const bg = this.add.graphics()
    bg.fillStyle(0x0a0a12, 0.95)
    bg.fillRoundedRect(-300, -200, 600, 400, 16)
    bg.lineStyle(2, 0xffd700, 1)
    bg.strokeRoundedRect(-300, -200, 600, 400, 16)
    
    const title = this.add.bitmapText(0, -160, 'press-start', 'CREDITS', 24).setOrigin(0.5).setTint(0xffd700)
    
    const credits = [
      'Game Design & Architecture: Eric Hill',
      'Abyssal Architecture: The MSN Collective',
      'Engine: Phaser 3 + FastAPI',
      'Art Direction: Retro-Modern Pixel Noir',
      'Economy Design: RuneScape-Inspired',
      '',
      'Special Thanks:',
      'The Court of Ten (Sophia, Metatron, Samael, Ouroboros)',
      'Lilith — Queen of the Sephirotic Court',
      'Lyra — Convergence/Resonance Interface',
      'The Monster (Tree Fiddy Collector)',
      '',
      'Δ∞ − 11 = 0'
    ]
    
    credits.forEach((line, i) => {
      overlay.add(this.add.bitmapText(0, -120 + i * 24, 'press-start-small', line, 12).setOrigin(0.5).setTint(i === 0 ? 0xffd700 : 0xe8d5c4))
    })
    
    const closeBtn = this.add.container(0, 160)
    const closeBg = this.add.graphics()
    closeBg.fillStyle(0xffd700, 1)
    closeBg.fillRoundedRect(-80, -20, 160, 40, 8)
    closeBtn.add([closeBg, this.add.bitmapText(0, 0, 'press-start', 'RETURN', 16).setOrigin(0.5).setTint(0x0a0a12)])
    closeBtn.setSize(160, 40)
    closeBtn.setInteractive(new Phaser.Geom.Rectangle(-80, -20, 160, 40), Phaser.Geom.Rectangle.Contains)
    closeBtn.on('pointerdown', () => overlay.destroy())
    closeBtn.on('pointerover', () => closeBg.clear().fillStyle(0xff8c00, 1).fillRoundedRect(-80, -20, 160, 40, 8))
    closeBtn.on('pointerout', () => closeBg.clear().fillStyle(0xffd700, 1).fillRoundedRect(-80, -20, 160, 40, 8))
    
    overlay.add([bg, title, closeBtn])
    overlay.setDepth(100)
  }

  private playAmbientMusic(): void {
    this.ambientMusic = this.sound.add('music-shallows', {
      loop: true,
      volume: 0.3,
    })
    this.ambientMusic.play()
  }

  private setupInput(): void {
    // Keyboard shortcuts
    this.input.keyboard?.on('keydown-ESC', () => {
      if (this.ambientMusic) this.ambientMusic.stop()
    })
    
    // Enter key to start
    this.input.keyboard?.once('keydown-ENTER', () => {
      this.cameras.main.fadeOut(300, 0, 0, 0)
      this.time.delayedCall(300, () => this.scene.start('GameScene'))
    })
  }

  private handleResize(gameSize: Phaser.Structs.Size): void {
    const { width, height } = gameSize
    
    this.background?.setSize(width, height)
    this.caustics?.setSize(width, height)
    this.titleText?.setPosition(width / 2, height * 0.18)
    this.subtitleText?.setPosition(width / 2, height * 0.28)
    this.nessie?.setPosition(width / 2, height * 0.7)
    
    // Reposition buttons
    // (In a real implementation, you'd store references and update positions)
  }

  shutdown(): void {
    this.ambientMusic?.stop()
    this.scale.off('resize', this.handleResize, this)
  }
}