// Shared types for Abyssal Assets - Provenance System

export type ProvenanceType = 
  | 'dredge'
  | 'craft'
  | 'monster'
  | 'quest'
  | 'event'
  | 'trade'
  | 'gift'
  | 'found'
  | 'transmute'
  | 'salvage'
  | 'purchase'
  | 'reward'
  | 'genesis'; // First of its kind

export interface Provenance {
  type: ProvenanceType;
  source_id: string;           // monster_id, quest_id, event_id, player_id, etc.
  source_name: string;         // Human readable: "Nessie (Adult)", "Kraken Matriarch", "The Great Dredge"
  timestamp: number;
  
  // For monster drops
  kill_id?: string;            // Unique kill ID for world-first tracking
  kill_method?: 'solo' | 'party' | 'raid' | 'world_boss';
  party_members?: number[];
  precision?: number;          // For dredge-origin hats (0-1)
  critical_hit?: boolean;
  world_first?: boolean;
  world_event_active?: string;
  
  // For crafted items
  skill_levels?: Record<string, number>; // Skills at creation time
  station_id?: string;         // Which crafting station
  catalyst_used?: string;      // Catalyst item ID
  quality_roll?: number;       // 0-1 quality
  essence_charge?: number;     // Initial essence charge
  
  // For quest/event rewards
  quest_id?: string;
  event_id?: string;
  choice_made?: string;        // For branching quests
  
  // For trades
  trader_id?: number;
  trade_id?: string;
  price_paid?: number;
  
}

export interface TransmuteRecord {
  timestamp: number;
  from_item_id: string;
  to_item_id: string;
  catalyst_used?: string;
  success: boolean;
  essence_cost: number;
  stat_changes: Record<string, number>;
  essence_charge_before: number;
  essence_charge_after: number;
  transmuter_id: number;
  transmuter_skill_levels: Record<string, number>;
}

export interface ItemEssence {
  item_id: number;
  current_charge: number;
  max_charge: number;
  essence_type: string;        // 'arcane', 'primal', 'divine', 'void', 'prismatic'
  recharge_rate: number;       // Per hour
  last_recharge: number;
  capacity_bonus: number;      // From item quality/enchants
}

export interface ItemStats {
  // Base stats
  clout_bonus: number;
  dredge_luck: number;
  craft_speed: number;
  market_fee_reduction: number;
  dredge_speed: number;
  salvage_efficiency: number;
  hunting_luck: number;
  foraging_yield: number;
  
  // Combat
  health_bonus: number;
  armor_bonus: number;
  evasion_bonus: number;
  damage_bonus: number;
  critical_chance: number;
  critical_multiplier: number;
  
  // Resistances
  resistance_physical: number;
  resistance_piercing: number;
  resistance_crushing: number;
  resistance_slashing: number;
  resistance_poison: number;
  resistance_acid: number;
  resistance_electric: number;
  resistance_pressure: number;
  resistance_sonic: number;
  resistance_psychic: number;
  resistance_void: number;
  
  // Utility
  oxygen_bonus: number;
  pressure_resistance: number;
  sanity_bonus: number;
  sonar_range: number;
  night_vision: boolean;
  water_breathing: boolean;
  
  // Social/Economic
  trading_fee_reduction: number;
  negotiation_bonus: number;
  guild_xp_bonus: number;
  party_xp_share: number;
  
  // Special
  essence_regen: number;
  transmute_cost_reduction: number;
  experience_bonus: number;
  soul_coin_find: number;
  rare_drop_chance: number;
  double_loot_chance: number;
  auto_identify: boolean;
  
  // Cosmetic
  particle_effect?: string;
  shader?: string;
  dyeable: boolean;
  title_granted?: string;
  emote_unlocked?: string;
}

export interface HatProvenance extends Provenance {
  // Hat-specific provenance
  progenitor: {
    type: 'dredge' | 'craft' | 'monster' | 'quest' | 'event' | 'trade' | 'genesis';
    source_id: string;
    source_name: string;
    kill_id?: string;
    kill_method?: 'solo' | 'party' | 'raid' | 'world_boss';
    party_members?: number[];
    precision?: number;
    critical_hit?: boolean;
    world_first?: boolean;
    world_event_active?: string;
  };
  
  // Transmutation
  transmute_count: number;
  transmute_history: TransmuteRecord[];
  transmute_eligible: boolean;
  transmute_cost_base: number;
  transmute_tier_preserved: boolean;
  
  // Essence
  essence_charge: number;
  max_essence: number;
  essence_type?: string;
  
  // Soul binding
  soul_bound: boolean;
  soul_bound_to?: number;
  soul_bind_timestamp?: number;
  trade_locked: boolean;
  
  // Stats snapshot at creation
  stats_snapshot: ItemStats;
}

