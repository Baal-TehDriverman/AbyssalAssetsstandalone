import { Scene, GameObjects, Math as PhaserMath } from 'phaser'

interface MarketItem {
  id: string
  name: string
  tier: string
  price: number
  quantity: number
  sellerId?: string
  sellerName?: string
  stats: Record<string, number>
  visual: {
    sprite: string
    particleEffect?: string
    shader?: string
  }
  provenance: {
    creatorId?: string
    creationTimestamp: number
    tradeHistory: TradeRecord[]
  }
  metadata: {
    discontinued: boolean
    limitedEdition: boolean
    eventSource?: string
    serialNumber?: number
  }
}

interface TradeRecord {
  from: string
  to: string
  price: number
  timestamp: number
}

interface OrderBookEntry {
  price: number
  quantity: number
  orders: number
  isBuy: boolean
}

interface PlayerMarketData {
  abyssalCoins: number
  inventory: MarketItem[]
  activeListings: MarketListing[]
  tradeHistory: TradeRecord[]
}

interface MarketListing {
  id: string
  itemId: string
  price: number
  quantity: number
  timestamp: number
  expiresAt: number
}

const TIER_ORDER = ['noob', 'common', 'uncommon', 'rare', 'epic', 'legendary', 'mythic']
const TIER_COLORS: Record<string, number> = {
  noob: 0x888888,
  common: 0xffffff,
  uncommon: 0x4caf50,
  rare: 0x2196f3,
  epic: 0x9c27b0,
  legendary: 0xffd700,
  mythic: 0xff00ff,
}

export class MarketScene extends Scene {
  // Market data
  private marketItems: MarketItem[] = []
  private orderBook: { buys: OrderBookEntry[]; sells: OrderBookEntry[] } = { buys: [], sells: [] }
  private priceHistory: Map<string, { time: number; price: number }[]> = new Map()
  private playerData!: PlayerMarketData
  private selectedItem: MarketItem | null = null
  private currentTab: 'browse' | 'sell' | 'buy' | 'vault' | 'history' = 'browse'
  private filterTier: string = 'all'
  private sortBy: 'price_asc' | 'price_desc' | 'recent' | 'tier' = 'price_asc'
  private searchQuery: string = ''

  // UI Containers
  private mainContainer!: GameObjects.Container
  private headerContainer!: GameObjects.Container
  private tabContainer!: GameObjects.Container
  private marketContentContainer!: GameObjects.Container
  private sidebarContainer!: GameObjects.Container
  private detailContainer!: GameObjects.Container
  private footerContainer!: GameObjects.Container

  // UI Elements
  private itemList!: GameObjects.Container
  private itemListMask!: GameObjects.Graphics
  private orderBookContainer!: GameObjects.Container
  private priceChartContainer!: GameObjects.Container
  private playerCoinsText!: GameObjects.BitmapText
  private playerCloutText!: GameObjects.BitmapText
  private searchInput!: HTMLInputElement
  private notifications: GameObjects.Container[] = []

  // Animation/State
  private refreshTimer: Phaser.Time.TimerEvent | null = null

  constructor() {
    super({ key: 'MarketScene' })
  }

  init(data: { playerData?: PlayerMarketData }): void {
    this.playerData = data.playerData || {
      abyssalCoins: 10000,
      inventory: this.generateMockInventory(),
      activeListings: [],
      tradeHistory: [],
    }

    // Generate mock market data
    this.generateMockMarket()
    this.generateMockOrderBook()
    this.generateMockPriceHistory()
  }

  private generateMockInventory(): MarketItem[] {
    const items: MarketItem[] = []
    const templates = this.getItemTemplates()

    // Give player a few starter items
    const starterItems = ['wool-beanie', 'fisherman-cap', 'kelp-crown', 'kelp-top-hat']
    starterItems.forEach(id => {
      const t = templates.find(x => x.id === id)
      if (t) items.push(this.createItemInstance(t))
    })

    return items
  }

  private getItemTemplates(): any[] {
    return [
      // Noob
      { id: 'soggy-visor', name: 'Soggy Tourist Visor', tier: 'noob', basePrice: 5, stats: { clout_bonus: 1 }, desc: 'A sodden reminder that everyone starts somewhere.' },
      { id: 'plastic-horns', name: 'Plastic Viking Horns', tier: 'noob', basePrice: 8, stats: { clout_bonus: 1 }, desc: 'Cheap costume horns. Barely intimidating.' },
      { id: 'wet-cardboard', name: 'Wet Cardboard Crown', tier: 'noob', basePrice: 3, stats: { clout_bonus: 1 }, desc: 'Regal... if you squint. And ignore the sogginess.' },

      // Common
      { id: 'wool-beanie', name: 'Wool Beanie', tier: 'common', basePrice: 50, stats: { clout_bonus: 2, dredge_luck: 0.02 }, desc: 'Warm, practical, distinctly unmagical.' },
      { id: 'fisherman-cap', name: 'Fisherman\'s Cap', tier: 'common', basePrice: 75, stats: { clout_bonus: 2, dredge_luck: 0.03 }, desc: 'Classic headwear for the working angler.' },
      { id: 'kelp-crown', name: 'Kelp Crown', tier: 'common', basePrice: 120, stats: { clout_bonus: 3, craft_speed: 0.05 }, desc: 'Woven from Loch kelp. Surprisingly durable.' },

      // Uncommon
      { id: 'kelp-top-hat', name: 'Kelp-Woven Top Hat', tier: 'uncommon', basePrice: 1500, stats: { clout_bonus: 10, dredge_luck: 0.05 }, desc: 'Tall, distinguished, faintly smells of brine.' },
      { id: 'sub-captain-cap', name: 'Submarine Officer\'s Cap', tier: 'uncommon', basePrice: 2200, stats: { clout_bonus: 12, market_fee_reduction: 0.02 }, desc: 'Salvaged from a U-boat. Still has the insignia.' },
      { id: 'coral-tiara', name: 'Coral Tiara', tier: 'uncommon', basePrice: 3500, stats: { clout_bonus: 15, craft_speed: 0.1 }, desc: 'Living coral, gently pulsing. Don\'t feed it.' },

      // Rare
      { id: 'admiral-bicorn', name: 'Sunken Admiral\'s Bicorn', tier: 'rare', basePrice: 15000, stats: { clout_bonus: 50, dredge_luck: 0.1 }, desc: 'Worn by Admiral Thalassos at the Battle of the Trench.' },
      { id: 'pearl-fedora', name: 'Pearl-Studded Fedora', tier: 'rare', basePrice: 25000, stats: { clout_bonus: 60, market_fee_reduction: 0.05 }, desc: 'Each pearl harvested from a giant clam. Ouch.' },
      { id: 'seaweed-sombrero', name: 'Enchanted Seaweed Sombrero', tier: 'rare', basePrice: 35000, stats: { clout_bonus: 75, craft_speed: 0.2 }, desc: 'Wide brim provides shade. And +5 mystery.' },

      // Epic
      { id: 'plundered-captain-cap', name: 'Plundered Captain\'s Cap', tier: 'epic', basePrice: 150000, stats: { clout_bonus: 200, dredge_luck: 0.15 }, desc: 'Taken from the notorious Captain Blackfin.' },
      { id: 'kraken-ink-stetson', name: 'Kraken Ink Stetson', tier: 'epic', basePrice: 250000, stats: { clout_bonus: 250, market_fee_reduction: 0.1 }, desc: 'Dyed with genuine Kraken ink. Never fades.' },
      { id: 'abyssal-crown', name: 'Abyssal Crown', tier: 'epic', basePrice: 500000, stats: { clout_bonus: 300, craft_speed: 0.3 }, desc: 'Forged at the Hydrothermal Vent Forge. Radiates pressure.' },

      // Legendary
      { id: 'surgeons-photograph', name: '1934 Surgeon\'s Photograph', tier: 'legendary', basePrice: 5000000, stats: { clout_bonus: 1000, dredge_luck: 0.25, market_fee_reduction: 0.2 }, desc: 'The hat FROM the photo. Discontinued. #47/100', metadata: { discontinued: true, limitedEdition: true, serialNumber: 47 } },
      { id: 'neptunes-trident-helm', name: 'Neptune\'s Trident Helm', tier: 'legendary', basePrice: 15000000, stats: { clout_bonus: 1500, dredge_luck: 0.3, craft_speed: 0.4 }, desc: 'Blessed by the Sea God himself. Or so they say.' },

      // Mythic
      { id: 'nessies-crown', name: 'Nessie\'s Lost Crown', tier: 'mythic', basePrice: 0, stats: { clout_bonus: 5000, dredge_luck: 0.5, craft_speed: 0.5, market_fee_reduction: 0.5 }, desc: 'The Monster\'s own regalia. Reality bends.', metadata: { eventSource: 'World First' } },
      { id: 'original-monster-hat', name: 'Original 1933 Monster Hunter\'s Hat', tier: 'mythic', basePrice: 0, stats: { clout_bonus: 3000, dredge_luck: 0.4, market_fee_reduction: 0.3 }, desc: 'Worn by the first to photograph the beast.', metadata: { eventSource: 'GM Event' } },
    ]
  }

