import { Scene, GameObjects, Math as PhaserMath } from 'phaser'

interface DredgeSpotData {
  x: number
  y: number
  zone: string
  depth: number
  active: boolean
  cooldown: number
}

interface DredgeMiniGameData {
  spot: DredgeSpotData
  playerClout: number
  boatTier: number
  onComplete: (result: { success: boolean; loot?: any }) => void
}

export class DredgeMiniGameScene extends Scene {
  private spot!: DredgeSpotData
  private playerClout!: number
  private boatTier!: number
  private onComplete!: (result: { success: boolean; loot?: any }) => void

  // Sonar sweep mechanics
  private sweepLine!: GameObjects.Graphics
  private sweepAngle: number = -Math.PI / 2
  private sweepSpeed: number = 0
  private isSweeping: boolean = false
  private sweepDirection: number = 1
  private readonly SWEEP_MIN_SPEED = 0.02
  private readonly SWEEP_MAX_SPEED = 0.08

  // Target zone (the "hit" area)
  private targetZone!: { start: number; end: number; depth: number }
  private targetGraphics!: GameObjects.Graphics

  // UI Elements
  // @ts-ignore - assigned in createUI()
  private _zoneNameDisplay!: GameObjects.BitmapText
  // @ts-ignore - assigned in createUI()
  private _depthDisplay!: GameObjects.BitmapText
  private instructionText!: GameObjects.BitmapText
  private sonarPing!: GameObjects.Graphics
  private pingRadius: number = 0
  private pingAlpha: number = 0

  // Result
  private result: { success: boolean; loot?: any } | null = null
  private resultContainer!: GameObjects.Container
  private isComplete: boolean = false

  // Audio
  private sonarLoop: Phaser.Sound.BaseSound | null = null
  private ambientLoop: Phaser.Sound.BaseSound | null = null

  constructor() {
    super({ key: 'DredgeMiniGameScene' })
  }

  init(data: DredgeMiniGameData): void {
    this.spot = data.spot
    this.playerClout = data.playerClout
    this.boatTier = data.boatTier
    this.onComplete = data.onComplete
  }

  create(): void {
    // === BACKGROUND ===
    this.createBackground()

    // === SONAR DISPLAY ===
    this.createSonarDisplay()

    // === UI ===
    this.createUI()

    // === INPUT ===
    this.setupInput()

    // === TARGET ZONE GENERATION ===
    this.generateTargetZone()

    // === AUDIO ===
    this.playAudio()

    // === RESET STATE ===
    this.isSweeping = false
    this.sweepAngle = -Math.PI / 2
    this.sweepSpeed = 0
    this.isComplete = false
    this.result = null
  }

  private createBackground(): void {
    const { width, height } = this.scale

    // Dark water background
    this.add.rectangle(0, 0, width, height, 0x051020).setOrigin(0)

    // Subtle grid lines for depth feel
    const grid = this.add.graphics()
    grid.lineStyle(1, 0x0a2a40, 0.5)
    for (let i = 0; i < width; i += 50) {
      grid.lineBetween(i, 0, i, height)
    }
    for (let i = 0; i < height; i += 50) {
      grid.lineBetween(0, i, width, i)
    }
    grid.setDepth(-5)

    // Caustic light rays
    for (let i = 0; i < 5; i++) {
      const ray = this.add.graphics()
      ray.fillStyle(0x1a4a6a, 0.05)
      const x = PhaserMath.Between(0, width)
      ray.fillTriangle(x, height, x + 300, 0, x - 300, 0)
      ray.setDepth(-4)
      this.tweens.add({
        targets: ray,
        alpha: { from: 0.05, to: 0.15 },
        x: x + PhaserMath.Between(-100, 100),
        duration: PhaserMath.Between(8000, 20000),
        ease: 'Sine.easeInOut',
        yoyo: true,
        repeat: -1,
      })
    }

    // Floating particles
    this.add.particles(0, 0, 'particle-mist', {
      x: { min: 0, max: width },
      y: { min: 0, max: height },
      lifespan: { min: 5000, max: 15000 },
      speedX: { min: -10, max: 10 },
      speedY: { min: -20, max: 5 },
      scale: { start: 0.5, end: 0 },
      alpha: { start: 0.2, end: 0 },
      frequency: 300,
      blendMode: 'ADD',
    }).setDepth(-3)
  }

