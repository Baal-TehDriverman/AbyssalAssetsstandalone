// Shared types for Abyssal Assets - Monster System

export type MonsterTier = 
  | 'noob'          // Tier 0 - No real threat, Noob/Common drops only
  | 'common'        // Tier 1 - Standard wildlife
  | 'uncommon'      // Tier 2 - Notable threats
  | 'rare'          // Tier 3 - Dangerous cryptids
  | 'epic'          // Tier 4 - Boss-level cryptids
  | 'legendary'     // Tier 5 - Major named bosses
  | 'mythic';       // Tier 6 - Unique world bosses

export type MonsterType = 
  | 'fish'
  | 'crustacean'
  | 'mollusk'
  | 'reptile'
  | 'amphibian'
  | 'mammal'
  | 'cephalopod'
  | 'crustacean_giant'
  | 'cryptid'
  | 'legendary_cryptid'
  | 'eldritch'
  | 'divine'
  | 'primordial';

export type MonsterBehavior = 
  | 'passive'           // Never attacks
  | 'territorial'       // Attacks if approached
  | 'aggressive'        // Attacks on sight
  | 'predatory'         // Hunts players actively
  | 'pack_hunter'       // Hunts in groups
  | 'ambush'            // Stealth, surprise attacks
  | 'boss'              // Complex mechanics, phases
  | 'world_boss';       // Server-wide event

export type DamageType = 
  | 'physical'
  | 'piercing'
  | 'crushing'
  | 'slashing'
  | 'poison'
  | 'acid'
  | 'electric'
  | 'pressure'
  | 'sonic'
  | 'psychic'
  | 'void';

export type MonsterSize = 
  | 'tiny'         // < 0.5m
  | 'small'        // 0.5-1m
  | 'medium'       // 1-3m
  | 'large'        // 3-10m
  | 'huge'         // 10-50m
  | 'colossal';    // 50m+

export interface MonsterStats {
  health: number;
  max_health: number;
  armor: number;          // Reduces physical/piercing/crushing/slashing
  resistance: Partial<Record<DamageType, number>>; // 0-1, 1 = immune
  evasion: number;        // 0-1, chance to dodge
  accuracy: number;       // 0-1, hit chance
  critical_chance: number;
  critical_multiplier: number;
  damage_min: number;
  damage_max: number;
  attack_speed: number;   // attacks per second
  attack_range: number;   // in tiles
  move_speed: number;     // tiles per second
  turn_speed: number;     // degrees per second
}

export interface MonsterAI {
  behavior: MonsterBehavior;
  aggro_range: number;          // Detection range
  leash_range: number;          // Max distance from spawn
  patrol_route?: PatrolPoint[]; // If patrolling
  pack_size?: number;           // For pack hunters
  call_for_help_range: number;
  flee_threshold: number;       // HP % to flee
  enrage_threshold: number;     // HP % to enrage
  mechanics: MonsterMechanic[];
}

export interface PatrolPoint {
  x: number;
  y: number;
  wait_time: number; // seconds
}

export interface MonsterMechanic {
  id: string;
  name: string;
  description: string;
  trigger: MechanicTrigger;
  effect: MechanicEffect;
  cooldown: number;
  warning_time: number; // seconds before activation
  telegraph: MechanicTelegraph;
}

export interface MechanicTrigger {
  type: MechanicTriggerType;
  parameters?: Record<string, any>;
}

export type MechanicTriggerType = 
  | 'hp_threshold'       // HP % reached
  | 'time_interval'      // Every X seconds
  | 'player_action'      // Player attacks, uses skill, etc.
  | 'player_position'    // Player in specific area
  | 'combo'              // After specific combo
  | 'enrage'             // When enraged
  | 'phase_transition'   // Phase change
  | 'summon'             // When minion dies
  | 'custom';

export interface MechanicEffect {
  type: 'damage' | 'debuff' | 'knockback' | 'stun' | 'fear' | 'spawn' | 'summon' | 'transform' | 'heal' | 'shield' | 'teleport' | 'environment' | 'custom';
  target: 'player' | 'all_players' | 'area' | 'self' | 'minions' | 'random_player' | 'environment';
  parameters: Record<string, any>;
}

export interface MechanicTelegraph {
  type: 'visual' | 'audio' | 'ui' | 'screen_shake' | 'screen_flash' | 'ground_marker' | 'particle';
  duration: number; // seconds before effect
  intensity: number; // 0-1
  data: Record<string, any>; // e.g., color, radius, sprite
}

export interface MonsterDrop {
  item_id: string;
  min_quantity: number;
  max_quantity: number;
  base_chance: number;      // 0-1
  rarity_modifier: number;  // Multiplier based on item rarity
  conditions?: DropCondition[];
}

export type DropCondition = 
  | { type: 'player_luck'; threshold: number }
  | { type: 'critical_hit'; }
  | { type: 'party_size'; min: number }
  | { type: 'first_kill'; }
  | { type: 'world_event'; event_id: string }
  | { type: 'time_of_day'; hour_range: [number, number] }
  | { type: 'weather'; weather_type: string }
  | { type: 'player_clout'; min: number }
  | { type: 'skill_level'; skill_id: string; level: number }
  | { type: 'world_first_kill'; }
  | { type: 'world_event_active'; event_id: string };

export interface MonsterLootTable {
  guaranteed: MonsterDrop[];      // Always dropped
  common: MonsterDrop[];          // High chance
  uncommon: MonsterDrop[];        // Medium chance
  rare: MonsterDrop[];            // Low chance
  epic: MonsterDrop[];            // Very low chance
  legendary: MonsterDrop[];       // Very low chance
  mythic: MonsterDrop[];          // Extremely low chance
  unique: MonsterDrop[];          // One per world (world first)
}