  private createItemInstance(template: any): MarketItem {
    return {
      id: template.id,
      name: template.name,
      tier: template.tier,
      price: template.basePrice + PhaserMath.Between(-Math.floor(template.basePrice * 0.1), Math.floor(template.basePrice * 0.1)),
      quantity: 1,
      stats: { ...template.stats },
      visual: {
        sprite: `hat-${template.id}`,
        particleEffect: template.tier !== 'noob' && template.tier !== 'common' ? `particle-rarity-${template.tier}` : undefined,
        shader: template.tier === 'mythic' ? 'shader-mythic-distort' : template.tier === 'legendary' || template.tier === 'epic' ? 'shader-rarity-glow' : undefined,
      },
      provenance: {
        creatorId: template.metadata?.creatorId,
        creationTimestamp: Date.now() - PhaserMath.Between(0, 31536000000),
        tradeHistory: [],
      },
      metadata: {
        discontinued: template.metadata?.discontinued || false,
        limitedEdition: template.metadata?.limitedEdition || false,
        eventSource: template.metadata?.eventSource,
        serialNumber: template.metadata?.serialNumber,
      },
    }
  }

  private generateMockMarket(): void {
    const templates = this.getItemTemplates()
    this.marketItems = []

    templates.forEach(template => {
      // Don't show mythic items in regular market (vault only)
      if (template.tier === 'mythic') return

      // Number of listings per item varies by tier
      let listingCount: number
      switch (template.tier) {
        case 'noob': listingCount = PhaserMath.Between(20, 50); break
        case 'common': listingCount = PhaserMath.Between(10, 30); break
        case 'uncommon': listingCount = PhaserMath.Between(3, 10); break
        case 'rare': listingCount = PhaserMath.Between(1, 5); break
        case 'epic': listingCount = PhaserMath.Between(1, 3); break
        case 'legendary': listingCount = PhaserMath.Between(0, 1); break
        default: listingCount = 1
      }

      for (let i = 0; i < listingCount; i++) {
        const item = this.createItemInstance(template)
        // Vary prices slightly
        item.price = Math.floor(item.price * PhaserMath.FloatBetween(0.9, 1.3))
        item.sellerId = `seller_${PhaserMath.Between(1000, 9999)}`
        item.sellerName = `Angler_${PhaserMath.Between(100, 999)}`
        this.marketItems.push(item)
      }
    })

    // Sort by price initially
    this.sortItems()
  }

  private generateMockOrderBook(): void {
    // Generate buy orders (bids)
    this.orderBook.buys = []
    this.marketItems.slice(0, 20).forEach(item => {
      const bidCount = PhaserMath.Between(1, 5)
      for (let i = 0; i < bidCount; i++) {
        this.orderBook.buys.push({
          price: Math.floor(item.price * PhaserMath.FloatBetween(0.7, 0.95)),
          quantity: PhaserMath.Between(1, 3),
          orders: PhaserMath.Between(1, 3),
          isBuy: true,
        })
      }
    })
    this.orderBook.buys.sort((a, b) => b.price - a.price) // Highest bid first

    // Generate sell orders (asks)
    this.orderBook.sells = []
    this.marketItems.slice(0, 20).forEach(item => {
      const askCount = PhaserMath.Between(1, 5)
      for (let i = 0; i < askCount; i++) {
        this.orderBook.sells.push({
          price: Math.floor(item.price * PhaserMath.FloatBetween(1.05, 1.3)),
          quantity: PhaserMath.Between(1, 3),
          orders: PhaserMath.Between(1, 3),
          isBuy: false,
        })
      }
    })
    this.orderBook.sells.sort((a, b) => a.price - b.price) // Lowest ask first
  }

  private generateMockPriceHistory(): void {
    this.marketItems.slice(0, 10).forEach(item => {
      const history: { time: number; price: number }[] = []
      let price = item.price
      const now = Date.now()

      for (let i = 30; i >= 0; i--) {
        const dayMs = 86400000
        const variation = PhaserMath.FloatBetween(-0.1, 0.1)
        price = Math.max(1, Math.floor(price * (1 + variation)))
        history.push({ time: now - i * dayMs, price })
      }
      this.priceHistory.set(item.id, history)
    })
  }

  create(): void {
    // === BACKGROUND ===
    this.createBackground()

    // === MAIN LAYOUT ===
    this.createLayout()

    // === HEADER ===
    this.createHeader()

    // === TABS ===
    this.createTabs()

    // === CONTENT AREA ===
    this.createContentArea()

    // === SIDEBAR (ORDER BOOK / PRICE CHART) ===
    this.createSidebar()

    // === DETAIL PANEL ===
    this.createDetailPanel()

    // === FOOTER ===
    this.createFooter()

    // === INPUT ===
    this.setupInput()

    // === NETWORKING (placeholder) ===
    this.setupNetworking()

    // === AUTO REFRESH ===
    this.startAutoRefresh()

    // === RESIZE ===
    this.scale.on('resize', this.handleResize, this)

    // Focus search input
    this.time.delayedCall(100, () => this.searchInput?.focus())
  }

  private createBackground(): void {
    const { width, height } = this.scale

    // Deep water gradient
    const bg = this.add.graphics()
    bg.fillGradientStyle(0x051020, 0x051020, 0x0a1a30, 0x0a1a30, 1)
    bg.fillRect(0, 0, width, height)
    bg.setDepth(-10)

    // Subtle market grid pattern
    const grid = this.add.graphics()
    grid.lineStyle(1, 0x0a2a40, 0.3)
    for (let i = 0; i < width; i += 60) {
      grid.lineBetween(i, 0, i, height)
    }
    for (let i = 0; i < height; i += 60) {
      grid.lineBetween(0, i, width, i)
    }
    grid.setDepth(-9)

    // Ambient particles (gold dust, bubbles)
    this.add.particles(0, 0, 'particle-sparkle', {
      x: { min: 0, max: width },
      y: { min: 0, max: height },
      lifespan: { min: 8000, max: 20000 },
      speedX: { min: -5, max: 5 },
      speedY: { min: -15, max: -5 },
      scale: { start: 0.3, end: 0 },
      alpha: { start: 0.4, end: 0 },
      frequency: 500,
      blendMode: 'ADD',
    }).setDepth(-8)

    this.add.particles(0, 0, 'particle-bubble', {
      x: { min: 0, max: width },
      y: height + 50,
      lifespan: { min: 10000, max: 20000 },
      speedY: { min: -30, max: -10 },
      speedX: { min: -15, max: 15 },
      scale: { start: 0.4, end: 0 },
      alpha: { start: 0.2, end: 0 },
      frequency: 300,
      blendMode: 'ADD',
    }).setDepth(-8)
  }