  private createSonarDisplay(): void {
    const { width, height } = this.scale
    const centerX = width / 2
    const centerY = height / 2
    const radarRadius = Math.min(width, height) * 0.35

    // Radar background circle
    const radarBg = this.add.graphics()
    radarBg.fillStyle(0x0a0a1a, 1)
    radarBg.fillCircle(centerX, centerY, radarRadius + 20)
    radarBg.lineStyle(3, 0x00ff88, 0.5)
    radarBg.strokeCircle(centerX, centerY, radarRadius + 20)
    radarBg.setDepth(5)

    // Range rings
    const rings = this.add.graphics()
    rings.lineStyle(1, 0x00ff88, 0.2)
    for (let r = 0.25; r <= 1; r += 0.25) {
      rings.strokeCircle(centerX, centerY, radarRadius * r)
    }
    rings.setDepth(6)

    // Crosshairs
    const crosshairs = this.add.graphics()
    crosshairs.lineStyle(1, 0x00ff88, 0.3)
    crosshairs.lineBetween(centerX - radarRadius, centerY, centerX + radarRadius, centerY)
    crosshairs.lineBetween(centerX, centerY - radarRadius, centerX, centerY + radarRadius)
    crosshairs.setDepth(7)

    // Sweep line (the moving sonar beam)
    this.sweepLine = this.add.graphics()
    this.sweepLine.setDepth(10)

    // Target zone indicator
    this.targetGraphics = this.add.graphics()
    this.targetGraphics.setDepth(8)

    // Sonar ping effect
    this.sonarPing = this.add.graphics()
    this.sonarPing.setDepth(9)

    // Depth markers around radar
    for (let i = 0; i < 8; i++) {
      const angle = (i / 8) * Math.PI * 2 - Math.PI / 2
      const labelR = radarRadius + 45
      const lx = centerX + Math.cos(angle) * labelR
      const ly = centerY + Math.sin(angle) * labelR
      const depthLabel = (i + 1) * 250
      this.add.bitmapText(lx, ly, 'press-start-small', `${depthLabel}m`, 8)
        .setOrigin(0.5)
        .setTint(0x00ff88)
        .setDepth(6)
    }
  }

  private createUI(): void {
    const { width, height } = this.scale

    // Top info panel
    const panelBg = this.add.graphics()
    panelBg.fillStyle(0x0a0a12, 0.9)
    panelBg.fillRoundedRect(20, 20, width - 40, 100, 12)
    panelBg.lineStyle(2, 0x00ff88, 0.5)
    panelBg.strokeRoundedRect(20, 20, width - 40, 100, 12)
    panelBg.setDepth(20).setScrollFactor(0)

    // Zone name
    this._zoneNameDisplay = this.add.bitmapText(width / 2, 40, 'press-start', this.spot.zone.toUpperCase(), 20)
      .setOrigin(0.5)
      .setTint(this.getZoneColor(this.spot.zone))
      .setDepth(21)
      .setScrollFactor(0)

    // Depth
    this._depthDisplay = this.add.bitmapText(width / 2, 70, 'press-start-small', `TARGET DEPTH: ${this.spot.depth}m`, 14)
      .setOrigin(0.5)
      .setTint(0xffd700)
      .setDepth(21)
      .setScrollFactor(0)

    // Difficulty
    const difficulty = this.calculateDifficulty()
    this.add.bitmapText(width - 140, 45, 'press-start-small', `DIFFICULTY: ${difficulty}`, 10)
      .setOrigin(1, 0.5)
      .setTint(difficulty === 'TRIVIAL' ? 0x4caf50 : difficulty === 'EASY' ? 0x8bc34a : difficulty === 'NORMAL' ? 0xff9800 : difficulty === 'HARD' ? 0xf44336 : 0xff00ff)
      .setDepth(21)
      .setScrollFactor(0)

    // Boat tier
    this.add.bitmapText(width - 140, 70, 'press-start-small', `SONAR: MK${this.boatTier}`, 10)
      .setOrigin(1, 0.5)
      .setTint(0x00ff88)
      .setDepth(21)
      .setScrollFactor(0)

    // Instruction
    this.instructionText = this.add.bitmapText(width / 2, height - 80, 'press-start-small', 'PRESS [SPACE] TO START SONAR SWEEP', 14)
      .setOrigin(0.5)
      .setTint(0xe8d5c4)
      .setDepth(20)
      .setScrollFactor(0)

    // Pulse the instruction
    this.tweens.add({
      targets: this.instructionText,
      alpha: { from: 1, to: 0.4 },
      duration: 1500,
      ease: 'Sine.easeInOut',
      yoyo: true,
      repeat: -1,
    })

    // Result container (hidden initially)
    this.resultContainer = this.add.container(width / 2, height / 2).setDepth(50).setScrollFactor(0).setVisible(false)
  }