export interface ItemStats {
  // Base stats (from hat definition)
  base: {
    clout_bonus: number;
    dredge_luck: number;
    craft_speed: number;
    market_fee_reduction: number;
    dredge_speed: number;
    salvage_efficiency: number;
    hunting_luck: number;
    foraging_yield: number;
    health_bonus: number;
    armor_bonus: number;
    evasion_bonus: number;
    damage_bonus: number;
    critical_chance: number;
    critical_multiplier: number;
    resistance_physical: number;
    resistance_piercing: number;
    resistance_crushing: number;
    resistance_slashing: number;
    resistance_poison: number;
    resistance_acid: number;
    resistance_electric: number;
    resistance_pressure: number;
    resistance_sonic: number;
    resistance_psychic: number;
    resistance_void: number;
    oxygen_bonus: number;
    pressure_resistance: number;
    sanity_bonus: number;
    sonar_range: number;
    night_vision: boolean;
    water_breathing: boolean;
    trading_fee_reduction: number;
    negotiation_bonus: number;
    guild_xp_bonus: number;
    party_xp_share: number;
    essence_regen: number;
    transmute_cost_reduction: number;
    rarity_preservation: number;
    experience_bonus: number;
    soul_coin_find: number;
    rare_drop_chance: number;
    double_loot_chance: number;
    auto_identify: boolean;
  };
  
  // Modified by provenance
  modified: {
    clout_bonus: number;
    dredge_luck: number;
    craft_speed: number;
    market_fee_reduction: number;
    // ... all stats
  };
  
  // Provenance bonuses
  provenance_bonus: {
    monster_origin: number;      // +10% stats
    world_first_kill: number;    // +25% stats
    party_kill: number;          // -10% stats per member
    critical_kill: number;       // +1 rarity tier
    world_event: number;         // Unique visual effect
    precision_bonus: number;     // For dredge origin
    craft_quality: number;       // 0-1 quality roll
    maker_skill: number;         // Skill levels at creation
  };
  
  // Dynamic
  dynamic: {
    essence_charge: number;
    max_essence: number;
    essence_type?: string;
    transmute_count: number;
    transmute_history: TransmuteRecord[];
    soul_bound: boolean;
    soul_bound_to?: number;
    trade_locked: boolean;
  };
}

export interface TransmuteRecord {
  timestamp: number;
  from_item_id: string;
  to_item_id: string;
  catalyst_used?: string;
  success: boolean;
  essence_cost: number;
  stat_changes: Record<string, number>;
  essence_charge_before: number;
  essence_charge_after: number;
  transmuter_id: number;
  transmuter_skill_levels: Record<string, number>;
}

export const PROGENITOR_TYPE_DISPLAY: Record<string, string> = {
  dredge: 'Dredged from the Depths',
  craft: 'Forged at the Forge',
  monster: 'Slain the Beast',
  quest: 'Completed the Saga',
  event: 'Witnessed History',
  trade: 'Traded on the Exchange',
  gift: 'Gifted by Friend',
  found: 'Found in the Depths',
  transmute: 'Transmuted by Alchemy',
  salvage: 'Salvaged from Wreckage',
  purchase: 'Purchased at Market',
  reward: 'Awarded for Valor',
  genesis: 'The First of Its Kind',
};

export const PROGENITOR_COLORS: Record<string, string> = {
  dredge: '#00ffff',
  craft: '#ffd700',
  monster: '#ff4444',
  quest: '#ff00ff',
  event: '#00ff88',
  trade: '#ff8c00',
  gift: '#ff69b4',
  found: '#8888ff',
  transmute: '#8a2be2',
  salvage: '#a0522d',
  purchase: '#32cd32',
  reward: '#ff8c00',
  genesis: '#ffffff',
};

export function getProvenanceDisplay(provenance: ProvenanceType): string {
  return PROGENITOR_TYPE_DISPLAY[provenance] || provenance;
}

export function getProvenanceColor(provenance: ProvenanceType): string {
  return PROGENITOR_COLORS[provenance] || '#ffffff';
}

export function calculateProvenanceBonus(provenance: HatProvenance): Record<string, number> {
  const bonuses: Record<string, number> = {};
  
  if (provenance.type === 'monster') {
    bonuses.stats_all = 0.10; // +10% all stats
    if (provenance.world_first) bonuses.stats_all = 0.25;
    if (provenance.critical_hit) bonuses.rarity_tier = 1;
    if (provenance.kill_method === 'party' && provenance.party_members) {
      bonuses.stats_all = -0.1 * (provenance.party_members.length - 1);
    }
    if (provenance.world_event_active) {
      // Unique visual effect handled separately
    }
  }
  
  if (provenance.type === 'dredge' && provenance.precision) {
    bonuses.precision_bonus = provenance.precision * 0.5;
  }
  
  if (provenance.type === 'craft') {
    const quality = provenance.quality_roll || 0.5;
    bonuses.craft_quality = quality;
    if (provenance.skill_levels) {
      const avg_skill = Object.values(provenance.skill_levels).reduce((a, b) => a + b, 0) / Object.keys(provenance.skill_levels).length;
      bonuses.maker_skill = avg_skill / 99;
    }
  }
  
  return bonuses;
}