  private createLayout(): void {
    this.mainContainer = this.add.container(0, 0).setDepth(10)

    // Layout dimensions
    const { width, height } = this.scale
    this.headerHeight = 80
    this.tabHeight = 50
    this.footerHeight = 60
    this.sidebarWidth = 320
    this.detailWidth = 380

    this.contentX = 20
    this.contentY = this.headerHeight + this.tabHeight + 10
    this.contentWidth = width - this.sidebarWidth - this.detailWidth - 60
    this.contentHeight = height - this.contentY - this.footerHeight - 20

    this.sidebarX = this.contentX + this.contentWidth + 20
    this.detailX = this.sidebarX + this.sidebarWidth + 20
  }

  private headerHeight: number = 80
  private tabHeight: number = 50
  private footerHeight: number = 60
  private sidebarWidth: number = 320
  private detailWidth: number = 380
  private contentX: number = 20
  private contentY: number = 140
  private contentWidth: number = 600
  private contentHeight: number = 600
  private sidebarX: number = 640
  private detailX: number = 980

  private createHeader(): void {
    const { width } = this.scale

    this.headerContainer = this.add.container(0, 0).setDepth(20)
    this.mainContainer.add(this.headerContainer)

    // Background
    const bg = this.add.graphics()
    bg.fillStyle(0x0a0a12, 0.95)
    bg.fillRect(0, 0, width, this.headerHeight)
    bg.lineStyle(2, 0xffd700, 0.5)
    bg.lineBetween(0, this.headerHeight, width, this.headerHeight)
    this.headerContainer.add(bg)

    // Title
    this.headerContainer.add(this.add.bitmapText(30, 20, 'press-start', 'THE LOCH EXCHANGE', 22)
      .setTint(0xffd700))

    // Subtitle
    this.headerContainer.add(this.add.bitmapText(30, 52, 'press-start-small', 'CENTRAL LIMIT ORDER BOOK — REAL-TIME', 10)
      .setTint(0x00ff88))

    // Player coins
    this.playerCoinsText = this.add.bitmapText(width - 30, 20, 'press-start', this.formatCoins(this.playerData.abyssalCoins), 18)
      .setOrigin(1, 0)
      .setTint(0xffd700)
    this.headerContainer.add(this.playerCoinsText)

    this.headerContainer.add(this.add.bitmapText(width - 30, 50, 'press-start-small', 'ABYSSAL COINS', 8)
      .setOrigin(1, 0)
      .setTint(0x888888))

    // Clout
    this.playerCloutText = this.add.bitmapText(width - 280, 20, 'press-start', `CLOUT: ${this.formatNumber(this.playerData.inventory.reduce((s, i) => s + (i.stats.clout_bonus || 0), 0))}`, 14)
      .setOrigin(1, 0)
      .setTint(0x00ff88)
    this.headerContainer.add(this.playerCloutText)

    // Search input (HTML overlay)
    this.createSearchInput(width)
  }

  private createSearchInput(_width: number): void {
    // Create HTML input for search
    const input = document.createElement('input')
    input.type = 'text'
    input.placeholder = 'Search hats...'
    input.style.cssText = `
      position: fixed;
      left: ${300}px;
      top: ${20}px;
      width: ${300}px;
      height: 36px;
      background: #1a1a2e;
      border: 2px solid #333;
      border-radius: 8px;
      color: #e8d5c4;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 14px;
      padding: 0 12px;
      outline: none;
      z-index: 1000;
    `
    input.addEventListener('focus', () => input.style.borderColor = '#ffd700')
    input.addEventListener('blur', () => input.style.borderColor = '#333')
    input.addEventListener('input', (e) => {
      this.searchQuery = (e.target as HTMLInputElement).value.toLowerCase()
      this.filterAndSortItems()
    })

    document.body.appendChild(input)
    this.searchInput = input
  }

  private createTabs(): void {
    const { width } = this.scale
    const tabY = this.headerHeight

    this.tabContainer = this.add.container(0, tabY).setDepth(20)
    this.mainContainer.add(this.tabContainer)

    // Background
    const bg = this.add.graphics()
    bg.fillStyle(0x0a0a12, 0.95)
    bg.fillRect(0, 0, width, this.tabHeight)
    bg.lineStyle(1, 0x222222, 1)
    bg.lineBetween(0, this.tabHeight, width, this.tabHeight)
    this.tabContainer.add(bg)

    const tabs = [
      { id: 'browse', label: 'BROWSE', icon: '🎩' },
      { id: 'sell', label: 'SELL', icon: '💰' },
      { id: 'buy', label: 'BUY ORDERS', icon: '📋' },
      { id: 'vault', label: 'THE VAULT', icon: '🔒' },
      { id: 'history', label: 'HISTORY', icon: '📈' },
    ]

    const tabWidth = 180
    tabs.forEach((tab, i) => {
      const x = 40 + i * tabWidth
      const container = this.add.container(x, this.tabHeight / 2)

      const bgTab = this.add.graphics()
      bgTab.fillStyle(i === 0 ? 0x1a1a2e : 0x0a0a12, 1)
      bgTab.fillRoundedRect(-tabWidth / 2 + 10, -20, tabWidth - 20, 40, 8)
      if (i === 0) {
        bgTab.lineStyle(2, 0xffd700, 1)
        bgTab.strokeRoundedRect(-tabWidth / 2 + 10, -20, tabWidth - 20, 40, 8)
      }
      container.add(bgTab)
      container.setData('bg', bgTab)

      const text = this.add.bitmapText(0, 0, 'press-start-small', `${tab.icon} ${tab.label}`, 12)
        .setOrigin(0.5)
        .setTint(i === 0 ? 0xffd700 : 0x888888)
      container.add(text)
      container.setData('text', text)

      container.setSize(tabWidth - 20, 40)
      container.setInteractive(new Phaser.Geom.Rectangle(-tabWidth / 2 + 10, -20, tabWidth - 20, 40), Phaser.Geom.Rectangle.Contains)

      container.on('pointerover', () => {
        if (this.currentTab !== tab.id) {
          bgTab.clear().fillStyle(0x1a1a2e, 1).fillRoundedRect(-tabWidth / 2 + 10, -20, tabWidth - 20, 40, 8)
          text.setTint(0xe8d5c4)
        }
      })

      container.on('pointerout', () => {
        if (this.currentTab !== tab.id) {
          bgTab.clear().fillStyle(0x0a0a12, 1).fillRoundedRect(-tabWidth / 2 + 10, -20, tabWidth - 20, 40, 8)
          text.setTint(0x888888)
        }
      })

      container.on('pointerdown', () => this.switchTab(tab.id))

      container.setData('tabId', tab.id)
      this.tabContainer.add(container)
    })
  }

  private switchTab(tabId: string): void {
    const validTabs: ('browse' | 'sell' | 'buy' | 'vault' | 'history')[] = ['browse', 'sell', 'buy', 'vault', 'history']
    if (!validTabs.includes(tabId as any)) return

    this.currentTab = tabId as 'browse' | 'sell' | 'buy' | 'vault' | 'history'

    // Update tab visuals
    this.tabContainer.each((container: GameObjects.Container) => {
      const bg = container.getData('bg') as GameObjects.Graphics
      const text = container.getData('text') as GameObjects.BitmapText
      const id = container.getData('tabId') as string

      bg.clear()
      if (id === tabId) {
        bg.fillStyle(0x1a1a2e, 1)
        bg.fillRoundedRect(-80, -20, 160, 40, 8)
        bg.lineStyle(2, 0xffd700, 1)
        bg.strokeRoundedRect(-80, -20, 160, 40, 8)
        text.setTint(0xffd700)
      } else {
        bg.fillStyle(0x0a0a12, 1)
        bg.fillRoundedRect(-80, -20, 160, 40, 8)
        text.setTint(0x888888)
      }
    })

    // Refresh content
    this.refreshContent()
  }