  private setupInput(): void {
    this.input.keyboard!.on('keydown-SPACE', () => {
      if (!this.isSweeping && !this.isComplete) {
        this.startSweep()
      } else if (this.isSweeping && !this.isComplete) {
        this.onSpacePressedDuringSweep()
      }
    })

    // Allow clicking too
    this.input.on('pointerdown', () => {
      if (!this.isSweeping && !this.isComplete) {
        this.startSweep()
      } else if (this.isSweeping && !this.isComplete) {
        this.onSpacePressedDuringSweep()
      }
    })

    // Escape to cancel (forfeit)
    this.input.keyboard!.on('keydown-ESC', () => {
      if (!this.isComplete) {
        this.forfeit()
      }
    })
  }

  private calculateDifficulty(): string {
    // Base difficulty from depth
    let difficultyScore = this.spot.depth / 2000 // 0-1+

    // Boat tier reduces difficulty
    difficultyScore -= (this.boatTier - 1) * 0.15

    // Clout reduces difficulty slightly
    difficultyScore -= Math.min(this.playerClout / 100000, 0.3)

    // Zone modifier
    const zoneMod: Record<string, number> = {
      shallows: -0.2,
      standard: 0,
      deep: 0.15,
      trench: 0.3,
      abyssal: 0.5,
    }
    difficultyScore += zoneMod[this.spot.zone] || 0

    difficultyScore = PhaserMath.Clamp(difficultyScore, 0, 1)

    if (difficultyScore < 0.15) return 'TRIVIAL'
    if (difficultyScore < 0.35) return 'EASY'
    if (difficultyScore < 0.55) return 'NORMAL'
    if (difficultyScore < 0.8) return 'HARD'
    return 'ABYSSAL'
  }

  private generateTargetZone(): void {
    const { width, height } = this.scale
    const centerX = width / 2
    const centerY = height / 2
    const radarRadius = Math.min(width, height) * 0.35

    // Calculate target angle based on depth
    // Deeper = narrower target zone, more precise timing needed
    const difficulty = this.calculateDifficulty()
    let targetWidth: number

    switch (difficulty) {
      case 'TRIVIAL': targetWidth = 0.6; break // ~34 degrees
      case 'EASY': targetWidth = 0.45; break  // ~26 degrees
      case 'NORMAL': targetWidth = 0.3; break  // ~17 degrees
      case 'HARD': targetWidth = 0.2; break    // ~11 degrees
      case 'ABYSSAL': targetWidth = 0.12; break // ~7 degrees
      default: targetWidth = 0.3;
    }

    // Boat tier widens target slightly
    targetWidth += (this.boatTier - 1) * 0.05

    // Randomize target position within the sweep arc (90 degrees to 270 degrees = bottom half)
    const sweepStart = -Math.PI / 2 // -90 degrees (left)
    const sweepEnd = Math.PI / 2     // 90 degrees (right)
    const sweepRange = sweepEnd - sweepStart

    const targetCenter = sweepStart + PhaserMath.FloatBetween(targetWidth / 2, sweepRange - targetWidth / 2)

    this.targetZone = {
      start: targetCenter - targetWidth / 2,
      end: targetCenter + targetWidth / 2,
      depth: this.spot.depth,
    }

    // Draw target zone
    this.targetGraphics.clear()
    this.targetGraphics.fillStyle(0xffd700, 0.15)
    this.targetGraphics.slice(centerX, centerY, radarRadius, this.targetZone.start, this.targetZone.end, false)
    this.targetGraphics.fillPath()

    this.targetGraphics.lineStyle(2, 0xffd700, 0.8)
    this.targetGraphics.slice(centerX, centerY, radarRadius, this.targetZone.start, this.targetZone.end, false)
    this.targetGraphics.strokePath()

    // Add glow effect
    const glowTween = this.tweens.add({
      targets: this.targetGraphics,
      alpha: { from: 1, to: 0.5 },
      duration: 1000,
      ease: 'Sine.easeInOut',
      yoyo: true,
      repeat: -1,
    })
    this.targetGraphics.setData('glowTween', glowTween)
  }