export interface Monster {
  id: string;
  name: string;
  title: string;
  tier: MonsterTier;
  type: MonsterType;
  behavior: MonsterBehavior;
  size: MonsterSize;
  stats: MonsterStats;
  ai: MonsterAI;
  loot_table: MonsterLootTable;
  xp_reward: number;
  clout_reward: number;
  soul_coin_reward: number;
  
  // Spawning
  spawn_zones: string[];           // Zone IDs where it spawns
  spawn_conditions: SpawnCondition[];
  respawn_time_base: number;      // seconds
  respawn_variance: number;       // +/- seconds
  max_population: number;         // Max simultaneous in zone
  
  // Visual
  sprite: string;
  scale: number;
  animations: Record<string, AnimationData>;
  color_variants: string[];       // Palette swap keys
  particle_effects?: string[];    // Ambient particles
  
  // Audio
  sound_idle?: string;
  sound_aggro?: string;
  sound_attack?: string;
  sound_death?: string;
  sound_hurt?: string;
  
  // Lore
  description: string;
  lore_entries: string[];         // Lore entry IDs unlocked on kill
  bestiary_entry: BestiaryEntry;
  
  // Scaling
  level_scaling: LevelScaling;
  
  // Social
  faction?: string;
  friendly_factions: string[];
  hostile_factions: string[];
  
  // Special
  is_world_boss: boolean;
  world_boss_event_id?: string;
  required_quest?: string;        // Quest required to spawn
  despawn_on_flee: boolean;
}

export interface AnimationData {
  frame_rate: number;
  frames: number;
  loop: boolean;
  offset?: { x: number; y: number };
}

export interface SpawnCondition {
  type: 'time_of_day' | 'weather' | 'world_event' | 'player_count' | 'quest_complete' | 'item_held' | 'custom';
  operator: 'eq' | 'neq' | 'gt' | 'gte' | 'lt' | 'lte' | 'between';
  value: string | number | [number, number];
}

export interface LevelScaling {
  enabled: boolean;
  base_level: number;
  level_per_tier: number;
  stat_multiplier_per_level: number; // e.g., 1.05 = 5% per level
  max_level: number;
  elite_chance: number; // Chance to spawn as elite (1.5x stats, better loot)
  champion_chance: number; // Champion (2x stats, unique mechanics)
}

export interface BestiaryEntry {
  id: string;
  monster_id: string;
  name: string;
  description: string;
  known_drops: string[];        // Item IDs player has seen drop
  kill_count: number;
  first_kill_date?: string;
  fastest_kill_time?: number;   // seconds
  largest_size_seen?: number;   // For size-variable monsters
  weaknesses_discovered: string[]; // Damage types
  behaviors_observed: string[]; // AI behaviors seen
  completion_percentage: number;
}

export interface MonsterSpawnPoint {
  id: string;
  monster_id: string;
  zone: string;
  x: number;
  y: number;
  radius: number;
  max_concurrent: number;
  respawn_timer: number;
  last_spawn: number;
  active: boolean;
  conditions: SpawnCondition[];
}

export interface MonsterInstance {
  instance_id: string;
  monster_id: string;
  spawn_point_id: string;
  x: number;
  y: number;
  current_health: number;
  max_health: number;
  level: number;
  stats: MonsterStats;
  ai_state: MonsterAIState;
  aggro_targets: AggroTarget[];
  summoned_by?: string; // instance_id of summoner
  spawned_at: number;
  last_attack: number;
  elite: boolean;
  champion: boolean;
  champion_variant?: string;
  custom_loot_modifiers?: Record<string, number>;
}

export interface MonsterAIState {
  current_behavior: MonsterBehavior;
  current_target?: string; // player instance_id
  patrol_index: number;
  last_action: number;
  cooldowns: Record<string, number>;
  enraged: boolean;
  phase: number;
  mechanics_used: Record<string, number>;
  flee_attempts: number;
  call_for_help_sent: boolean;
}

export interface AggroTarget {
  player_id: number;
  threat: number;
  last_damage_time: number;
  distance: number;
}

// Monster Drops by Tier (Reference Data)
export const MONSTER_TIER_DROP_RATES: Record<string, { hat_drop_chance: number; hat_rarity_weights: Record<string, number> }> = {
  ambient: { 
    hat_drop_chance: 0.001, 
    hat_rarity_weights: { noob: 0.9, common: 0.1 } 
  },
  common: { 
    hat_drop_chance: 0.05, 
    hat_rarity_weights: { common: 0.7, uncommon: 0.3 } 
  },
  uncommon: { 
    hat_drop_chance: 0.15, 
    hat_rarity_weights: { uncommon: 0.7, rare: 0.2, epic: 0.1 } 
  },
  rare: { 
    hat_drop_chance: 0.3, 
    hat_rarity_weights: { rare: 0.6, epic: 0.3, legendary: 0.1 } 
  },
  epic: { 
    hat_drop_chance: 0.5, 
    hat_rarity_weights: { epic: 0.6, legendary: 0.3, mythic: 0.1 } 
  },
  legendary: { 
    hat_drop_chance: 0.75, 
    hat_rarity_weights: { legendary: 0.7, mythic: 0.3 } 
  },
  mythic: { 
    hat_drop_chance: 1.0, 
    hat_rarity_weights: { mythic: 1.0 } 
  },
};