  private createContentArea(): void {
    this.marketContentContainer = this.add.container(this.contentX, this.contentY).setDepth(15)
    this.mainContainer.add(this.marketContentContainer)

    // Background panel
    const bg = this.add.graphics()
    bg.fillStyle(0x0a0a12, 0.9)
    bg.fillRoundedRect(0, 0, this.contentWidth, this.contentHeight, 12)
    bg.lineStyle(1, 0x222222, 1)
    bg.strokeRoundedRect(0, 0, this.contentWidth, this.contentHeight, 12)
    this.marketContentContainer.add(bg)

    // Item list container (scrollable)
    this.itemList = this.add.container(10, 50).setDepth(16)
    this.marketContentContainer.add(this.itemList)

    // Mask for scrolling
    this.itemListMask = this.add.graphics()
    this.itemListMask.fillStyle(0xffffff, 1)
    this.itemListMask.fillRect(0, 0, this.contentWidth - 20, this.contentHeight - 70)
    this.itemList.setMask(new Phaser.Display.Masks.GeometryMask(this, this.itemListMask))

    // Scrollbar
    this.createScrollbar()

    // Tier filter chips
    this.createTierFilters()

    // Sort dropdown
    this.createSortDropdown()

    this.refreshContent()
  }

  private createTierFilters(): void {
    const tiers = ['all', 'noob', 'common', 'uncommon', 'rare', 'epic', 'legendary']
    let x = 10

    tiers.forEach(tier => {
      const container = this.add.container(x + 40, 25)
      const isActive = this.filterTier === tier

      const bg = this.add.graphics()
      bg.fillStyle(isActive ? TIER_COLORS[tier] : 0x1a1a2e, isActive ? 1 : 0.5)
      bg.fillRoundedRect(-35, -14, 70, 28, 14)
      if (isActive) bg.lineStyle(2, 0xffffff, 1).strokeRoundedRect(-35, -14, 70, 28, 14)
      container.add(bg)

      const label = tier === 'all' ? 'ALL' : tier.toUpperCase().slice(0, 4)
      const text = this.add.bitmapText(0, 0, 'press-start-small', label, 8)
        .setOrigin(0.5)
        .setTint(isActive ? 0x0a0a12 : 0xe8d5c4)
      container.add(text)

      container.setSize(70, 28)
      container.setInteractive(new Phaser.Geom.Rectangle(-35, -14, 70, 28), Phaser.Geom.Rectangle.Contains)

      container.on('pointerdown', () => {
        this.filterTier = tier
        this.refreshContent()
      })

      this.marketContentContainer.add(container)
      x += 80
    })
  }

  private createSortDropdown(): void {
    const x = this.contentWidth - 150
    const y = 25

    const container = this.add.container(x, y)
    this.marketContentContainer.add(container)

    const bg = this.add.graphics()
    bg.fillStyle(0x1a1a2e, 1)
    bg.fillRoundedRect(-100, -14, 200, 28, 14)
    bg.lineStyle(1, 0x333333, 1)
    bg.strokeRoundedRect(-100, -14, 200, 28, 14)
    container.add(bg)

    const sortLabels: Record<string, string> = {
      price_asc: '↑ PRICE',
      price_desc: '↓ PRICE',
      recent: '🕐 RECENT',
      tier: '🎩 TIER',
    }

    const text = this.add.bitmapText(0, 0, 'press-start-small', sortLabels[this.sortBy], 8)
      .setOrigin(0.5)
      .setTint(0xe8d5c4)
    container.add(text)
    container.setData('text', text)

    container.setSize(200, 28)
    container.setInteractive(new Phaser.Geom.Rectangle(-100, -14, 200, 28), Phaser.Geom.Rectangle.Contains)

    container.on('pointerdown', () => this.cycleSort())
  }

  private cycleSort(): void {
    const sorts: typeof this.sortBy[] = ['price_asc', 'price_desc', 'recent', 'tier']
    const currentIndex = sorts.indexOf(this.sortBy)
    this.sortBy = sorts[(currentIndex + 1) % sorts.length]
    this.sortItems()
    this.refreshContent()
  }

  private createScrollbar(): void {
    // Simple scrollbar on right side
    this.scrollbar = this.add.graphics()
    this.scrollbar.setDepth(17)
    this.scrollbar.fillStyle(0x333333, 1)
    this.scrollbar.fillRoundedRect(this.contentWidth - 12, 50, 8, this.contentHeight - 70, 4)
    this.marketContentContainer.add(this.scrollbar)

    // Scroll thumb
    this.scrollThumb = this.add.graphics()
    this.scrollThumb.setDepth(18)
    this.scrollThumb.fillStyle(0xffd700, 1)
    this.scrollThumb.fillRoundedRect(this.contentWidth - 12, 50, 8, 100, 4)
    this.marketContentContainer.add(this.scrollThumb)

    this.scrollOffset = 0
    this.maxScrollOffset = 0

    // Mouse wheel scroll
    this.input.on('wheel', (_pointer: any, _currentlyOver: any, _deltaX: number, deltaY: number) => {
      if (this.isPointerInContent(_pointer)) {
        this.scrollOffset = PhaserMath.Clamp(this.scrollOffset - deltaY * 2, 0, this.maxScrollOffset)
        this.updateScroll()
      }
    })
  }

  private scrollbar!: GameObjects.Graphics
  private scrollThumb!: GameObjects.Graphics
  private scrollOffset: number = 0
  private maxScrollOffset: number = 0

  private isPointerInContent(pointer: any): boolean {
    const worldPoint = this.marketContentContainer.getWorldTransformMatrix().transformPoint(pointer.x, pointer.y)
    return worldPoint.x >= this.contentX &&
           worldPoint.x <= this.contentX + this.contentWidth &&
           worldPoint.y >= this.contentY &&
           worldPoint.y <= this.contentY + this.contentHeight
  }

  private updateScroll(): void {
    this.itemList.setPosition(10, 50 - this.scrollOffset)
    const thumbHeight = Math.max(30, (this.contentHeight - 70) / Math.max(1, (this.maxScrollOffset + this.contentHeight - 70) / (this.contentHeight - 70)) * (this.contentHeight - 70))
    this.scrollThumb.clear()
    this.scrollThumb.fillStyle(0xffd700, 1)
    const thumbY = 50 + (this.scrollOffset / Math.max(1, this.maxScrollOffset)) * (this.contentHeight - 70 - thumbHeight)
    this.scrollThumb.fillRoundedRect(this.contentWidth - 12, thumbY, 8, thumbHeight, 4)
  }

  private createSidebar(): void {
    this.sidebarContainer = this.add.container(this.sidebarX, this.contentY).setDepth(15)
    this.mainContainer.add(this.sidebarContainer)

    // Background
    const bg = this.add.graphics()
    bg.fillStyle(0x0a0a12, 0.9)
    bg.fillRoundedRect(0, 0, this.sidebarWidth, this.contentHeight, 12)
    bg.lineStyle(1, 0x222222, 1)
    bg.strokeRoundedRect(0, 0, this.sidebarWidth, this.contentHeight, 12)
    this.sidebarContainer.add(bg)

    // Order Book Title
    this.sidebarContainer.add(this.add.bitmapText(this.sidebarWidth / 2, 20, 'press-start-small', 'ORDER BOOK', 12)
      .setOrigin(0.5)
      .setTint(0xffd700))

    // Order book container
    this.orderBookContainer = this.add.container(10, 50).setDepth(16)
    this.sidebarContainer.add(this.orderBookContainer)

    this.renderOrderBook()

    // Price Chart Title
    const chartY = 50 + 22 * 15 + 20
    this.sidebarContainer.add(this.add.bitmapText(this.sidebarWidth / 2, chartY, 'press-start-small', 'PRICE CHART (30D)', 12)
      .setOrigin(0.5)
      .setTint(0xffd700))

    // Price chart container
    this.priceChartContainer = this.add.container(10, chartY + 30).setDepth(16)
    this.sidebarContainer.add(this.priceChartContainer)

    this.renderPriceChart()
  }