  private startSweep(): void {
    this.isSweeping = true
    this.sweepAngle = -Math.PI / 2
    this.sweepSpeed = this.SWEEP_MIN_SPEED
    this.sweepDirection = 1

    // Update instruction
    this.instructionText.setText('PRESS [SPACE] TO STOP ON TARGET ZONE')
    this.instructionText.setTint(0xffd700)

    // Play sweep start sound
    this.sound.play('sfx-dredge-start', { volume: 0.5 })

    // Start sonar ping loop
    this.startSonarPing()
  }

  private startSonarPing(): void {
    const { width, height } = this.scale
    const centerX = width / 2
    const centerY = height / 2

    this.time.addEvent({
      delay: 800,
      loop: true,
      callback: () => {
        if (!this.isSweeping || this.isComplete) return

        this.pingRadius = 0
        this.pingAlpha = 0.8
        this.sound.play('sfx-market-buy', { volume: 0.15, rate: 1.5 })

        this.tweens.add({
          targets: this,
          pingRadius: Math.min(width, height) * 0.4,
          pingAlpha: 0,
          duration: 800,
          ease: 'Power2',
          onUpdate: () => {
            this.sonarPing.clear()
            this.sonarPing.lineStyle(2, 0x00ff88, this.pingAlpha)
            this.sonarPing.strokeCircle(centerX, centerY, this.pingRadius)
          },
        })
      },
    })
  }

  update(_time: number, delta: number): void {
    if (this.isComplete) return

    if (this.isSweeping) {
      this.updateSweep(delta)
    }

    // Draw sweep line
    this.drawSweepLine()
  }

  private updateSweep(delta: number): void {
    const sweepStart = -Math.PI / 2
    const sweepEnd = Math.PI / 2
    const sweepRange = sweepEnd - sweepStart

    // Accelerate then decelerate (pendulum motion)
    const progress = (this.sweepAngle - sweepStart) / sweepRange

    if (this.sweepDirection > 0) {
      // Accelerating to middle, then decelerating
      if (progress < 0.5) {
        this.sweepSpeed = PhaserMath.Linear(this.SWEEP_MIN_SPEED, this.SWEEP_MAX_SPEED, progress * 2)
      } else {
        this.sweepSpeed = PhaserMath.Linear(this.SWEEP_MAX_SPEED, this.SWEEP_MIN_SPEED, (progress - 0.5) * 2)
      }
    } else {
      // Return sweep - constant speed
      this.sweepSpeed = this.SWEEP_MAX_SPEED * 0.7
    }

    this.sweepAngle += this.sweepSpeed * this.sweepDirection * (delta / 16.67)

    // Check bounds
    if (this.sweepAngle >= sweepEnd && this.sweepDirection > 0) {
      this.sweepAngle = sweepEnd
      this.sweepDirection = -1
      // Play turn sound
      this.sound.play('sfx-dredge-pull', { volume: 0.3, rate: 0.8 })
    } else if (this.sweepAngle <= sweepStart && this.sweepDirection < 0) {
      this.sweepAngle = sweepStart
      // Missed the target - auto-forfeit after return sweep
      this.missedTarget()
    }
  }

