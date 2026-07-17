import { describe, it, expect } from 'vitest'

// Test the shared types that define our game's data contracts
import {
  MarketItem,
  TradeRecord,
  OrderBookEntry,
  PlayerMarketData,
  MarketListing,
  TIER_ORDER,
  TIER_COLORS,
} from '../../../shared/types'

describe('Shared Types - Data Contracts', () => {
  it('TIER_ORDER has correct progression from noob to mythic', () => {
    expect(TIER_ORDER).toEqual([
      'noob',
      'common',
      'uncommon',
      'rare',
      'epic',
      'legendary',
      'mythic',
    ])
  })

  it('TIER_COLORS has entry for every tier', () => {
    TIER_ORDER.forEach((tier) => {
      expect(TIER_COLORS[tier]).toBeDefined()
      expect(typeof TIER_COLORS[tier]).toBe('number')
    })
  })

  it('MarketItem requires all mandatory fields', () => {
    const item: MarketItem = {
      id: 'hat-test-001',
      name: 'Test Hat',
      tier: 'common',
      price: 100,
      quantity: 1,
      stats: { clout: 5, luck: 2 },
      visual: { sprite: 'hat-test', particleEffect: 'sparkle' },
      provenance: { creationTimestamp: Date.now(), tradeHistory: [] },
      metadata: { discontinued: false, limitedEdition: false },
    }

    expect(item.id).toBe('hat-test-001')
    expect(item.tier).toBe('common')
    expect(item.stats.clout).toBe(5)
  })

  it('TradeRecord captures buyer, seller, price, timestamp', () => {
    const trade: TradeRecord = {
      from: 'player-123',
      to: 'player-456',
      price: 5000,
      timestamp: Date.now(),
    }

    expect(trade.from).toBe('player-123')
    expect(trade.price).toBe(5000)
  })

  it('OrderBookEntry distinguishes buys from sells', () => {
    const buy: OrderBookEntry = { price: 1000, quantity: 5, orders: 3, isBuy: true }
    const sell: OrderBookEntry = { price: 1200, quantity: 3, orders: 2, isBuy: false }

    expect(buy.isBuy).toBe(true)
    expect(sell.isBuy).toBe(false)
  })

  it('PlayerMarketData tracks coins, inventory, listings, history', () => {
    const playerData: PlayerMarketData = {
      abyssalCoins: 10000,
      inventory: [],
      activeListings: [],
      tradeHistory: [],
    }

    expect(playerData.abyssalCoins).toBe(10000)
    expect(Array.isArray(playerData.inventory)).toBe(true)
  })

  it('MarketListing includes expiration for time-limited orders', () => {
    const listing: MarketListing = {
      id: 'listing-001',
      itemId: 'hat-rare-001',
      price: 25000,
      quantity: 1,
      timestamp: Date.now(),
      expiresAt: Date.now() + 86400000, // 24 hours
    }

    expect(listing.expiresAt).toBeGreaterThan(listing.timestamp)
  })
})