  private renderOrderBook(): void {
    this.orderBookContainer.removeAll(true)

    // Headers
    const headerY = 0
    this.orderBookContainer.add(this.add.bitmapText(10, headerY, 'press-start-small', 'BIDS (BUY)', 8).setTint(0x4caf50))
    this.orderBookContainer.add(this.add.bitmapText(160, headerY, 'press-start-small', 'ASKS (SELL)', 8).setTint(0xf44336))

    // Column headers
    const colY = 20
    this.orderBookContainer.add(this.add.bitmapText(10, colY, 'press-start-small', 'PRICE', 7).setTint(0x888888))
    this.orderBookContainer.add(this.add.bitmapText(90, colY, 'press-start-small', 'QTY', 7).setTint(0x888888))
    this.orderBookContainer.add(this.add.bitmapText(160, colY, 'press-start-small', 'PRICE', 7).setTint(0x888888))
    this.orderBookContainer.add(this.add.bitmapText(240, colY, 'press-start-small', 'QTY', 7).setTint(0x888888))

    const maxRows = 12
    const rowHeight = 18

    // Bids (green)
    this.orderBook.buys.slice(0, maxRows).forEach((bid, i) => {
      const y = 40 + i * rowHeight
      const bidBg = this.add.graphics()
      bidBg.fillStyle(0x4caf50, 0.1)
      bidBg.fillRect(0, y - 2, this.sidebarWidth - 20, rowHeight)
      this.orderBookContainer.add(bidBg)

      this.orderBookContainer.add(this.add.bitmapText(10, y, 'press-start-small', this.formatCoins(bid.price), 8).setTint(0x4caf50))
      this.orderBookContainer.add(this.add.bitmapText(90, y, 'press-start-small', `x${bid.quantity} (${bid.orders})`, 8).setTint(0x8bc34a))
    })

    // Asks (red)
    this.orderBook.sells.slice(0, maxRows).forEach((ask, i) => {
      const y = 40 + i * rowHeight
      const askBg = this.add.graphics()
      askBg.fillStyle(0xf44336, 0.1)
      askBg.fillRect(this.sidebarWidth / 2, y - 2, this.sidebarWidth / 2 - 10, rowHeight)
      this.orderBookContainer.add(askBg)

      this.orderBookContainer.add(this.add.bitmapText(160, y, 'press-start-small', this.formatCoins(ask.price), 8).setTint(0xf44336))
      this.orderBookContainer.add(this.add.bitmapText(240, y, 'press-start-small', `x${ask.quantity} (${ask.orders})`, 8).setTint(0xef9a9a))
    })

    // Spread
    if (this.orderBook.buys.length && this.orderBook.sells.length) {
      const spread = this.orderBook.sells[0].price - this.orderBook.buys[0].price
      const spreadPct = ((spread / this.orderBook.buys[0].price) * 100).toFixed(2)
      const spreadY = 40 + maxRows * rowHeight + 10
      this.orderBookContainer.add(this.add.bitmapText(10, spreadY, 'press-start-small', `SPREAD: ${this.formatCoins(spread)} (${spreadPct}%)`, 8).setTint(0xffd700))
    }
  }

  private renderPriceChart(): void {
    this.priceChartContainer.removeAll(true)

    if (!this.selectedItem) return

    const history = this.priceHistory.get(this.selectedItem.id)
    if (!history || history.length < 2) return

    const w = this.sidebarWidth - 20
    const h = 150
    const padding = 20

    // Find min/max price
    const prices = history.map(p => p.price)
    const minPrice = Math.min(...prices)
    const maxPrice = Math.max(...prices)
    const priceRange = maxPrice - minPrice || 1

    // Background
    const chartBg = this.add.graphics()
    chartBg.fillStyle(0x051020, 1)
    chartBg.fillRect(0, 0, w, h)
    chartBg.lineStyle(1, 0x222222, 1)
    chartBg.strokeRect(0, 0, w, h)
    this.priceChartContainer.add(chartBg)

    // Grid lines
    chartBg.lineStyle(1, 0x1a2a40, 0.5)
    for (let i = 1; i < 4; i++) {
      const y = padding + (h - 2 * padding) * i / 4
      chartBg.lineBetween(padding, y, w - padding, y)
    }
    for (let i = 1; i < 5; i++) {
      const x = padding + (w - 2 * padding) * i / 5
      chartBg.lineBetween(x, padding, x, h - padding)
    }

    // Price line
    const line = this.add.graphics()
    line.lineStyle(2, 0x00ff88, 1)
    line.beginPath()

    history.forEach((point, i) => {
      const x = padding + (w - 2 * padding) * i / (history.length - 1)
      const y = h - padding - (h - 2 * padding) * (point.price - minPrice) / priceRange
      if (i === 0) line.moveTo(x, y)
      else line.lineTo(x, y)
    })
    line.strokePath()
    this.priceChartContainer.add(line)

    // Fill under area
    const fill = this.add.graphics()
    fill.fillStyle(0x00ff88, 0.1)
    fill.beginPath()
    fill.moveTo(padding, h - padding)
    history.forEach((point, i) => {
      const x = padding + (w - 2 * padding) * i / (history.length - 1)
      const y = h - padding - (h - 2 * padding) * (point.price - minPrice) / priceRange
      fill.lineTo(x, y)
    })
    fill.lineTo(w - padding, h - padding)
    fill.closePath()
    fill.fillPath()
    this.priceChartContainer.add(fill)

    // Current price label
    const currentPrice = history[history.length - 1].price
    const change = history.length > 1 ? ((currentPrice - history[history.length - 2].price) / history[history.length - 2].price * 100) : 0
    const changeColor = change >= 0 ? 0x4caf50 : 0xf44336
    const changeSign = change >= 0 ? '+' : ''

    this.priceChartContainer.add(this.add.bitmapText(w / 2, 10, 'press-start-small', `${this.formatCoins(currentPrice)} (${changeSign}${change.toFixed(2)}%)`, 10)
      .setOrigin(0.5)
      .setTint(changeColor))

    // Min/Max labels
    this.priceChartContainer.add(this.add.bitmapText(padding, h - padding + 5, 'press-start-small', this.formatCoins(minPrice), 7).setTint(0x888888))
    this.priceChartContainer.add(this.add.bitmapText(w - padding, h - padding + 5, 'press-start-small', this.formatCoins(maxPrice), 7).setOrigin(1, 0).setTint(0x888888))
  }

  private createDetailPanel(): void {
    this.detailContainer = this.add.container(this.detailX, this.contentY).setDepth(15)
    this.mainContainer.add(this.detailContainer)

    // Background
    const bg = this.add.graphics()
    bg.fillStyle(0x0a0a12, 0.9)
    bg.fillRoundedRect(0, 0, this.detailWidth, this.contentHeight, 12)
    bg.lineStyle(1, 0x222222, 1)
    bg.strokeRoundedRect(0, 0, this.detailWidth, this.contentHeight, 12)
    this.detailContainer.add(bg)

    // Placeholder text
    this.detailContainer.add(this.add.bitmapText(this.detailWidth / 2, this.contentHeight / 2, 'press-start-small', 'SELECT A HAT\nTO VIEW DETAILS', 12)
      .setOrigin(0.5)
      .setTint(0x555555)
      .setCenterAlign())
  }