  private drawSweepLine(): void {
    const { width, height } = this.scale
    const centerX = width / 2
    const centerY = height / 2
    const radarRadius = Math.min(width, height) * 0.35

    this.sweepLine.clear()

    // Main beam
    const endX = centerX + Math.cos(this.sweepAngle) * radarRadius
    const endY = centerY + Math.sin(this.sweepAngle) * radarRadius

    // Beam core
    this.sweepLine.lineStyle(4, 0x00ff88, 1)
    this.sweepLine.lineBetween(centerX, centerY, endX, endY)

    // Beam glow
    this.sweepLine.lineStyle(12, 0x00ff88, 0.15)
    this.sweepLine.lineBetween(centerX, centerY, endX, endY)

    // Beam tip
    this.sweepLine.fillStyle(0x00ff88, 1)
    this.sweepLine.fillCircle(endX, endY, 6)

    // Check if beam is over target zone
    const inTarget = this.sweepAngle >= this.targetZone.start && this.sweepAngle <= this.targetZone.end

    if (inTarget) {
      // Highlight when over target
      this.sweepLine.lineStyle(6, 0xffd700, 1)
      this.sweepLine.lineBetween(centerX, centerY, endX, endY)
      this.sweepLine.fillStyle(0xffd700, 1)
      this.sweepLine.fillCircle(endX, endY, 8)
    }
  }

  private checkHit(): boolean {
    return this.sweepAngle >= this.targetZone.start && this.sweepAngle <= this.targetZone.end
  }

  private onSpacePressedDuringSweep(): void {
    if (!this.isSweeping || this.isComplete) return

    const hit = this.checkHit()
    this.isSweeping = false
    this.isComplete = true

    // Stop instruction pulse
    this.tweens.killTweensOf(this.instructionText)

    if (hit) {
      this.success()
    } else {
      this.failure()
    }
  }

  private success(): void {
    this.sound.play('sfx-dredge-success', { volume: 0.6 })

    // Generate loot
    const loot = this.generateLoot()

    this.result = { success: true, loot }
    this.showResult(true, loot)

    // Call completion callback after delay
    this.time.delayedCall(3000, () => {
      this.onComplete(this.result!)
      this.scene.stop()
    })
  }

  private failure(): void {
    this.sound.play('sfx-dredge-fail', { volume: 0.6 })

    this.result = { success: false }
    this.showResult(false)

    this.time.delayedCall(2000, () => {
      this.onComplete(this.result!)
      this.scene.stop()
    })
  }

  private missedTarget(): void {
    // Player didn't press space in time
    this.isSweeping = false
    this.isComplete = true

    this.result = { success: false }
    this.showResult(false, null, 'SONAR SWEEP COMPLETE — NO TARGET ACQUIRED')

    this.time.delayedCall(2000, () => {
      this.onComplete(this.result!)
      this.scene.stop()
    })
  }

  private forfeit(): void {
    this.isComplete = true
    this.result = { success: false }
    this.showResult(false, null, 'DREDGE ABANDONED')

    this.time.delayedCall(1000, () => {
      this.onComplete(this.result!)
      this.scene.stop()
    })
  }