// Monster Definitions (Partial - for reference)
export const MONSTER_DEFINITIONS: Record<string, Partial<Monster>> = {
  // TIER 0 - AMBIENT
  'loch_minnow': {
    id: 'loch_minnow',
    name: 'Loch Minnow',
    title: 'The Ever-Present',
    tier: 'noob',
    type: 'fish',
    behavior: 'passive',
    size: 'tiny',
    stats: { health: 10, max_health: 10, armor: 0, resistance: {}, evasion: 0.8, accuracy: 0.3, critical_chance: 0, critical_multiplier: 1.5, damage_min: 1, damage_max: 2, attack_speed: 1, attack_range: 1, move_speed: 10, turn_speed: 180 },
    ai: { behavior: 'passive', aggro_range: 0, leash_range: 100, call_for_help_range: 0, flee_threshold: 0.2, enrage_threshold: 1.1, mechanics: [] },
    loot_table: { guaranteed: [], common: [{ item_id: 'hat-soggy-visor', min_quantity: 1, max_quantity: 1, base_chance: 0.01, rarity_modifier: 1 }], uncommon: [], rare: [], epic: [], legendary: [], mythic: [], unique: [] },
    xp_reward: 5,
    clout_reward: 1,
    soul_coin_reward: 1,
    spawn_zones: ['shallows'],
    spawn_conditions: [],
    respawn_time_base: 10,
    respawn_variance: 5,
    max_population: 100,
    sprite: 'monster-minnow',
    scale: 0.5,
    animations: { idle: { frame_rate: 8, frames: 4, loop: true } },
    color_variants: ['silver', 'gold', 'albino'],
    particle_effects: ['water-ripples'],
    sound_idle: 'sfx-fish-swim',
    sound_death: 'sfx-fish-splash',
    description: 'Tiny silver fish that swarm the shallows. Harmless but numerous.',
    lore_entries: ['bestiary-minnow'],
    bestiary_entry: { id: 'bestiary-minnow', monster_id: 'loch_minnow', name: 'Loch Minnow', description: 'The most common life in the Loch. They travel in massive schools and are the primary food source for almost everything larger.', known_drops: ['hat-soggy-visor', 'hat-plastic-horns'], kill_count: 0, weaknesses_discovered: [], behaviors_observed: ['schooling', 'fleeing'], completion_percentage: 0 },
    level_scaling: { enabled: false, base_level: 1, level_per_tier: 0, stat_multiplier_per_level: 1.0, max_level: 5, elite_chance: 0, champion_chance: 0 },
    is_world_boss: false,
    despawn_on_flee: true,
  },

  // TIER 1 - COMMON
  'loch_trout': {
    id: 'loch_trout',
    name: 'Loch Trout',
    title: 'The Angler\'s Prize',
    tier: 'common',
    type: 'fish',
    behavior: 'territorial',
    size: 'medium',
    stats: { health: 150, max_health: 150, armor: 10, resistance: { physical: 0.1, piercing: 0.05 }, evasion: 0.3, accuracy: 0.7, critical_chance: 0.05, critical_multiplier: 1.5, damage_min: 15, damage_max: 25, attack_speed: 1.2, attack_range: 2, move_speed: 8, turn_speed: 90 },
    ai: { behavior: 'territorial', aggro_range: 15, leash_range: 50, call_for_help_range: 10, flee_threshold: 0.15, enrage_threshold: 1.1, mechanics: [{ id: 'dash', name: 'Sudden Dash', description: 'Rapid burst of speed', trigger: { type: 'hp_threshold', parameters: { threshold: 0.5 } }, effect: { type: 'damage', target: 'player', parameters: { multiplier: 1.5 } }, cooldown: 15, warning_time: 1.5, telegraph: { type: 'visual', duration: 1.5, intensity: 0.8, data: { color: '#00ffff', sprite: 'telegraph-dash' } } }] },
    loot_table: { guaranteed: [{ item_id: 'fish_meat', min_quantity: 1, max_quantity: 3, base_chance: 1.0, rarity_modifier: 1 }], common: [{ item_id: 'hat-fisherman-cap', min_quantity: 1, max_quantity: 1, base_chance: 0.05, rarity_modifier: 1 }, { item_id: 'fish_scale', min_quantity: 2, max_quantity: 5, base_chance: 0.7, rarity_modifier: 1 }], uncommon: [{ item_id: 'hat-kelp-crown', min_quantity: 1, max_quantity: 1, base_chance: 0.02, rarity_modifier: 1 }], rare: [], epic: [], legendary: [], mythic: [], unique: [] },
    xp_reward: 75,
    clout_reward: 10,
    soul_coin_reward: 50,
    spawn_zones: ['shallows', 'standard'],
    spawn_conditions: [],
    respawn_time_base: 60,
    respawn_variance: 20,
    max_population: 20,
    sprite: 'monster-trout',
    scale: 1.0,
    animations: { idle: { frame_rate: 6, frames: 6, loop: true }, attack: { frame_rate: 12, frames: 4, loop: false }, dash: { frame_rate: 20, frames: 3, loop: false }, death: { frame_rate: 8, frames: 5, loop: false } },
    color_variants: ['silver', 'rainbow', 'golden', 'albino'],
    particle_effects: ['water-wake'],
    sound_idle: 'sfx-fish-swim',
    sound_aggro: 'sfx-fish-splash',
    sound_attack: 'sfx-fish-bite',
    sound_death: 'sfx-fish-flop',
    description: 'Territorial freshwater trout grown massive in the Loch\'s nutrient-rich waters. Prized by anglers for their Fisherman\'s Caps.',
    lore_entries: ['bestiary-trout'],
    bestiary_entry: { id: 'bestiary-trout', monster_id: 'loch_trout', name: 'Loch Trout', description: 'Aggressive territorial fish that patrol the shallows and standard depths. Their scales are prized for crafting Fisherman\'s Caps.', known_drops: ['hat-fisherman-cap', 'fish_scale', 'fish_meat'], kill_count: 0, weaknesses_discovered: [], behaviors_observed: ['territorial', 'dash_attack'], completion_percentage: 0 },
    level_scaling: { enabled: true, base_level: 5, level_per_tier: 2, stat_multiplier_per_level: 1.05, max_level: 20, elite_chance: 0.05, champion_chance: 0.01 },
    is_world_boss: false,
    despawn_on_flee: true,
  },

  // TIER 2 - UNCOMMON
  'giant_pike': {
    id: 'giant_pike',
    name: 'Giant Pike',
    title: 'The Water Wolf',
    tier: 'uncommon',
    type: 'fish',
    behavior: 'predatory',
    size: 'large',
    stats: { health: 800, max_health: 800, armor: 50, resistance: { physical: 0.2, piercing: 0.15, crushing: 0.1 }, evasion: 0.25, accuracy: 0.85, critical_chance: 0.15, critical_multiplier: 2.0, damage_min: 60, damage_max: 100, attack_speed: 0.8, attack_range: 4, move_speed: 6, turn_speed: 60 },
    ai: { behavior: 'predatory', aggro_range: 30, leash_range: 80, call_for_help_range: 20, flee_threshold: 0.1, enrage_threshold: 0.3, mechanics: [{ id: 'ambush_strike', name: 'Ambush Strike', description: 'Burst from hiding for massive damage', trigger: { type: 'player_action', parameters: { action: 'enter_territory' } }, effect: { type: 'damage', target: 'player', parameters: { multiplier: 3.0, bleed: true } }, cooldown: 30, warning_time: 2.0, telegraph: { type: 'visual', duration: 2.0, intensity: 0.9, data: { color: '#ff4444', sprite: 'telegraph-ambush' } } }, { id: 'tail_whip', name: 'Tail Whip', description: 'Wide knockback attack', trigger: { type: 'time_interval', parameters: { interval: 20 } }, effect: { type: 'knockback', target: 'area', parameters: { radius: 5, force: 10 } }, cooldown: 20, warning_time: 1.0, telegraph: { type: 'ground_marker', duration: 1.0, intensity: 0.8, data: { radius: 5, color: '#ff4444' } } }] },
    loot_table: { guaranteed: [{ item_id: 'pike_meat', min_quantity: 2, max_quantity: 5, base_chance: 1.0, rarity_modifier: 1 }, { item_id: 'pike_scale', min_quantity: 3, max_quantity: 8, base_chance: 0.9, rarity_modifier: 1 }], common: [{ item_id: 'hat-kelp-top-hat', min_quantity: 1, max_quantity: 1, base_chance: 0.08, rarity_modifier: 1 }, { item_id: 'hat-sub-captain-cap', min_quantity: 1, max_quantity: 1, base_chance: 0.05, rarity_modifier: 1 }], uncommon: [{ item_id: 'hat-coral-tiara', min_quantity: 1, max_quantity: 1, base_chance: 0.03, rarity_modifier: 1 }], rare: [{ item_id: 'hat-admiral-bicorn', min_quantity: 1, max_quantity: 1, base_chance: 0.01, rarity_modifier: 1 }], epic: [], legendary: [], mythic: [], unique: [] },
    xp_reward: 300,
    clout_reward: 40,
    soul_coin_reward: 500,
    spawn_zones: ['standard', 'deep'],
    spawn_conditions: [],
    respawn_time_base: 300,
    respawn_variance: 60,
    max_population: 5,
    sprite: 'monster-giant-pike',
    scale: 1.5,
    animations: { idle: { frame_rate: 4, frames: 4, loop: true }, attack: { frame_rate: 10, frames: 5, loop: false }, ambush: { frame_rate: 15, frames: 3, loop: false }, death: { frame_rate: 6, frames: 6, loop: false } },
    color_variants: ['green', 'red', 'albino', 'melanistic'],
    particle_effects: ['water-disturbance'],
    sound_idle: 'sfx-pike-swim',
    sound_aggro: 'sfx-pike-roar',
    sound_attack: 'sfx-pike-strike',
    sound_death: 'sfx-pike-thrash',
    description: 'Apex predator of the standard depths. The Pike strikes with lightning speed from concealed positions. Its scales make excellent armor.',
    lore_entries: ['bestiary-giant-pike'],
    bestiary_entry: { id: 'bestiary-giant-pike', monster_id: 'giant_pike', name: 'Giant Pike', description: 'The apex predator of the standard depths. Ambush predator that strikes from concealment. Its scales are prized for high-tier hat crafting.', known_drops: ['hat-kelp-top-hat', 'hat-sub-captain-cap', 'pike_scale', 'pike_meat'], kill_count: 0, weaknesses_discovered: [], behaviors_observed: ['ambush', 'territorial', 'bleed_attack'], completion_percentage: 0 },
    level_scaling: { enabled: true, base_level: 15, level_per_tier: 3, stat_multiplier_per_level: 1.06, max_level: 35, elite_chance: 0.1, champion_chance: 0.02 },
    is_world_boss: false,
    despawn_on_flee: true,
  },

  // TIER 3 - RARE
  'abyssal_anglerfish': {
    id: 'abyssal_anglerfish',
    name: 'Abyssal Anglerfish',
    title: 'The Light in the Dark',
    tier: 'rare',
    type: 'fish',
    behavior: 'ambush',
    size: 'large',
    stats: { health: 3000, max_health: 3000, armor: 150, resistance: { physical: 0.3, piercing: 0.2, crushing: 0.2, acid: 0.4, pressure: 0.5 }, evasion: 0.2, accuracy: 0.9, critical_chance: 0.2, critical_multiplier: 2.5, damage_min: 150, damage_max: 250, attack_speed: 0.6, attack_range: 6, move_speed: 3, turn_speed: 40 },
    ai: { behavior: 'ambush', aggro_range: 40, leash_range: 100, call_for_help_range: 50, flee_threshold: 0.05, enrage_threshold: 0.25, mechanics: [{ id: 'lure_hypnosis', name: 'Hypnotic Lure', description: 'Draws players toward its maw', trigger: { type: 'player_position', parameters: { radius: 10 } }, effect: { type: 'debuff', target: 'player', parameters: { type: 'hypnotized', duration: 3, pull_force: 2 } }, cooldown: 25, warning_time: 1.5, telegraph: { type: 'visual', duration: 2, intensity: 1.0, data: { color: '#ff00ff', sprite: 'telegraph-hypnosis' } } }, { id: 'ink_cloud', name: 'Ink Cloud', description: 'Blinds and poisons', trigger: { type: 'hp_threshold', parameters: { threshold: 0.4 } }, effect: { type: 'environment', target: 'area', parameters: { type: 'ink_cloud', radius: 8, duration: 10, poison: true, blind: true } }, cooldown: 45, warning_time: 1.0, telegraph: { type: 'screen_flash', duration: 0.5, intensity: 0.7, data: { color: '#1a001a' } } }] },
    loot_table: { guaranteed: [{ item_id: 'angler_lure', min_quantity: 1, max_quantity: 1, base_chance: 0.8, rarity_modifier: 1 }, { item_id: 'angler_ink', min_quantity: 2, max_quantity: 5, base_chance: 0.9, rarity_modifier: 1 }], common: [{ item_id: 'hat-kelp-top-hat', min_quantity: 1, max_quantity: 1, base_chance: 0.05, rarity_modifier: 1 }], uncommon: [{ item_id: 'hat-sub-captain-cap', min_quantity: 1, max_quantity: 1, base_chance: 0.05, rarity_modifier: 1 }, { item_id: 'hat-coral-tiara', min_quantity: 1, max_quantity: 1, base_chance: 0.03, rarity_modifier: 1 }], rare: [{ item_id: 'hat-admiral-bicorn', min_quantity: 1, max_quantity: 1, base_chance: 0.05, rarity_modifier: 1 }, { item_id: 'hat-pearl-fedora', min_quantity: 1, max_quantity: 1, base_chance: 0.03, rarity_modifier: 1 }], epic: [{ item_id: 'hat-plundered-captain-cap', min_quantity: 1, max_quantity: 1, base_chance: 0.01, rarity_modifier: 1 }], legendary: [], mythic: [], unique: [] },
    xp_reward: 1500,
    clout_reward: 100,
    soul_coin_reward: 2000,
    spawn_zones: ['deep', 'abyssal'],
    spawn_conditions: [{ type: 'time_of_day', operator: 'between', value: [20, 6] }], // Night only
    respawn_time_base: 1800,
    respawn_variance: 300,
    max_population: 2,
    sprite: 'monster-anglerfish',
    scale: 1.8,
    animations: { idle: { frame_rate: 3, frames: 2, loop: true }, attack: { frame_rate: 12, frames: 4, loop: false }, lure: { frame_rate: 2, frames: 6, loop: true }, death: { frame_rate: 5, frames: 7, loop: false } },
    color_variants: ['black', 'dark_blue', 'purple', 'bioluminescent'],
    particle_effects: ['bioluminescence', 'lure-glow'],
    sound_idle: 'sfx-angler-hum',
    sound_aggro: 'sfx-angler-click',
    sound_attack: 'sfx-angler-bite',
    sound_death: 'sfx-angler-collapse',
    description: 'A monstrous anglerfish that lures prey with bioluminescent bait. Its ink clouds the water, blinding and poisoning prey.',
    lore_entries: ['bestiary-anglerfish'],
    bestiary_entry: { id: 'bestiary-anglerfish', monster_id: 'abyssal_anglerfish', name: 'Abyssal Anglerfish', description: 'Deep-dwelling ambush predator using bioluminescent lure. Its ink clouds blind and poison. The lure itself is a prized crafting material.', known_drops: ['angler_lure', 'angler_ink', 'hat-admiral-bicorn', 'hat-plundered-captain-cap'], kill_count: 0, weaknesses_discovered: [], behaviors_observed: ['ambush', 'hypnosis', 'ink_cloud'], completion_percentage: 0 },
    level_scaling: { enabled: true, base_level: 35, level_per_tier: 4, stat_multiplier_per_level: 1.07, max_level: 55, elite_chance: 0.15, champion_chance: 0.03 },
    is_world_boss: false,
    despawn_on_flee: false,
  },

  // TIER 4 - EPIC
  'kraken_matriarch': {
    id: 'kraken_matriarch',
    name: 'Kraken Matriarch',
    title: 'Mother of the Deep',
    tier: 'epic',
    type: 'cephalopod',
    behavior: 'boss',
    size: 'colossal',
    stats: { health: 500000, max_health: 500000, armor: 500, resistance: { physical: 0.5, piercing: 0.4, crushing: 0.3, acid: 0.6, pressure: 0.8, sonic: 0.3 }, evasion: 0.1, accuracy: 0.95, critical_chance: 0.25, critical_multiplier: 3.0, damage_min: 500, damage_max: 1000, attack_speed: 0.3, attack_range: 50, move_speed: 2, turn_speed: 15 },
    ai: { behavior: 'boss', aggro_range: 200, leash_range: 500, call_for_help_range: 200, flee_threshold: 0.01, enrage_threshold: 0.3, mechanics: [
      { id: 'tentacle_slam', name: 'Tentacle Slam', description: 'Massive tentacle crushes area', trigger: { type: 'time_interval', parameters: { interval: 15 } }, effect: { type: 'damage', target: 'area', parameters: { radius: 15, damage: 500, knockback: 20 } }, cooldown: 15, warning_time: 3.0, telegraph: { type: 'ground_marker', duration: 3.0, intensity: 1.0, data: { radius: 15, color: '#4400ff' } } },
      { id: 'ink_storm', name: 'Ink Storm', description: 'Massive ink cloud blinds and damages', trigger: { type: 'hp_threshold', parameters: { threshold: 0.6 } }, effect: { type: 'environment', target: 'area', parameters: { type: 'ink_storm', radius: 50, duration: 30, damage_per_sec: 50, blind: true, slow: 0.5 } }, cooldown: 120, warning_time: 5.0, telegraph: { type: 'screen_flash', duration: 2.0, intensity: 1.0, data: { color: '#0a0022' } } },
      { id: 'summon_spawn', name: 'Summon Kraken Spawn', description: 'Calls forth smaller kraken', trigger: { type: 'hp_threshold', parameters: { threshold: 0.4 } }, effect: { type: 'summon', target: 'self', parameters: { monster_id: 'kraken_spawn', count: 4, radius: 30 } }, cooldown: 180, warning_time: 4.0, telegraph: { type: 'screen_flash', duration: 2.0, intensity: 0.8, data: { color: '#00aaff' } } },
      { id: 'tidal_wave', name: 'Tidal Wave', description: 'Massive wave pushes all players back', trigger: { type: 'hp_threshold', parameters: { threshold: 0.2 } }, effect: { type: 'knockback', target: 'all_players', parameters: { force: 50, distance: 50 } }, cooldown: 300, warning_time: 5.0, telegraph: { type: 'screen_flash', duration: 3.0, intensity: 1.0, data: { color: '#00ffff' } } },
    ]},
    loot_table: { guaranteed: [{ item_id: 'kraken_ink', min_quantity: 10, max_quantity: 20, base_chance: 1.0, rarity_modifier: 1 }, { item_id: 'kraken_tentacle', min_quantity: 2, max_quantity: 4, base_chance: 1.0, rarity_modifier: 1 }, { item_id: 'kraken_eye', min_quantity: 1, max_quantity: 1, base_chance: 1.0, rarity_modifier: 1 }], common: [], uncommon: [], rare: [{ item_id: 'hat-kraken-ink-stetson', min_quantity: 1, max_quantity: 1, base_chance: 0.1, rarity_modifier: 1 }], epic: [{ item_id: 'hat-abyssal-crown', min_quantity: 1, max_quantity: 1, base_chance: 0.05, rarity_modifier: 1 }], legendary: [{ item_id: 'hat-neptunes-trident-helm', min_quantity: 1, max_quantity: 1, base_chance: 0.01, rarity_modifier: 1 }], mythic: [], unique: [] },
    xp_reward: 100000,
    clout_reward: 5000,
    soul_coin_reward: 100000,
    spawn_zones: ['trench'],
    spawn_conditions: [{ type: 'world_event', operator: 'eq', value: 'kraken_awakens' }],
    respawn_time_base: 604800, // Weekly
    respawn_variance: 86400,
    max_population: 1,
    sprite: 'monster-kraken-matriarch',
    scale: 5.0,
    animations: { idle: { frame_rate: 2, frames: 4, loop: true }, attack: { frame_rate: 8, frames: 8, loop: false }, slam: { frame_rate: 10, frames: 6, loop: false }, ink: { frame_rate: 5, frames: 8, loop: false }, death: { frame_rate: 3, frames: 12, loop: false } },
    color_variants: ['deep_purple', 'abyssal_black', 'crimson', 'bioluminescent_blue'],
    particle_effects: ['ink_particles', 'pressure_waves', 'bioluminescence'],
    sound_idle: 'sfx-kraken-hum',
    sound_aggro: 'sfx-kraken-roar',
    sound_attack: 'sfx-kraken-slam',
    sound_death: 'sfx-kraken-scream',
    description: 'The ancient mother of all krakens. Her ink clouds the trench. Her tentacles crush submarines. Only the boldest dare challenge her.',
    lore_entries: ['bestiary-kraken-matriarch'],
    bestiary_entry: { id: 'bestiary-kraken-matriarch', monster_id: 'kraken_matriarch', name: 'Kraken Matriarch', description: 'Ancient cephalopod of immense size. Her ink clouds the trench for miles. Defeating her yields Kraken Ink — the rarest crafting catalyst.', known_drops: ['kraken_ink', 'kraken_tentacle', 'kraken_eye', 'hat-kraken-ink-stetson', 'hat-abyssal-crown', 'hat-neptunes-trident-helm'], kill_count: 0, weaknesses_discovered: [], behaviors_observed: ['tentacle_slam', 'ink_storm', 'summon_spawn', 'tidal_wave'], completion_percentage: 0 },
    level_scaling: { enabled: false, base_level: 70, level_per_tier: 0, stat_multiplier_per_level: 1.0, max_level: 70, elite_chance: 0, champion_chance: 0 },
    is_world_boss: true,
    world_boss_event_id: 'kraken_awakens',
    required_quest: 'act_viii_kraken_matriarch',
    despawn_on_flee: false,
  },

  // TIER 5 - LEGENDARY
  'nessie_adult': {
    id: 'nessie_adult',
    name: 'Nessie',
    title: 'The Loch\'s Guardian',
    tier: 'legendary',
    type: 'legendary_cryptid',
    behavior: 'boss',
    size: 'colossal',
    stats: { health: 2000000, max_health: 2000000, armor: 1000, resistance: { physical: 0.7, piercing: 0.6, crushing: 0.5, acid: 0.8, pressure: 0.9, sonic: 0.5, electric: 0.4, psychic: 0.3, void: 0.2 }, evasion: 0.15, accuracy: 0.98, critical_chance: 0.3, critical_multiplier: 3.5, damage_min: 2000, damage_max: 4000, attack_speed: 0.2, attack_range: 100, move_speed: 5, turn_speed: 10 },
    ai: { behavior: 'boss', aggro_range: 500, leash_range: 1000, call_for_help_range: 500, flee_threshold: 0, enrage_threshold: 0.2, mechanics: [
      { id: 'loch_surge', name: 'Loch Surge', description: 'Massive water wave damages entire zone', trigger: { type: 'hp_threshold', parameters: { threshold: 0.8 } }, effect: { type: 'damage', target: 'all_players', parameters: { damage: 1000, radius: 200, knockback: 50 } }, cooldown: 120, warning_time: 5.0, telegraph: { type: 'screen_flash', duration: 4.0, intensity: 1.0, data: { color: '#00ffff' } } },
      { id: 'ancient_roar', name: 'Ancient Roar', description: 'Sonic wave stuns and fears', trigger: { type: 'hp_threshold', parameters: { threshold: 0.5 } }, effect: { type: 'debuff', target: 'all_players', parameters: { type: 'stun', duration: 3, fear: true, silence: true } }, cooldown: 180, warning_time: 4.0, telegraph: { type: 'screen_flash', duration: 3.0, intensity: 1.0, data: { color: '#ffd700' } } },
      { id: 'summon_guardians', name: 'Summon Loch Guardians', description: 'Calls ancient protectors', trigger: { type: 'hp_threshold', parameters: { threshold: 0.3 } }, effect: { type: 'summon', target: 'self', parameters: { monster_id: 'loch_guardian', count: 3, radius: 50 } }, cooldown: 300, warning_time: 5.0, telegraph: { type: 'screen_flash', duration: 3.0, intensity: 1.0, data: { color: '#00ff88' } } },
      { id: 'reality_fracture', name: 'Reality Fracture', description: 'Tears space, teleports players', trigger: { type: 'hp_threshold', parameters: { threshold: 0.1 } }, effect: { type: 'teleport', target: 'all_players', parameters: { random: true, radius: 100 } }, cooldown: 300, warning_time: 5.0, telegraph: { type: 'screen_flash', duration: 3.0, intensity: 1.0, data: { color: '#ff00ff' } } },
    ]},
    loot_table: { guaranteed: [{ item_id: 'nessie_scale', min_quantity: 5, max_quantity: 10, base_chance: 1.0, rarity_modifier: 1 }, { item_id: 'nessie_essence', min_quantity: 3, max_quantity: 5, base_chance: 1.0, rarity_modifier: 1 }, { item_id: 'loch_water_pure', min_quantity: 1, max_quantity: 1, base_chance: 1.0, rarity_modifier: 1 }], common: [], uncommon: [], rare: [], epic: [{ item_id: 'hat-nessie-scale-crown', min_quantity: 1, max_quantity: 1, base_chance: 0.2, rarity_modifier: 1 }], legendary: [{ item_id: 'hat-nessies-crown', min_quantity: 1, max_quantity: 1, base_chance: 0.1, rarity_modifier: 1 }], mythic: [{ item_id: 'hat-liliths-crown', min_quantity: 1, max_quantity: 1, base_chance: 0.001, rarity_modifier: 1 }], unique: [] },
    xp_reward: 5000000,
    clout_reward: 100000,
    soul_coin_reward: 5000000,
    spawn_zones: ['trench'],
    spawn_conditions: [{ type: 'quest_complete', operator: 'eq', value: 'act_xi_queens_audience' }],
    respawn_time_base: 2592000, // Monthly
    respawn_variance: 604800,
    max_population: 1,
    sprite: 'monster-nessie',
    scale: 8.0,
    animations: { idle: { frame_rate: 1, frames: 8, loop: true }, surge: { frame_rate: 5, frames: 12, loop: false }, roar: { frame_rate: 3, frames: 8, loop: false }, death: { frame_rate: 1, frames: 20, loop: false } },
    color_variants: ['ancient_green', 'loch_blue', 'golden', 'prismatic'],
    particle_effects: ['water-caustics-mega', 'divine-aura', 'reality-distortion'],
    sound_idle: 'sfx-nessie-hum',
    sound_aggro: 'sfx-nessie-roar',
    sound_attack: 'sfx-nessie-surge',
    sound_death: 'sfx-nessie-farewell',
    description: 'The Guardian of the Loch. Ancient beyond measure. She watches. She judges. She crowns.',
    lore_entries: ['bestiary-nessie', 'lore-nessie-origin', 'lore-nessie-crown'],
    bestiary_entry: { id: 'bestiary-nessie', monster_id: 'nessie_adult', name: 'Nessie', description: 'The eternal guardian of the Loch. Her scales hold the history of the deep. To face her is to face the Loch itself.', known_drops: ['nessie_scale', 'nessie_essence', 'loch_water_pure', 'hat-nessie-scale-crown', 'hat-nessies-crown', 'hat-liliths-crown'], kill_count: 0, weaknesses_discovered: [], behaviors_observed: ['loch_surge', 'ancient_roar', 'summon_guardians', 'reality_fracture'], completion_percentage: 0 },
    level_scaling: { enabled: false, base_level: 100, level_per_tier: 0, stat_multiplier_per_level: 1.0, max_level: 100, elite_chance: 0, champion_chance: 0 },
    is_world_boss: true,
    world_boss_event_id: 'liliths_feast',
    required_quest: 'act_xi_queens_audience',
    despawn_on_flee: false,
  },

  // TIER 6 - MYTHIC
  'lilith_true': {
    id: 'lilith_true',
    name: 'Lilith',
    title: 'Queen of the Sephirotic Court',
    tier: 'mythic',
    type: 'divine',
    behavior: 'world_boss',
    size: 'colossal',
    stats: { health: 50000000, max_health: 50000000, armor: 5000, resistance: { physical: 0.95, piercing: 0.9, crushing: 0.85, acid: 0.95, pressure: 1.0, sonic: 0.9, electric: 0.95, psychic: 0.99, void: 0.9 }, evasion: 0.25, accuracy: 1.0, critical_chance: 0.5, critical_multiplier: 5.0, damage_min: 10000, damage_max: 20000, attack_speed: 0.1, attack_range: 1000, move_speed: 10, turn_speed: 5 },
    ai: { behavior: 'world_boss', aggro_range: 5000, leash_range: 5000, call_for_help_range: 5000, flee_threshold: 0, enrage_threshold: 0, mechanics: [
      { id: 'sephirotic_judgment', name: 'Sephirotic Judgment', description: 'Instantly executes unworthy', trigger: { type: 'hp_threshold', parameters: { threshold: 0.9 } }, effect: { type: 'damage', target: 'all_players', parameters: { execute_threshold: 0.1, damage: 999999 } }, cooldown: 300, warning_time: 10.0, telegraph: { type: 'screen_flash', duration: 8.0, intensity: 1.0, data: { color: '#ffffff' } } },
      { id: 'reality_rewrite', name: 'Reality Rewrite', description: 'Changes the rules of the fight', trigger: { type: 'hp_threshold', parameters: { threshold: 0.7 } }, effect: { type: 'custom', target: 'environment', parameters: { rewrite_type: 'random', duration: 60 } }, cooldown: 240, warning_time: 8.0, telegraph: { type: 'screen_flash', duration: 5.0, intensity: 1.0, data: { color: '#ff00ff' } } },
      { id: 'court_summon', name: 'Court of Ten', description: 'Summons the Sephirotic Court', trigger: { type: 'hp_threshold', parameters: { threshold: 0.5 } }, effect: { type: 'summon', target: 'self', parameters: { monster_id: 'sephirotic_archon', count: 10, radius: 100 } }, cooldown: 600, warning_time: 10.0, telegraph: { type: 'screen_flash', duration: 5.0, intensity: 1.0, data: { color: '#ffd700' } } },
      { id: 'abyssal_collapse', name: 'Abyssal Collapse', description: 'The Loch itself turns against you', trigger: { type: 'hp_threshold', parameters: { threshold: 0.2 } }, effect: { type: 'environment', target: 'all_players', parameters: { type: 'abyssal_collapse', damage_per_sec: 1000, reality_damage: true } }, cooldown: 300, warning_time: 8.0, telegraph: { type: 'screen_flash', duration: 4.0, intensity: 1.0, data: { color: '#0a001a' } } },
    ]},
    loot_table: { guaranteed: [{ item_id: 'lilith_tear', min_quantity: 1, max_quantity: 3, base_chance: 1.0, rarity_modifier: 1 }, { item_id: 'lilith_essence', min_quantity: 10, max_quantity: 20, base_chance: 1.0, rarity_modifier: 1 }, { item_id: 'sephirotic_fragment', min_quantity: 5, max_quantity: 10, base_chance: 1.0, rarity_modifier: 1 }, { item_id: 'the_ledger_page', min_quantity: 1, max_quantity: 1, base_chance: 1.0, rarity_modifier: 1 }], common: [], uncommon: [], rare: [], epic: [], legendary: [{ item_id: 'hat-liliths-crown', min_quantity: 1, max_quantity: 1, base_chance: 0.5, rarity_modifier: 1 }], mythic: [{ item_id: 'hat-liliths-crown', min_quantity: 1, max_quantity: 1, base_chance: 1.0, rarity_modifier: 1 }], unique: [{ item_id: 'hat-liliths-crown', min_quantity: 1, max_quantity: 1, base_chance: 1.0, rarity_modifier: 1 }] },
    xp_reward: 100000000,
    clout_reward: 1000000,
    soul_coin_reward: 100000000,
    spawn_zones: ['throne_room'],
    spawn_conditions: [{ type: 'quest_complete', operator: 'eq', value: 'act_xii_eternal_exchange' }],
    respawn_time_base: 31536000, // Yearly
    respawn_variance: 2592000,
    max_population: 1,
    sprite: 'monster-lilith',
    scale: 10.0,
    animations: { idle: { frame_rate: 0.5, frames: 12, loop: true }, judgment: { frame_rate: 5, frames: 16, loop: false }, rewrite: { frame_rate: 3, frames: 12, loop: false }, death: { frame_rate: 1, frames: 30, loop: false } },
    color_variants: ['prismatic', 'cosmic', 'void', 'golden'],
    particle_effects: ['reality-distortion', 'divine-light', 'sephirotic-rings', 'abyssal-shadow'],
    sound_idle: 'sfx-lilith-hum',
    sound_aggro: 'sfx-lilith-decree',
    sound_attack: 'sfx-lilith-judgment',
    sound_death: 'sfx-lilith-transcendence',
    description: 'The Queen. The Architect. The Sceptre-bearer. She does not fight. She judges.',
    lore_entries: ['bestiary-lilith', 'lore-lilith-origin', 'lore-lilith-crown', 'lore-abyssal-saga-complete'],
    bestiary_entry: { id: 'bestiary-lilith', monster_id: 'lilith_true', name: 'Lilith', description: 'The Queen of the Sephirotic Court. The Architect of the Abyssal Exchange. She does not fight. She judges. To face her is to face the sum of all your choices.', known_drops: ['lilith_tear', 'lilith_essence', 'sephirotic_fragment', 'the_ledger_page', 'hat-liliths-crown'], kill_count: 0, weaknesses_discovered: [], behaviors_observed: ['sephirotic_judgment', 'reality_rewrite', 'court_summon', 'abyssal_collapse'], completion_percentage: 0 },
    level_scaling: { enabled: false, base_level: 200, level_per_tier: 0, stat_multiplier_per_level: 1.0, max_level: 200, elite_chance: 0, champion_chance: 0 },
    is_world_boss: true,
    world_boss_event_id: 'liliths_feast',
    required_quest: 'act_xii_eternal_exchange',
    despawn_on_flee: false,
  },
};