  private createFooter(): void {
    const { width, height } = this.scale
    const footerY = height - this.footerHeight

    this.footerContainer = this.add.container(0, footerY).setDepth(20)
    this.mainContainer.add(this.footerContainer)

    // Background
    const bg = this.add.graphics()
    bg.fillStyle(0x0a0a12, 0.95)
    bg.fillRect(0, 0, width, this.footerHeight)
    bg.lineStyle(1, 0x222222, 1)
    bg.lineBetween(0, 0, width, 0)
    this.footerContainer.add(bg)

    // Action buttons
    const buttons = [
      { text: 'BUY', color: 0x4caf50, action: () => this.buySelected(), enabled: () => !!this.selectedItem && this.currentTab === 'browse' },
      { text: 'PLACE BUY ORDER', color: 0x2196f3, action: () => this.placeBuyOrder(), enabled: () => !!this.selectedItem },
      { text: 'LIST FOR SALE', color: 0xff9800, action: () => this.listForSale(), enabled: () => this.currentTab === 'sell' && this.playerData.inventory.length > 0 },
      { text: 'CANCEL LISTING', color: 0xf44336, action: () => this.cancelListing(), enabled: () => this.currentTab === 'sell' && this.playerData.activeListings.length > 0 },
      { text: 'RETURN TO LOCH', color: 0x888888, action: () => this.returnToGame(), enabled: () => true },
    ]

    const btnWidth = 180
    const btnHeight = 40
    const startX = (width - buttons.length * (btnWidth + 10)) / 2

    buttons.forEach((btn, i) => {
      const x = startX + i * (btnWidth + 10) + btnWidth / 2
      const y = this.footerHeight / 2

      const container = this.add.container(x, y)
      const canEnable = btn.enabled()

      const bgBtn = this.add.graphics()
      bgBtn.fillStyle(canEnable ? btn.color : 0x333333, canEnable ? 1 : 0.5)
      bgBtn.fillRoundedRect(-btnWidth / 2, -btnHeight / 2, btnWidth, btnHeight, 8)
      if (canEnable) {
        bgBtn.lineStyle(2, Phaser.Display.Color.IntegerToColor(btn.color).brighten(50).color, 1)
        bgBtn.strokeRoundedRect(-btnWidth / 2, -btnHeight / 2, btnWidth, btnHeight, 8)
      }
      container.add(bgBtn)

      const text = this.add.bitmapText(0, 0, 'press-start-small', btn.text, 12)
        .setOrigin(0.5)
        .setTint(canEnable ? 0x0a0a12 : 0x666666)
      container.add(text)

      if (canEnable) {
        container.setSize(btnWidth, btnHeight)
        container.setInteractive(new Phaser.Geom.Rectangle(-btnWidth / 2, -btnHeight / 2, btnWidth, btnHeight), Phaser.Geom.Rectangle.Contains)

        container.on('pointerover', () => {
          bgBtn.clear()
          bgBtn.fillStyle(Phaser.Display.Color.IntegerToColor(btn.color).brighten(50).color, 1)
          bgBtn.fillRoundedRect(-btnWidth / 2, -btnHeight / 2, btnWidth, btnHeight, 8)
          bgBtn.lineStyle(2, 0xffffff, 1)
          bgBtn.strokeRoundedRect(-btnWidth / 2, -btnHeight / 2, btnWidth, btnHeight, 8)
          text.setScale(1.05)
        })

        container.on('pointerout', () => {
          bgBtn.clear()
          bgBtn.fillStyle(btn.color, 1)
          bgBtn.fillRoundedRect(-btnWidth / 2, -btnHeight / 2, btnWidth, btnHeight, 8)
          bgBtn.lineStyle(2, Phaser.Display.Color.IntegerToColor(btn.color).brighten(50).color, 1)
          bgBtn.strokeRoundedRect(-btnWidth / 2, -btnHeight / 2, btnWidth, btnHeight, 8)
          text.setScale(1)
        })

        container.on('pointerdown', btn.action)
      }

      this.footerContainer.add(container)
    })
  }

  private setupInput(): void {
    // Keyboard shortcuts
    this.input.keyboard!.on('keydown-ESC', () => this.returnToGame())
    this.input.keyboard!.on('keydown-TAB', () => this.cycleTab())
  }

  private cycleTab(): void {
    const tabs = ['browse', 'sell', 'buy', 'vault', 'history']
    const currentIndex = tabs.indexOf(this.currentTab)
    this.switchTab(tabs[(currentIndex + 1) % tabs.length])
  }

  private setupNetworking(): void {
    // Placeholder for WebSocket connection to market feed
    console.log('[MarketScene] Market WebSocket placeholder')
  }

  private startAutoRefresh(): void {
    // Refresh market data every 30 seconds
    this.refreshTimer = this.time.addEvent({
      delay: 30000,
      loop: true,
      callback: () => {
        this.simulateMarketActivity()
        this.refreshContent()
      },
    })
  }

  private simulateMarketActivity(): void {
    // Simulate price movements
    this.marketItems.forEach(item => {
      if (PhaserMath.FloatBetween(0, 1) < 0.1) { // 10% chance per refresh
        const variation = PhaserMath.FloatBetween(-0.05, 0.05)
        item.price = Math.max(1, Math.floor(item.price * (1 + variation)))
      }
    })

    // Update order book
    this.generateMockOrderBook()

    // Update price history
    this.marketItems.slice(0, 10).forEach(item => {
      const history = this.priceHistory.get(item.id)
      if (history) {
        const lastPrice = history[history.length - 1].price
        const variation = PhaserMath.FloatBetween(-0.03, 0.03)
        const newPrice = Math.max(1, Math.floor(lastPrice * (1 + variation)))
        history.push({ time: Date.now(), price: newPrice })
        if (history.length > 30) history.shift()
      }
    })

    this.sortItems()
  }

  private refreshContent(): void {
    this.filterAndSortItems()
    this.renderItemList()
    this.renderOrderBook()
    this.renderPriceChart()
    this.updateFooterButtons()
  }

  private filterAndSortItems(): void {
    // Filter
    let filtered = this.marketItems

    if (this.currentTab === 'sell') {
      filtered = this.playerData.inventory
    } else if (this.currentTab === 'vault') {
      filtered = this.marketItems.filter(i => i.metadata.discontinued || i.metadata.limitedEdition)
    } else if (this.currentTab === 'history') {
      filtered = this.playerData.tradeHistory.length ? this.playerData.tradeHistory.map(t => this.marketItems.find(i => i.id === t.from || i.id === t.to)).filter(Boolean) as MarketItem[] : []
    }

    // Tier filter
    if (this.filterTier !== 'all') {
      filtered = filtered.filter(i => i.tier === this.filterTier)
    }

    // Search filter
    if (this.searchQuery) {
      filtered = filtered.filter(i =>
        i.name.toLowerCase().includes(this.searchQuery) ||
        i.id.toLowerCase().includes(this.searchQuery)
      )
    }

    // Sort
    this.sortItems(filtered)

    this.filteredItems = filtered
  }

  private filteredItems: MarketItem[] = []

  private sortItems(items?: MarketItem[]): void {
    const arr = items || this.marketItems
    arr.sort((a, b) => {
      switch (this.sortBy) {
        case 'price_asc':
          return a.price - b.price
        case 'price_desc':
          return b.price - a.price
        case 'recent':
          return (b.provenance.creationTimestamp || 0) - (a.provenance.creationTimestamp || 0)
        case 'tier':
          return TIER_ORDER.indexOf(a.tier) - TIER_ORDER.indexOf(b.tier)
      }
    })
  }

