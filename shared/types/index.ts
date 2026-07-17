// Shared type definitions for Abyssal Assets
// Barrel file — re-exports all specialized modules

import { MonsterTier } from './monsters'

export * from './monsters'
export * from './skills'
export * from './synergies'
export * from './provenance'
export * from './quests'
export * from './game-master'

// ─── Game Types (unique to barrel) ──────────────────────────────

export interface MarketItem {
  id: string
  name: string
  tier: MonsterTier
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

export const TIER_ORDER: MonsterTier[] = [
  'noob', 'common', 'uncommon', 'rare', 'epic', 'legendary', 'mythic',
]

export const TIER_COLORS: Record<MonsterTier, number> = {
  noob: 0x888888,
  common: 0xffffff,
  uncommon: 0x4caf50,
  rare: 0x2196f3,
  epic: 0x9c27b0,
  legendary: 0xffd700,
  mythic: 0xff00ff,
}

export interface TradeRecord {
  from: string
  to: string
  price: number
  timestamp: number
}

export interface OrderBookEntry {
  price: number
  quantity: number
  orders: number
  isBuy: boolean
}

export interface PlayerMarketData {
  abyssalCoins: number
  inventory: MarketItem[]
  activeListings: MarketListing[]
  tradeHistory: TradeRecord[]
}

export interface MarketListing {
  id: string
  itemId: string
  price: number
  quantity: number
  timestamp: number
  expiresAt: number
}

export interface DredgeSpotData {
  x: number
  y: number
  zone: Zone
  depth: number
  active: boolean
  cooldown: number
}

export type Zone = 'shallows' | 'standard' | 'deep' | 'abyssal' | 'trench'

export const ZONES: Zone[] = ['shallows', 'standard', 'deep', 'abyssal', 'trench']

export interface PlayerData {
  abyssalCoins: number
  inventory: MarketItem[]
  boatTier: number
  clout: number
  currentZone: Zone
  skillLevels: Record<string, number>
  questFlags: Record<string, boolean>
}

export interface HatData extends MarketItem {
  hatType: string
  equipSlot: 'head'
}

export interface BoatData {
  tier: number
  name: string
  maxDepth: number
  sonarRange: number
  cargoCapacity: number
  speed: number
  durability: number
}

export interface NetworkEvents {
  'player:join': (data: { playerId: string; playerData: PlayerData }) => void
  'player:leave': (data: { playerId: string }) => void
  'market:update': (data: { items: MarketItem[]; orderBook: { buys: OrderBookEntry[]; sells: OrderBookEntry[] } }) => void
  'dredge:result': (data: { success: boolean; loot?: MarketItem; spotId: string }) => void
  'chat:message': (data: { from: string; text: string; channel: string }) => void
  'quest:progress': (data: { questId: string; objectiveId: string; progress: number }) => void
  'skill:xp': (data: { skillId: string; xp: number }) => void
  'zone:change': (data: { playerId: string; from: Zone; to: Zone }) => void
  'nessie:spawn': (data: { zone: Zone; position: { x: number; y: number } }) => void
}

export interface ServerToClientEvents {
  'market:items': { items: MarketItem[] }
  'market:orderbook': { buys: OrderBookEntry[]; sells: OrderBookEntry[] }
  'dredge:spot': { spot: DredgeSpotData }
  'dredge:start': { spotId: string; difficulty: string }
  'dredge:complete': { success: boolean; loot?: MarketItem; cloutGained: number }
  'player:update': { coins: number; clout: number; inventory: MarketItem[] }
  'quest:update': { questId: string; progress: number }
  'skill:levelup': { skillId: string; newLevel: number }
}

export interface ClientToServerEvents {
  'market:buy': { itemId: string; price: number; quantity: number }
  'market:sell': { itemId: string; price: number; quantity: number }
  'market:list': { itemId: string; price: number; quantity: number }
  'dredge:start': { spotId: string }
  'dredge:action': { sweepAngle: number }
  'player:move': { x: number; y: number; angle: number }
  'chat:send': { text: string; channel: string }
  'quest:accept': { questId: string }
  'skill:train': { skillId: string }
}
