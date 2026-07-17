import { Scene } from 'phaser'

export class BootScene extends Scene {
  constructor() {
    super({ key: 'BootScene', active: true })
  }

  preload(): void {
    // Load minimal assets needed for preloader
    this.load.setPath('assets/')
    
    // Loading screen assets
    this.load.image('loading-bg', 'ui/loading_bg.png')
    this.load.image('progress-bar-bg', 'ui/progress_bg.png')
    this.load.image('progress-bar-fill', 'ui/progress_fill.png')
    this.load.image('nessie-silhouette', 'ui/nessie_silhouette.png')
    
    // Font loading (bitmap font for retro feel)
    this.load.bitmapFont('press-start', 'fonts/press_start.png', 'fonts/press_start.xml')
    this.load.bitmapFont('press-start-small', 'fonts/press_start_small.png', 'fonts/press_start_small.xml')
  }

  create(): void {
    // Initialize game systems
    this.registry.set('playerData', null)
    this.registry.set('marketData', {})
    this.registry.set('inventory', [])
    this.registry.set('clout', 0)
    
    // Audio context initialization (requires user interaction)
    this.sound.pauseOnBlur = false
    
    // Start preloader
    this.scene.start('PreloadScene')
  }
}