  private renderItemList(): void {
    this.itemList.removeAll(true)

    const itemHeight = 80
    const padding = 10
    const startY = padding

    this.filteredItems.forEach((item, i) => {
      const y = startY + i * (itemHeight + padding)
      const isSelected = this.selectedItem?.id === item.id

      const container = this.add.container(0, y)
      container.setData('item', item)

      // Background
      const bg = this.add.graphics()
      bg.fillStyle(isSelected ? 0x1a2a2a : 0x0a0a12, 1)
      bg.fillRoundedRect(padding, 0, this.contentWidth - 2 * padding - 12, itemHeight, 8)
      if (isSelected) {
        bg.lineStyle(2, TIER_COLORS[item.tier], 1)
        bg.strokeRoundedRect(padding, 0, this.contentWidth - 2 * padding - 12, itemHeight, 8)
      }
      container.add(bg)

      // Tier indicator bar
      const tierBar = this.add.graphics()
      tierBar.fillStyle(TIER_COLORS[item.tier], 1)
      tierBar.fillRoundedRect(padding, 0, 4, itemHeight, 8)
      container.add(tierBar)

      // Item icon
      const icon = this.add.image(padding + 50, itemHeight / 2, item.visual.sprite)
        .setScale(1.5)
        .setDepth(17)
      container.add(icon)

      // Rarity glow for higher tiers
      if (item.visual.particleEffect) {
        const glow = this.add.image(padding + 50, itemHeight / 2, item.visual.particleEffect)
          .setScale(0.5)
          .setBlendMode('ADD')
          .setAlpha(0.5)
        container.add(glow)
        this.tweens.add({
          targets: glow,
          scale: { from: 0.4, to: 0.6 },
          alpha: { from: 0.3, to: 0.6 },
          duration: 1000,
          ease: 'Sine.easeInOut',
          yoyo: true,
          repeat: -1,
        })
      }

      // Mythic distortion
      if (item.visual.shader === 'shader-mythic-distort') {
        // Would apply shader in real implementation
      }

      // Name
      container.add(this.add.bitmapText(padding + 90, itemHeight / 2 - 18, 'press-start-small', item.name, 12)
        .setTint(TIER_COLORS[item.tier]))

      // Tier badge
      container.add(this.add.bitmapText(padding + 90, itemHeight / 2 + 2, 'press-start-small', item.tier.toUpperCase(), 8)
        .setTint(TIER_COLORS[item.tier]))

      // Price
      container.add(this.add.bitmapText(this.contentWidth - padding - 80, itemHeight / 2 - 10, 'press-start-small', this.formatCoins(item.price), 14)
        .setOrigin(1, 0)
        .setTint(0xffd700))

      container.add(this.add.bitmapText(this.contentWidth - padding - 80, itemHeight / 2 + 12, 'press-start-small', 'ABYSSAL COINS', 6)
        .setOrigin(1, 0)
        .setTint(0x888888))

      // Discontinued/Limited badge
      if (item.metadata.discontinued) {
        container.add(this.add.bitmapText(padding + 90, itemHeight / 2 + 22, 'press-start-small', '🔒 DISCONTINUED', 8).setTint(0xffd700))
        if (item.metadata.serialNumber) {
          container.add(this.add.bitmapText(this.contentWidth - padding - 80, itemHeight / 2 + 22, 'press-start-small', `#${item.metadata.serialNumber}`, 8).setOrigin(1, 0).setTint(0xffd700))
        }
      } else if (item.metadata.limitedEdition) {
        container.add(this.add.bitmapText(padding + 90, itemHeight / 2 + 22, 'press-start-small', '✨ LIMITED', 8).setTint(0x9c27b0))
      }

      // Seller info (for browse tab)
      if (this.currentTab === 'browse' && item.sellerName) {
        container.add(this.add.bitmapText(this.contentWidth - padding - 200, itemHeight / 2 + 12, 'press-start-small', `Seller: ${item.sellerName}`, 6)
          .setOrigin(1, 0)
          .setTint(0x666666))
      }

      // Interactivity
      container.setSize(this.contentWidth - 2 * padding - 12, itemHeight)
      container.setInteractive(new Phaser.Geom.Rectangle(padding, 0, this.contentWidth - 2 * padding - 12, itemHeight), Phaser.Geom.Rectangle.Contains)

      container.on('pointerover', () => {
        if (!isSelected) {
          bg.clear().fillStyle(0x12122a, 1).fillRoundedRect(padding, 0, this.contentWidth - 2 * padding - 12, itemHeight, 8)
        }
      })

      container.on('pointerout', () => {
        if (!isSelected) {
          bg.clear().fillStyle(0x0a0a12, 1).fillRoundedRect(padding, 0, this.contentWidth - 2 * padding - 12, itemHeight, 8)
        }
      })

      container.on('pointerdown', () => this.selectItem(item))

      this.itemList.add(container)
    })

    // Update scroll
    const totalHeight = this.filteredItems.length * (itemHeight + padding) + padding
    this.maxScrollOffset = Math.max(0, totalHeight - (this.contentHeight - 70))
    this.scrollOffset = Math.min(this.scrollOffset, this.maxScrollOffset)
    this.updateScroll()
  }

  private selectItem(item: MarketItem): void {
    this.selectedItem = item
    this.renderItemList()
    this.renderDetailPanel()
    this.renderPriceChart()
    this.updateFooterButtons()
  }