  private generateLoot(): any {
    // Loot table based on zone, depth, and player clout
    const zoneLootTables: Record<string, any[]> = {
      shallows: [
        { id: 'soggy-visor', name: 'Soggy Tourist Visor', tier: 'noob', weight: 40, stats: { clout_bonus: 1 } },
        { id: 'plastic-horns', name: 'Plastic Viking Horns', tier: 'noob', weight: 30, stats: { clout_bonus: 1 } },
        { id: 'wet-cardboard', name: 'Wet Cardboard Crown', tier: 'noob', weight: 20, stats: { clout_bonus: 1 } },
        { id: 'wool-beanie', name: 'Wool Beanie', tier: 'common', weight: 8, stats: { clout_bonus: 2, dredge_luck: 0.02 } },
        { id: 'fisherman-cap', name: 'Fisherman\'s Cap', tier: 'common', weight: 5, stats: { clout_bonus: 2, dredge_luck: 0.03 } },
        { id: 'kelp-crown', name: 'Kelp Crown', tier: 'common', weight: 3, stats: { clout_bonus: 3, craft_speed: 0.05 } },
      ],
      standard: [
        { id: 'wool-beanie', name: 'Wool Beanie', tier: 'common', weight: 30, stats: { clout_bonus: 2, dredge_luck: 0.02 } },
        { id: 'fisherman-cap', name: 'Fisherman\'s Cap', tier: 'common', weight: 25, stats: { clout_bonus: 2, dredge_luck: 0.03 } },
        { id: 'kelp-crown', name: 'Kelp Crown', tier: 'common', weight: 15, stats: { clout_bonus: 3, craft_speed: 0.05 } },
        { id: 'kelp-top-hat', name: 'Kelp-Woven Top Hat', tier: 'uncommon', weight: 12, stats: { clout_bonus: 10, dredge_luck: 0.05 } },
        { id: 'sub-captain-cap', name: 'Submarine Officer\'s Cap', tier: 'uncommon', weight: 8, stats: { clout_bonus: 12, market_fee_reduction: 0.02 } },
        { id: 'coral-tiara', name: 'Coral Tiara', tier: 'uncommon', weight: 5, stats: { clout_bonus: 15, craft_speed: 0.1 } },
        { id: 'admiral-bicorn', name: 'Sunken Admiral\'s Bicorn', tier: 'rare', weight: 2, stats: { clout_bonus: 50, dredge_luck: 0.1 } },
      ],
      deep: [
        { id: 'kelp-top-hat', name: 'Kelp-Woven Top Hat', tier: 'uncommon', weight: 30, stats: { clout_bonus: 10, dredge_luck: 0.05 } },
        { id: 'sub-captain-cap', name: 'Submarine Officer\'s Cap', tier: 'uncommon', weight: 20, stats: { clout_bonus: 12, market_fee_reduction: 0.02 } },
        { id: 'coral-tiara', name: 'Coral Tiara', tier: 'uncommon', weight: 15, stats: { clout_bonus: 15, craft_speed: 0.1 } },
        { id: 'admiral-bicorn', name: 'Sunken Admiral\'s Bicorn', tier: 'rare', weight: 15, stats: { clout_bonus: 50, dredge_luck: 0.1 } },
        { id: 'pearl-fedora', name: 'Pearl-Studded Fedora', tier: 'rare', weight: 10, stats: { clout_bonus: 60, market_fee_reduction: 0.05 } },
        { id: 'seaweed-sombrero', name: 'Enchanted Seaweed Sombrero', tier: 'rare', weight: 5, stats: { clout_bonus: 75, craft_speed: 0.2 } },
        { id: 'plundered-captain-cap', name: 'Plundered Captain\'s Cap', tier: 'epic', weight: 2, stats: { clout_bonus: 200, dredge_luck: 0.15 } },
      ],
      trench: [
        { id: 'admiral-bicorn', name: 'Sunken Admiral\'s Bicorn', tier: 'rare', weight: 25, stats: { clout_bonus: 50, dredge_luck: 0.1 } },
        { id: 'pearl-fedora', name: 'Pearl-Studded Fedora', tier: 'rare', weight: 20, stats: { clout_bonus: 60, market_fee_reduction: 0.05 } },
        { id: 'seaweed-sombrero', name: 'Enchanted Seaweed Sombrero', tier: 'rare', weight: 15, stats: { clout_bonus: 75, craft_speed: 0.2 } },
        { id: 'plundered-captain-cap', name: 'Plundered Captain\'s Cap', tier: 'epic', weight: 15, stats: { clout_bonus: 200, dredge_luck: 0.15 } },
        { id: 'kraken-ink-stetson', name: 'Kraken Ink Stetson', tier: 'epic', weight: 10, stats: { clout_bonus: 250, market_fee_reduction: 0.1 } },
        { id: 'abyssal-crown', name: 'Abyssal Crown', tier: 'epic', weight: 5, stats: { clout_bonus: 300, craft_speed: 0.3 } },
        { id: 'surgeons-photograph', name: '1934 Surgeon\'s Photograph', tier: 'legendary', weight: 1, stats: { clout_bonus: 1000, dredge_luck: 0.25, market_fee_reduction: 0.2 } },
      ],
      abyssal: [
        { id: 'plundered-captain-cap', name: 'Plundered Captain\'s Cap', tier: 'epic', weight: 25, stats: { clout_bonus: 200, dredge_luck: 0.15 } },
        { id: 'kraken-ink-stetson', name: 'Kraken Ink Stetson', tier: 'epic', weight: 20, stats: { clout_bonus: 250, market_fee_reduction: 0.1 } },
        { id: 'abyssal-crown', name: 'Abyssal Crown', tier: 'epic', weight: 15, stats: { clout_bonus: 300, craft_speed: 0.3 } },
        { id: 'surgeons-photograph', name: '1934 Surgeon\'s Photograph', tier: 'legendary', weight: 8, stats: { clout_bonus: 1000, dredge_luck: 0.25 } },
        { id: 'neptunes-trident-helm', name: 'Neptune\'s Trident Helm', tier: 'legendary', weight: 3, stats: { clout_bonus: 1500, dredge_luck: 0.3, craft_speed: 0.4 } },
        { id: 'nessies-crown', name: 'Nessie\'s Lost Crown', tier: 'mythic', weight: 0.1, stats: { clout_bonus: 5000, dredge_luck: 0.5, craft_speed: 0.5, market_fee_reduction: 0.5 } },
      ],
    }

    const table = zoneLootTables[this.spot.zone] || zoneLootTables.shallows

    // Weighted random selection
    const totalWeight = table.reduce((sum, item) => sum + item.weight, 0)
    let roll = PhaserMath.FloatBetween(0, totalWeight)

    for (const item of table) {
      roll -= item.weight
      if (roll <= 0) return { ...item, description: this.getItemDescription(item) }
    }

    return table[0]
  }

  private getItemDescription(item: any): string {
    const descriptions: Record<string, string> = {
      'noob': 'A sodden reminder that everyone starts somewhere.',
      'common': 'Functional headwear for the aspiring dredger.',
      'uncommon': 'Crafted with care from the Loch\'s bounty.',
      'rare': 'A treasure from the deep, coveted by many.',
      'epic': 'Legendary craftsmanship, whispered about in taverns.',
      'legendary': 'History made manifest. One of a kind.',
      'mythic': 'The Monster\'s own regalia. Reality bends.',
    }
    return descriptions[item.tier] || 'A curious find from the depths.'
  }

  private showResult(success: boolean, loot?: any, customMessage?: string): void {
    this.resultContainer.setVisible(true)
    this.resultContainer.removeAll()

    const container = this.add.container(0, 0)
    this.resultContainer.add(container)

    // Background
    const bg = this.add.graphics()
    bg.fillStyle(0x0a0a12, 0.98)
    bg.fillRoundedRect(-300, -200, 600, 400, 16)
    bg.lineStyle(4, success ? 0x00ff88 : 0xf44336, 1)
    bg.strokeRoundedRect(-300, -200, 600, 400, 16)
    container.add(bg)

    if (success && loot) {
      // Success animation
      const glow = this.add.image(0, -80, `ui-rarity-glow-${this.getTierIndex(loot.tier)}`)
        .setScale(3)
        .setBlendMode('ADD')
      container.add(glow)

      this.tweens.add({
        targets: glow,
        scale: 4,
        alpha: 0.3,
        duration: 1500,
        ease: 'Sine.easeInOut',
        yoyo: true,
        repeat: -1,
      })

      // Hat sprite
      const hat = this.add.image(0, -80, `hat-${loot.id}`)
        .setScale(3)
      container.add(hat)

      this.tweens.add({
        targets: hat,
        angle: 360,
        duration: 4000,
        ease: 'Linear',
        repeat: -1,
      })

      // Name
      container.add(this.add.bitmapText(0, -10, 'press-start', loot.name, 24)
        .setOrigin(0.5)
        .setTint(this.getTierColor(loot.tier)))

      // Tier
      container.add(this.add.bitmapText(0, 35, 'press-start-small', loot.tier.toUpperCase(), 16)
        .setOrigin(0.5)
        .setTint(this.getTierColor(loot.tier)))

      // Description
      container.add(this.add.bitmapText(0, 70, 'press-start-small', loot.description, 10)
        .setOrigin(0.5)
        .setTint(0xe8d5c4)
        .setMaxWidth(500))

      // Stats
      if (loot.stats) {
        let y = 110
        Object.entries(loot.stats).forEach(([stat, value]) => {
          const formattedStat = stat.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
          container.add(this.add.bitmapText(0, y, 'press-start-small', `+${value} ${formattedStat}`, 10)
            .setOrigin(0.5)
            .setTint(0x00ff88))
          y += 22
        })
      }

      // Clout gain
      const cloutGain = this.calculateCloutGain(loot.tier)
      container.add(this.add.bitmapText(0, 170, 'press-start', `+${cloutGain} CLOUT`, 20)
        .setOrigin(0.5)
        .setTint(0x00ff88))

    } else {
      // Failure
      container.add(this.add.bitmapText(0, -60, 'press-start', customMessage || 'TARGET MISSED', 24)
        .setOrigin(0.5)
        .setTint(0xf44336))

      container.add(this.add.bitmapText(0, -10, 'press-start-small', 'The depths keep their secrets...', 12)
        .setOrigin(0.5)
        .setTint(0x888888))

      // Show target zone for learning
      container.add(this.add.bitmapText(0, 40, 'press-start-small', `Target Angle: ${PhaserMath.RadToDeg(this.targetZone.start).toFixed(1)}° - ${PhaserMath.RadToDeg(this.targetZone.end).toFixed(1)}°`, 10)
        .setOrigin(0.5)
        .setTint(0xffd700))

      container.add(this.add.bitmapText(0, 70, 'press-start-small', `Your Stop: ${PhaserMath.RadToDeg(this.sweepAngle).toFixed(1)}°`, 10)
        .setOrigin(0.5)
        .setTint(0xe8d5c4))
    }

    // Animate in
    this.resultContainer.setScale(0)
    this.tweens.add({
      targets: this.resultContainer,
      scale: 1,
      duration: 400,
      ease: 'Back.out',
    })

    // Instruction to continue
    this.time.delayedCall(1500, () => {
      const continueText = this.add.bitmapText(0, 220, 'press-start-small', 'RETURNING TO LOCH...', 10)
        .setOrigin(0.5)
        .setTint(0x666666)
      this.resultContainer.add(continueText)

      this.tweens.add({
        targets: continueText,
        alpha: { from: 0, to: 1 },
        duration: 500,
      })
    })
  }