  private renderDetailPanel(): void {
    this.detailContainer.removeAll(true)

    if (!this.selectedItem) {
      this.detailContainer.add(this.add.bitmapText(this.detailWidth / 2, this.contentHeight / 2, 'press-start-small', 'SELECT A HAT\nTO VIEW DETAILS', 12)
        .setOrigin(0.5)
        .setTint(0x555555)
        .setCenterAlign())
      return
    }

    const item = this.selectedItem
    let y = 20
    const padding = 20
    const colWidth = this.detailWidth - 2 * padding

    // Item icon large
    const icon = this.add.image(this.detailWidth / 2, y + 60, item.visual.sprite)
      .setScale(3)
    this.detailContainer.add(icon)

    // Rarity glow
    if (item.visual.particleEffect) {
      const glow = this.add.image(this.detailWidth / 2, y + 60, item.visual.particleEffect)
        .setScale(1.5)
        .setBlendMode('ADD')
        .setAlpha(0.6)
      this.detailContainer.add(glow)
      this.tweens.add({
        targets: glow,
        scale: { from: 1.3, to: 1.7 },
        duration: 1500,
        ease: 'Sine.easeInOut',
        yoyo: true,
        repeat: -1,
      })
    }

    y += 150

    // Name
    this.detailContainer.add(this.add.bitmapText(this.detailWidth / 2, y, 'press-start', item.name, 18)
      .setOrigin(0.5)
      .setTint(TIER_COLORS[item.tier]))
    y += 30

    // Tier
    this.detailContainer.add(this.add.bitmapText(this.detailWidth / 2, y, 'press-start-small', item.tier.toUpperCase(), 12)
      .setOrigin(0.5)
      .setTint(TIER_COLORS[item.tier]))
    y += 25

    // Price
    this.detailContainer.add(this.add.bitmapText(this.detailWidth / 2, y, 'press-start-small', `${this.formatCoins(item.price)} ABYSSAL COINS`, 14)
      .setOrigin(0.5)
      .setTint(0xffd700))
    y += 25

    // Badges
    if (item.metadata.discontinued) {
      this.detailContainer.add(this.add.bitmapText(this.detailWidth / 2, y, 'press-start-small', `🔒 DISCONTINUED${item.metadata.serialNumber ? ` #${item.metadata.serialNumber}` : ''}`, 10)
        .setOrigin(0.5)
        .setTint(0xffd700))
      y += 20
    } else if (item.metadata.limitedEdition) {
      this.detailContainer.add(this.add.bitmapText(this.detailWidth / 2, y, 'press-start-small', '✨ LIMITED EDITION', 10)
        .setOrigin(0.5)
        .setTint(0x9c27b0))
      y += 20
    }
    if (item.metadata.eventSource) {
      this.detailContainer.add(this.add.bitmapText(this.detailWidth / 2, y, 'press-start-small', `EVENT: ${item.metadata.eventSource}`, 10)
        .setOrigin(0.5)
        .setTint(0x00ff88))
      y += 20
    }

    y += 10

    // Description
    const desc = this.getItemDescription(item)
    this.detailContainer.add(this.add.bitmapText(this.detailWidth / 2, y, 'press-start-small', desc, 10)
      .setOrigin(0.5)
      .setTint(0xe8d5c4)
      .setMaxWidth(colWidth)
      .setCenterAlign())
    y += 50

    // Stats
    this.detailContainer.add(this.add.bitmapText(padding, y, 'press-start-small', 'STAT BONUSES', 10)
      .setTint(0xffd700))
    y += 20

    Object.entries(item.stats).forEach(([stat, value]) => {
      const formattedStat = stat.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
      this.detailContainer.add(this.add.bitmapText(padding, y, 'press-start-small', `+${value} ${formattedStat}`, 10)
        .setTint(0x00ff88))
      y += 20
    })

    y += 10

    // Provenance
    this.detailContainer.add(this.add.bitmapText(padding, y, 'press-start-small', 'PROVENANCE', 10)
      .setTint(0xffd700))
    y += 20

    if (item.provenance.creatorId) {
      this.detailContainer.add(this.add.bitmapText(padding, y, 'press-start-small', `Crafted by: ${item.provenance.creatorId}`, 8).setTint(0x888888))
      y += 18
    }

    const createdDate = new Date(item.provenance.creationTimestamp).toLocaleDateString()
    this.detailContainer.add(this.add.bitmapText(padding, y, 'press-start-small', `Created: ${createdDate}`, 8).setTint(0x888888))
    y += 18

    this.detailContainer.add(this.add.bitmapText(padding, y, 'press-start-small', `Trades: ${item.provenance.tradeHistory.length}`, 8).setTint(0x888888))
    y += 18

    // Trade history (abbreviated)
    if (item.provenance.tradeHistory.length > 0) {
      this.detailContainer.add(this.add.bitmapText(padding, y, 'press-start-small', 'RECENT TRADES:', 8).setTint(0x888888))
      y += 18
      item.provenance.tradeHistory.slice(-3).forEach(trade => {
        this.detailContainer.add(this.add.bitmapText(padding + 10, y, 'press-start-small', `${trade.from} → ${trade.to} @ ${new Date(trade.timestamp).toLocaleDateString()}`, 7).setTint(0x666666))
        y += 16
      })
    }
  }

  private getItemDescription(item: MarketItem): string {
    const descriptions: Record<string, string> = {
      noob: 'A sodden reminder that everyone starts somewhere.',
      common: 'Functional headwear for the aspiring dredger.',
      uncommon: 'Crafted with care from the Loch\'s bounty.',
      rare: 'A treasure from the deep, coveted by many.',
      epic: 'Legendary craftsmanship, whispered about in taverns.',
      legendary: 'History made manifest. One of a kind.',
      mythic: 'The Monster\'s own regalia. Reality bends.',
    }
    return descriptions[item.tier] || 'A curious find from the depths.'
  }

  private updateFooterButtons(): void {
    // Recreate footer buttons (simple approach)
    this.footerContainer.removeAll(true)
    this.createFooter()
  }

  // Action handlers
  private buySelected(): void {
    if (!this.selectedItem) return
    if (this.playerData.abyssalCoins < this.selectedItem.price) {
      this.showNotification('INSUFFICIENT FUNDS', 0xf44336)
      return
    }

    this.playerData.abyssalCoins -= this.selectedItem.price
    this.playerData.inventory.push({ ...this.selectedItem })
    this.showNotification(`PURCHASED ${this.selectedItem.name.toUpperCase()}`, 0x4caf50)
    this.playerCoinsText.setText(this.formatCoins(this.playerData.abyssalCoins))
    this.sound.play('sfx-market-buy', { volume: 0.4 })

    // Add to trade history
    this.selectedItem.provenance.tradeHistory.push({
      from: this.selectedItem.sellerName || 'MARKET',
      to: this.playerData.inventory[0]?.id || 'PLAYER',
      price: this.selectedItem.price,
      timestamp: Date.now(),
    })
  }

  private placeBuyOrder(): void {
    if (!this.selectedItem) return
    this.showNotification('BUY ORDER PLACED (NOT YET IMPLEMENTED)', 0x2196f3)
  }

  private listForSale(): void {
    this.showNotification('LISTING UI (NOT YET IMPLEMENTED)', 0xff9800)
  }

  private cancelListing(): void {
    this.showNotification('CANCEL LISTING (NOT YET IMPLEMENTED)', 0xf44336)
  }

  private returnToGame(): void {
    this.cleanup()
    this.scene.start('GameScene', { playerData: this.convertToGamePlayerData() })
  }

  private convertToGamePlayerData(): any {
    const totalClout = this.playerData.inventory.reduce((s, i) => s + (i.stats.clout_bonus || 0), 0)
    const currentHat = this.playerData.inventory[0]?.id || 'soggy-visor'
    return {
      id: 'player_' + Math.random().toString(36).substr(2, 9),
      name: 'Angler_' + Math.random().toString(36).substr(2, 5),
      clout: totalClout,
      position: { x: 400, y: 300 },
      currentHat: currentHat,
      boatTier: 1,
    }
  }

  private showNotification(message: string, color: number): void {
    const { width } = this.scale
    const container = this.add.container(width / 2, 120).setDepth(100)

    const bg = this.add.graphics()
    bg.fillStyle(0x0a0a12, 0.95)
    bg.fillRoundedRect(-200, -25, 400, 50, 8)
    bg.lineStyle(2, color, 1)
    bg.strokeRoundedRect(-200, -25, 400, 50, 8)
    container.add(bg)

    const text = this.add.bitmapText(0, 0, 'press-start-small', message, 14)
      .setOrigin(0.5)
      .setTint(color)
    container.add(text)

    this.mainContainer.add(container)
    this.notifications.push(container)

    // Animate
    container.setScale(0)
    this.tweens.add({
      targets: container,
      scale: 1,
      duration: 300,
      ease: 'Back.out',
    })

    // Auto-remove
    this.time.delayedCall(3000, () => {
      this.tweens.add({
        targets: container,
        scale: 0,
        alpha: 0,
        y: container.y - 50,
        duration: 300,
        ease: 'Back.in',
        onComplete: () => {
          container.destroy()
          this.notifications = this.notifications.filter(n => n !== container)
        },
      })
    })

    // Stack notifications
    this.notifications.forEach((n, i) => {
      if (n !== container) {
        this.tweens.add({ targets: n, y: 120 - i * 60, duration: 300 })
      }
    })
  }

  private formatCoins(amount: number): string {
    if (amount >= 1000000) return (amount / 1000000).toFixed(2) + 'M'
    if (amount >= 1000) return (amount / 1000).toFixed(1) + 'K'
    return amount.toLocaleString()
  }

  private formatNumber(num: number): string {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
    return num.toString()
  }

  private handleResize(_gameSize: Phaser.Structs.Size): void {
    // Update search input position
    if (this.searchInput) {
      this.searchInput.style.left = `${300}px`
      this.searchInput.style.top = `${20}px`
    }

    // Recreate layout (simplified - full rebuild)
    this.mainContainer.removeAll(true)
    this.createBackground()
    this.createLayout()
    this.createHeader()
    this.createTabs()
    this.createContentArea()
    this.createSidebar()
    this.createDetailPanel()
    this.createFooter()
  }

  private cleanup(): void {
    if (this.searchInput) {
      this.searchInput.remove()
      this.searchInput = null as any
    }
    if (this.refreshTimer) {
      this.time.removeEvent(this.refreshTimer)
    }
    this.notifications.forEach(n => n.destroy())
    this.notifications = []
  }

  shutdown(): void {
    this.cleanup()
    this.scale.off('resize', this.handleResize, this)
  }
}