  private getTierColor(tier: string): number {
    const colors: Record<string, number> = {
      noob: 0x888888,
      common: 0xffffff,
      uncommon: 0x4caf50,
      rare: 0x2196f3,
      epic: 0x9c27b0,
      legendary: 0xffd700,
      mythic: 0xff00ff,
    }
    return colors[tier] || 0xffffff
  }

  private getTierIndex(tier: string): number {
    const indices: Record<string, number> = {
      noob: 0,
      common: 1,
      uncommon: 2,
      rare: 3,
      epic: 4,
      legendary: 5,
      mythic: 6,
    }
    return indices[tier] || 0
  }

  private calculateCloutGain(tier: string): number {
    const base: Record<string, number> = {
      noob: 1,
      common: 5,
      uncommon: 25,
      rare: 100,
      epic: 500,
      legendary: 2500,
      mythic: 10000,
    }
    return base[tier] || 1
  }

  private getZoneColor(zone: string): number {
    const colors: Record<string, number> = {
      shallows: 0x4caf50,
      standard: 0x2196f3,
      deep: 0x9c27b0,
      trench: 0xff9800,
      abyssal: 0xf44336,
    }
    return colors[zone] || 0xffffff
  }

  private playAudio(): void {
    this.ambientLoop = this.sound.add('music-deep', { loop: true, volume: 0.2 })
    this.ambientLoop.play()

    this.sonarLoop = this.sound.add('sfx-water-ambient', { loop: true, volume: 0.15 })
    this.sonarLoop.play()
  }

  shutdown(): void {
    this.ambientLoop?.stop()
    this.sonarLoop?.stop()
    this.tweens.killAll()
    this.time.removeAllEvents()
  }
}