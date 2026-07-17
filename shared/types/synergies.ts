// Shared types for Abyssal Assets - Skill Synergies & Combinations
import { SkillId } from './skills';

export interface SkillSynergy {
  id: string;
  name: string;
  description: string;
  skills: SkillId[];                  // 2 or more skills
  min_levels: [number, number] | Record<string, number>; // Minimum levels required
  bonus_type: SynergyBonusType;
  value: number;                      // Percentage or flat value
  condition?: SynergyCondition;
  visual_effect?: string;             // Particle/shader effect when active
}

export type SynergyBonusType = 
  | 'xp_boost'              // +% XP gain in both skills
  | 'drop_rate'             // +% rare drop chance
  | 'success_rate'          // +% craft/enchant/dredge success
  | 'speed'                 // +% action speed
  | 'quality'               // +% quality roll
  | 'efficiency'            // -% resource cost / time
  | 'damage'                // +% damage
  | 'crit_chance'           // +% crit chance
  | 'crit_multiplier'       // +% crit multiplier
  | 'damage_reduction'      // -% damage taken
  | 'evasion'               // +% dodge chance
  | 'resource_yield'        // +% materials from gathering
  | 'market_fee_reduction'  // -% market fees
  | 'stamina_regen'         // + stamina regen
  | 'essence_regen'         // + essence regen
  | 'oxygen_conservation'   // -% oxygen consumption
  | 'pressure_resistance'   // +% pressure resistance
  | 'sanity_preservation'   // -% sanity drain
  | 'rare_drop_chance'      // +% rare drop chance
  | 'double_loot_chance'    // +% chance for double loot
  | 'auto_loot'             // Auto-loot radius
  | 'craft_quality'         // +% quality roll
  | 'enchant_success'       // +% enchant success
  | 'transmute_preserve'    // Preserve rarity on transmute
  | 'essence_regen'         // + essence regen
  | 'transmute_cost'        // -% transmute cost
  | 'rarity_preservation'   // Preserve rarity on transmute
  | 'market_insight'        // See hidden market data
  | 'auction_duration'      // + listing duration
  | 'search_range'          // + search radius
  | 'party_xp_share'        // +% party XP share
  | 'party_drop_share'      // +% party drop share
  | 'revive_speed'          // +% revive speed
  | 'oxygen_conservation'   // -% oxygen use
  | 'pressure_immunity'     // Immune to pressure damage
  | 'sanity_shield'         // Sanity shield
  | 'reality_anchor'        // Reality distortion resistance
  | 'fate_weave'            // See fate threads
  | 'temporal_echo'         // See past/future echoes
  | 'discovery'             // Discover new things
  | 'negotiation_bonus'     // Bartering bonuses
  | 'endurance'             // Max endurance/stamina bonuses
  | 'craft_speed'           // Action speed in crafting
  | 'shared_liquidity'      // Guild economy sharing
  | 'invincibility'         // Absolute damage immunity
  | 'market_control'        // Dominate prices/fees
  | 'omega_state'          // Ascension ultimate form
  | 'fee_reduction'
  | 'pacify'
  | 'party_efficiency'
  | 'stamina'
  | 'reposition';

export interface SynergyCondition {
  type: 'both_above' | 'either_above' | 'sum_above' | 'difference_below' | 'product_above' | 'ratio_above' | 'all_above';
  threshold: number;
}

export interface SkillCombo {
  id: string;
  name: string;
  description: string;
  skills: SkillId[];              // 3+ skills
  min_levels: Record<string, number>;
  active_effect: ComboEffect;
  passive_effects: ComboEffect[];
  visual: ComboVisual;
}

export interface ComboEffect {
  type: ComboEffectType;
  value: number;
  targets: ComboTarget[];
  duration?: number;              // 0 = permanent while conditions met
  cooldown?: number;
}

export type ComboEffectType = 
  | 'stat_bonus'
  | 'unlock_ability'
  | 'unlock_recipe'
  | 'unlock_zone'
  | 'unlock_monster'
  | 'unlock_quest'
  | 'aura'
  | 'transformation'
  | 'passive_income'
  | 'reality_anchor'
  | 'fate_weave'
  | 'echo_chamber'
  | 'discovery'
  | 'quality'
  | 'resource_yield'
  | 'craft_speed'
  | 'efficiency'
  | 'damage'
  | 'evasion'
  | 'crit_chance'
  | 'market_control'
  | 'omega_state'
  | 'divine_insight'
  | 'reality_author'
  | 'market_insight'
  | 'rare_drop_chance'
  | 'craft_quality'
  | 'enchant_success'
  | 'rarity_preservation'
  | 'market_fee_reduction';

export type ComboTarget = 'self' | 'party' | 'guild' | 'zone' | 'global' | 'market' | 'monster' | 'item';

export interface ComboVisual {
  particle_effect?: string;
  shader?: string;
  aura_color?: string;
  title_prefix?: string;
  title_suffix?: string;
  title_color?: string;
}

export interface ActiveSynergy {
  synergy_id: string;
  skill_a: SkillId;
  skill_b: SkillId;
  level_a: number;
  level_b: number;
  active: boolean;
  uptime: number;          // Percentage of time active
  total_bonus: number;     // Computed bonus value
}

export interface SkillTree {
  skill_id: SkillId;
  nodes: SkillNode[];
  connections: SkillConnection[];
}

export interface SkillNode {
  id: string;
  skill_id: SkillId;
  level: number;
  x: number;
  y: number;
  type: 'core' | 'branch' | 'mastery' | 'ultimate' | 'synergy';
  unlocks: string[];        // Node IDs unlocked by this
  prerequisites: string[];  // Node IDs required
  icon: string;
  color: string;
  tooltip: string;
}

export interface SkillConnection {
  from: string;
  to: string;
  type: 'prerequisite' | 'synergy' | 'upgrade' | 'branch';
  style?: 'solid' | 'dashed' | 'dotted' | 'glowing';
}

// ============================================================================
// PREDEFINED SYNERGIES (All 2-Skill Combinations)
// ============================================================================

export const PREDEFINED_SYNERGIES: SkillSynergy[] = [
  // GATHERING + GATHERING
  {
    id: 'dredging_salvaging',
    name: 'Deep Recovery',
    description: 'Your dredge pulls up more from wrecks. The deep gives back what it took.',
    skills: ['dredging', 'salvaging'],
    min_levels: [30, 30],
    bonus_type: 'resource_yield',
    value: 25,
    condition: { type: 'both_above', threshold: 30 },
    visual_effect: 'salvage-glow',
  },
  {
    id: 'dredging_foraging',
    name: 'Kelp-Dredge Symbiosis',
    description: 'Your dredge pulls up living kelp. The forest feeds the depths.',
    skills: ['dredging', 'foraging'],
    min_levels: [20, 20],
    bonus_type: 'resource_yield',
    value: 15,
    condition: { type: 'both_above', threshold: 20 },
    visual_effect: 'kelp-particles',
  },
  {
    id: 'dredging_hunting',
    name: 'Apex Dredger',
    description: 'Your dredge attracts the beasts. They come to you.',
    skills: ['dredging', 'hunting'],
    min_levels: [50, 50],
    bonus_type: 'rare_drop_chance',
    value: 40,
    condition: { type: 'both_above', threshold: 50 },
    visual_effect: 'blood-in-water',
  },
  {
    id: 'dredging_navigation',
    name: 'The Charted Deep',
    description: 'Your charts reveal the dredge spots others miss.',
    skills: ['dredging', 'navigation'],
    min_levels: [30, 30],
    bonus_type: 'efficiency',
    value: 20,
    condition: { type: 'both_above', threshold: 30 },
    visual_effect: 'sonar-ping',
  },
  {
    id: 'salvaging_foraging',
    name: 'Wreck-Forest Cycle',
    description: 'Wrecks feed the forest. The forest feeds the wrecks.',
    skills: ['salvaging', 'foraging'],
    min_levels: [25, 25],
    bonus_type: 'resource_yield',
    value: 20,
    condition: { type: 'both_above', threshold: 25 },
    visual_effect: 'kelp-on-wreck',
  },
  {
    id: 'salvaging_hunting',
    name: 'Scavenger\'s Feast',
    description: 'The hunted leave more behind. Waste not.',
    skills: ['salvaging', 'hunting'],
    min_levels: [40, 40],
    bonus_type: 'resource_yield',
    value: 30,
    condition: { type: 'both_above', threshold: 40 },
    visual_effect: 'bone-glint',
  },
  {
    id: 'salvaging_navigation',
    name: 'The Wreck Mapper',
    description: 'Your charts show every wreck. None escape your net.',
    skills: ['salvaging', 'navigation'],
    min_levels: [35, 35],
    bonus_type: 'efficiency',
    value: 25,
    condition: { type: 'both_above', threshold: 35 },
    visual_effect: 'wreck-marker',
  },
  {
    id: 'foraging_hunting',
    name: 'The Forest Hunter',
    description: 'You hunt where the kelp grows thick. The forest provides.',
    skills: ['foraging', 'hunting'],
    min_levels: [30, 30],
    bonus_type: 'rare_drop_chance',
    value: 25,
    condition: { type: 'both_above', threshold: 30 },
    visual_effect: 'kelp-camouflage',
  },
  {
    id: 'foraging_navigation',
    name: 'The Kelp Cartographer',
    description: 'Your maps show every kelp bed, every hidden grove.',
    skills: ['foraging', 'navigation'],
    min_levels: [25, 25],
    bonus_type: 'efficiency',
    value: 20,
    condition: { type: 'both_above', threshold: 25 },
    visual_effect: 'kelp-map',
  },
  {
    id: 'hunting_navigation',
    name: 'The Tracker\'s Chart',
    description: 'Your maps show every lair, every trail. Nothing hides.',
    skills: ['hunting', 'navigation'],
    min_levels: [40, 40],
    bonus_type: 'efficiency',
    value: 30,
    condition: { type: 'both_above', threshold: 40 },
    visual_effect: 'trail-map',
  },

  // GATHERING + PROCESSING
  {
    id: 'dredging_salvage_processing',
    name: 'Direct to Forge',
    description: 'Your dredge feeds the furnace. No middleman.',
    skills: ['dredging', 'salvage_processing'],
    min_levels: [40, 40],
    bonus_type: 'efficiency',
    value: 30,
    condition: { type: 'both_above', threshold: 40 },
    visual_effect: 'ore-to-ingot',
  },
  {
    id: 'salvaging_salvage_processing',
    name: 'Perfect Recovery',
    description: 'Nothing wasted. Every bolt, every plate, recovered.',
    skills: ['salvaging', 'salvage_processing'],
    min_levels: [50, 50],
    bonus_type: 'efficiency',
    value: 40,
    condition: { type: 'both_above', threshold: 50 },
    visual_effect: 'perfect-recovery',
  },
  {
    id: 'foraging_fiber_working',
    name: 'Living Thread',
    description: 'The kelp spins itself. Your fingers barely guide it.',
    skills: ['foraging', 'fiber_working'],
    min_levels: [30, 30],
    bonus_type: 'efficiency',
    value: 25,
    condition: { type: 'both_above', threshold: 30 },
    visual_effect: 'auto-spin',
  },
  {
    id: 'hunting_bone_carving',
    name: 'Bone to Art',
    description: 'Every bone tells a story. You listen with your knives.',
    skills: ['hunting', 'bone_carving'],
    min_levels: [40, 40],
    bonus_type: 'quality',
    value: 30,
    condition: { type: 'both_above', threshold: 40 },
    visual_effect: 'bone-glow',
  },
  {
    id: 'salvaging_metallurgy',
    name: 'Sunken Steel',
    description: 'The deep\'s steel is purest. Your furnace knows its secrets.',
    skills: ['salvaging', 'metallurgy'],
    min_levels: [50, 50],
    bonus_type: 'quality',
    value: 25,
    condition: { type: 'both_above', threshold: 50 },
    visual_effect: 'pure-steel',
  },
  {
    id: 'foraging_fiber_working',
    name: 'Living Thread',
    description: 'The kelp spins itself. Your fingers barely guide it.',
    skills: ['foraging', 'fiber_working'],
    min_levels: [30, 30],
    bonus_type: 'efficiency',
    value: 25,
    condition: { type: 'both_above', threshold: 30 },
    visual_effect: 'auto-spin',
  },

  // PROCESSING + CRAFTING
  {
    id: 'salvage_processing_haberdashery',
    name: 'Wreck-Wear',
    description: 'Hats from the deep. The drowned would be proud.',
    skills: ['salvage_processing', 'haberdashery'],
    min_levels: [40, 40],
    bonus_type: 'quality',
    value: 20,
    condition: { type: 'both_above', threshold: 40 },
    visual_effect: 'wreck-hat',
  },
  {
    id: 'fiber_working_haberdashery',
    name: 'Living Thread',
    description: 'The kelp spins itself. Your fingers barely guide it.',
    skills: ['fiber_working', 'haberdashery'],
    min_levels: [30, 30],
    bonus_type: 'quality',
    value: 25,
    condition: { type: 'both_above', threshold: 30 },
    visual_effect: 'living-thread',
  },
  {
    id: 'bone_carving_haberdashery',
    name: 'Bone Crown',
    description: 'Crowns from the deep. The dead wear them well.',
    skills: ['bone_carving', 'haberdashery'],
    min_levels: [50, 50],
    bonus_type: 'quality',
    value: 30,
    condition: { type: 'both_above', threshold: 50 },
    visual_effect: 'bone-crown',
  },
  {
    id: 'metallurgy_haberdashery',
    name: 'Forged Crown',
    description: 'Steel sings under your hammer. The brim rings true.',
    skills: ['metallurgy', 'haberdashery'],
    min_levels: [50, 50],
    bonus_type: 'quality',
    value: 25,
    condition: { type: 'both_above', threshold: 50 },
    visual_effect: 'steel-ring',
  },

  // CRAFTING + CRAFTING
  {
    id: 'haberdashery_enchanting',
    name: 'Woven Magic',
    description: 'Thread and spell intertwine. The stitch holds the spell.',
    skills: ['haberdashery', 'enchanting'],
    min_levels: [50, 50],
    bonus_type: 'enchant_success',
    value: 25,
    condition: { type: 'both_above', threshold: 50 },
    visual_effect: 'magic-stitch',
  },
  {
    id: 'haberdashery_alchemy',
    name: 'Transmuted Thread',
    description: 'Thread becomes gold. The brim holds transmutation.',
    skills: ['haberdashery', 'alchemy'],
    min_levels: [50, 50],
    bonus_type: 'quality',
    value: 20,
    condition: { type: 'both_above', threshold: 50 },
    visual_effect: 'gold-thread',
  },
  {
    id: 'haberdashery_runecrafting',
    name: 'Runic Brim',
    description: 'Runes woven into the weave. Reality bends at the brim.',
    skills: ['haberdashery', 'runecrafting'],
    min_levels: [60, 60],
    bonus_type: 'quality',
    value: 30,
    condition: { type: 'both_above', threshold: 60 },
    visual_effect: 'runic-thread',
  },
  {
    id: 'enchanting_alchemy',
    name: 'Potent Thread',
    description: 'Potions in the stitch. The hat drinks the magic.',
    skills: ['enchanting', 'alchemy'],
    min_levels: [50, 50],
    bonus_type: 'enchant_success',
    value: 25,
    condition: { type: 'both_above', threshold: 50 },
    visual_effect: 'potion-stitch',
  },
  {
    id: 'enchanting_runecrafting',
    name: 'Runic Enchantment',
    description: 'Runes hold the enchantment. The magic never fades.',
    skills: ['enchanting', 'runecrafting'],
    min_levels: [60, 60],
    bonus_type: 'enchant_success',
    value: 35,
    condition: { type: 'both_above', threshold: 60 },
    visual_effect: 'permanent-rune',
  },
  {
    id: 'alchemy_runecrafting',
    name: 'Philosopher\'s Brim',
    description: 'Gold into lead into legend. The hat transcends matter.',
    skills: ['alchemy', 'runecrafting'],
    min_levels: [70, 70],
    bonus_type: 'transmute_preserve',
    value: 50,
    condition: { type: 'both_above', threshold: 70 },
    visual_effect: 'philosopher-brim',
  },
  {
    id: 'alchemy_haberdashery',
    name: 'Transmuted Thread',
    description: 'Thread becomes gold. The brim holds transmutation.',
    skills: ['alchemy', 'haberdashery'],
    min_levels: [50, 50],
    bonus_type: 'quality',
    value: 20,
    condition: { type: 'both_above', threshold: 50 },
    visual_effect: 'gold-thread',
  },
  {
    id: 'runecrafting_haberdashery',
    name: 'Runic Brim',
    description: 'Runes woven into the weave. Reality bends at the brim.',
    skills: ['runecrafting', 'haberdashery'],
    min_levels: [60, 60],
    bonus_type: 'quality',
    value: 30,
    condition: { type: 'both_above', threshold: 60 },
    visual_effect: 'runic-thread',
  },
  {
    id: 'masterwork_haberdashery',
    name: 'The Perfect Hat',
    description: 'Every stitch perfect. Every thread purposeful. Legendary.',
    skills: ['masterwork', 'haberdashery'],
    min_levels: [80, 80],
    bonus_type: 'quality',
    value: 50,
    condition: { type: 'both_above', threshold: 80 },
    visual_effect: 'perfect-hat',
  },
  {
    id: 'masterwork_enchanting',
    name: 'Eternal Enchantment',
    description: 'The enchantment never fades. Forever woven.',
    skills: ['masterwork', 'enchanting'],
    min_levels: [85, 85],
    bonus_type: 'enchant_success',
    value: 50,
    condition: { type: 'both_above', threshold: 85 },
    visual_effect: 'eternal-enchant',
  },
  {
    id: 'masterwork_alchemy',
    name: 'Philosopher\'s Crown',
    description: 'Gold becomes legend. The crown transcends value.',
    skills: ['masterwork', 'alchemy'],
    min_levels: [85, 85],
    bonus_type: 'transmute_preserve',
    value: 50,
    condition: { type: 'both_above', threshold: 85 },
    visual_effect: 'philosopher-crown',
  },
  {
    id: 'masterwork_runecrafting',
    name: 'World-Rune Crown',
    description: 'Reality inscribed. The crown rewrites the world.',
    skills: ['masterwork', 'runecrafting'],
    min_levels: [85, 85],
    bonus_type: 'rarity_preservation',
    value: 100,
    condition: { type: 'both_above', threshold: 85 },
    visual_effect: 'world-rune',
  },

  // CRAFTING + KNOWLEDGE
  {
    id: 'haberdashery_lore',
    name: 'Lore-Woven',
    description: 'Every stitch tells a story. The hat remembers.',
    skills: ['haberdashery', 'lore'],
    min_levels: [40, 40],
    bonus_type: 'quality',
    value: 15,
    condition: { type: 'both_above', threshold: 40 },
    visual_effect: 'lore-thread',
  },
  {
    id: 'enchanting_lore',
    name: 'Lore-Enchanted',
    description: 'Ancient words in modern weave. Power from the past.',
    skills: ['enchanting', 'lore'],
    min_levels: [50, 50],
    bonus_type: 'enchant_success',
    value: 20,
    condition: { type: 'both_above', threshold: 50 },
    visual_effect: 'ancient-rune',
  },
  {
    id: 'alchemy_lore',
    name: 'Ancient Formula',
    description: 'Lost recipes rediscovered. The old ways work best.',
    skills: ['alchemy', 'lore'],
    min_levels: [50, 50],
    bonus_type: 'discovery',
    value: 30,
    condition: { type: 'both_above', threshold: 50 },
    visual_effect: 'ancient-tome',
  },
  {
    id: 'runecrafting_lore',
    name: 'Ancient Runes',
    description: 'Runes from before the Loch. Power older than memory.',
    skills: ['runecrafting', 'lore'],
    min_levels: [60, 60],
    bonus_type: 'discovery',
    value: 40,
    condition: { type: 'both_above', threshold: 60 },
    visual_effect: 'ancient-rune-glow',
  },
  {
    id: 'runecrafting_scholarship',
    name: 'Wisdom Inscribed',
    description: 'Wisdom becomes rune. The brim thinks.',
    skills: ['runecrafting', 'scholarship'],
    min_levels: [70, 70],
    bonus_type: 'discovery',
    value: 50,
    condition: { type: 'both_above', threshold: 70 },
    visual_effect: 'wise-rune',
  },
  {
    id: 'alchemy_scholarship',
    name: 'Philosopher\'s Wisdom',
    description: 'Knowledge transmuted. The formula perfects itself.',
    skills: ['alchemy', 'scholarship'],
    min_levels: [70, 70],
    bonus_type: 'discovery',
    value: 40,
    condition: { type: 'both_above', threshold: 70 },
    visual_effect: 'wise-formula',
  },
  {
    id: 'sonar_tuning_lore',
    name: 'Echoes of the Past',
    description: 'The sonar hears echoes of the past. History in the ping.',
    skills: ['sonar_tuning', 'lore'],
    min_levels: [40, 40],
    bonus_type: 'efficiency',
    value: 20,
    condition: { type: 'both_above', threshold: 40 },
    visual_effect: 'echo-ping',
  },
  {
    id: 'sonar_tuning_scholarship',
    name: 'Calculated Ping',
    description: 'Mathematics perfects the ping. Precision absolute.',
    skills: ['sonar_tuning', 'scholarship'],
    min_levels: [50, 50],
    bonus_type: 'efficiency',
    value: 25,
    condition: { type: 'both_above', threshold: 50 },
    visual_effect: 'math-ping',
  },

  // CRAFTING + SOCIAL/ECONOMIC
  {
    id: 'haberdashery_trading',
    name: 'Market Hatter',
    description: 'You know what sells. The market bends to your brim.',
    skills: ['haberdashery', 'trading'],
    min_levels: [40, 40],
    bonus_type: 'market_fee_reduction',
    value: 20,
    condition: { type: 'both_above', threshold: 40 },
    visual_effect: 'market-hat',
  },
  {
    id: 'haberdashery_negotiation',
    name: 'Hatter\'s Tongue',
    description: 'Your hats speak for themselves. And so do you.',
    skills: ['haberdashery', 'negotiation'],
    min_levels: [40, 40],
    bonus_type: 'negotiation_bonus',
    value: 25,
    condition: { type: 'both_above', threshold: 40 },
    visual_effect: 'silver-tongue',
  },
  {
    id: 'enchanting_trading',
    name: 'Enchanted Market',
    description: 'Magic sells itself. You just set the price.',
    skills: ['enchanting', 'trading'],
    min_levels: [50, 50],
    bonus_type: 'market_fee_reduction',
    value: 15,
    condition: { type: 'both_above', threshold: 50 },
    visual_effect: 'magic-market',
  },
  {
    id: 'runecrafting_trading',
    name: 'Runic Commerce',
    description: 'Runes that sell themselves. The market reads itself.',
    skills: ['runecrafting', 'trading'],
    min_levels: [60, 60],
    bonus_type: 'market_insight',
    value: 30,
    condition: { type: 'both_above', threshold: 60 },
    visual_effect: 'runic-market',
  },
  {
    id: 'alchemy_trading',
    name: 'Transmuted Profit',
    description: 'Lead to gold. The market is your crucible.',
    skills: ['alchemy', 'trading'],
    min_levels: [50, 50],
    bonus_type: 'market_fee_reduction',
    value: 20,
    condition: { type: 'both_above', threshold: 50 },
    visual_effect: 'gold-market',
  },

  // KNOWLEDGE + KNOWLEDGE
  {
    id: 'lore_scholarship',
    name: 'Wisdom of Ages',
    description: 'Knowledge compounds. Every text illuminates another.',
    skills: ['lore', 'scholarship'],
    min_levels: [50, 50],
    bonus_type: 'discovery',
    value: 40,
    condition: { type: 'both_above', threshold: 50 },
    visual_effect: 'wisdom-aura',
  },
  {
    id: 'lore_sonar_tuning',
    name: 'Echoes of History',
    description: 'The sonar hears the past. Every ping a history lesson.',
    skills: ['lore', 'sonar_tuning'],
    min_levels: [40, 40],
    bonus_type: 'efficiency',
    value: 20,
    condition: { type: 'both_above', threshold: 40 },
    visual_effect: 'history-ping',
  },
  {
    id: 'scholarship_sonar_tuning',
    name: 'Calculated Echo',
    description: 'Mathematics perfects the ping. Precision absolute.',
    skills: ['scholarship', 'sonar_tuning'],
    min_levels: [50, 50],
    bonus_type: 'efficiency',
    value: 25,
    condition: { type: 'both_above', threshold: 50 },
    visual_effect: 'math-ping',
  },

  // KNOWLEDGE + CRAFTING
  {
    id: 'lore_haberdashery',
    name: 'Lore-Woven',
    description: 'Every stitch tells a story. The hat remembers.',
    skills: ['lore', 'haberdashery'],
    min_levels: [40, 40],
    bonus_type: 'quality',
    value: 15,
    condition: { type: 'both_above', threshold: 40 },
    visual_effect: 'lore-thread',
  },
  {
    id: 'lore_enchanting',
    name: 'Lore-Enchanted',
    description: 'Ancient words in modern weave. Power from the past.',
    skills: ['lore', 'enchanting'],
    min_levels: [50, 50],
    bonus_type: 'enchant_success',
    value: 20,
    condition: { type: 'both_above', threshold: 50 },
    visual_effect: 'ancient-rune',
  },
  {
    id: 'lore_alchemy',
    name: 'Ancient Formula',
    description: 'Lost recipes rediscovered. The old ways work best.',
    skills: ['lore', 'alchemy'],
    min_levels: [50, 50],
    bonus_type: 'discovery',
    value: 30,
    condition: { type: 'both_above', threshold: 50 },
    visual_effect: 'ancient-tome',
  },
  {
    id: 'lore_runecrafting',
    name: 'Ancient Runes',
    description: 'Runes from before the Loch. Power older than memory.',
    skills: ['lore', 'runecrafting'],
    min_levels: [60, 60],
    bonus_type: 'discovery',
    value: 40,
    condition: { type: 'both_above', threshold: 60 },
    visual_effect: 'ancient-rune-glow',
  },
  {
    id: 'scholarship_runecrafting',
    name: 'Wisdom Inscribed',
    description: 'Wisdom becomes rune. The brim thinks.',
    skills: ['scholarship', 'runecrafting'],
    min_levels: [70, 70],
    bonus_type: 'discovery',
    value: 50,
    condition: { type: 'both_above', threshold: 70 },
    visual_effect: 'wise-rune',
  },
  {
    id: 'scholarship_alchemy',
    name: 'Philosopher\'s Wisdom',
    description: 'Knowledge transmuted. The formula perfects itself.',
    skills: ['scholarship', 'alchemy'],
    min_levels: [70, 70],
    bonus_type: 'discovery',
    value: 40,
    condition: { type: 'both_above', threshold: 70 },
    visual_effect: 'wise-formula',
  },

  // COMBAT + GATHERING
  {
    id: 'hunting_dredging',
    name: 'Apex Dredger',
    description: 'Your dredge attracts the beasts. They come to you.',
    skills: ['hunting', 'dredging'],
    min_levels: [50, 50],
    bonus_type: 'rare_drop_chance',
    value: 40,
    condition: { type: 'both_above', threshold: 50 },
    visual_effect: 'blood-in-water',
  },
  {
    id: 'hunting_salvaging',
    name: 'Scavenger\'s Feast',
    description: 'The hunted leave more behind. Waste not.',
    skills: ['hunting', 'salvaging'],
    min_levels: [40, 40],
    bonus_type: 'resource_yield',
    value: 30,
    condition: { type: 'both_above', threshold: 40 },
    visual_effect: 'bone-glint',
  },
  {
    id: 'hunting_foraging',
    name: 'The Forest Hunter',
    description: 'You hunt where the kelp grows thick. The forest provides.',
    skills: ['hunting', 'foraging'],
    min_levels: [30, 30],
    bonus_type: 'rare_drop_chance',
    value: 25,
    condition: { type: 'both_above', threshold: 30 },
    visual_effect: 'kelp-camouflage',
  },
  {
    id: 'hunting_navigation',
    name: 'The Tracker\'s Chart',
    description: 'Your maps show every lair, every trail. Nothing hides.',
    skills: ['hunting', 'navigation'],
    min_levels: [40, 40],
    bonus_type: 'efficiency',
    value: 30,
    condition: { type: 'both_above', threshold: 40 },
    visual_effect: 'trail-map',
  },
  {
    id: 'evasion_hunting',
    name: 'Dance with Death',
    description: 'You dodge their strike, then take their head.',
    skills: ['evasion', 'hunting'],
    min_levels: [50, 50],
    bonus_type: 'crit_chance',
    value: 25,
    condition: { type: 'both_above', threshold: 50 },
    visual_effect: 'death-dance',
  },
  {
    id: 'harpooning_hunting',
    name: 'One Shot, One Kill',
    description: 'Your harpoon finds the heart. The beast falls.',
    skills: ['harpooning', 'hunting'],
    min_levels: [40, 40],
    bonus_type: 'damage',
    value: 30,
    condition: { type: 'both_above', threshold: 40 },
    visual_effect: 'perfect-throw',
  },
  {
    id: 'survival_hunting',
    name: 'Endurance Hunter',
    description: 'You outlast them. The deep doesn\'t claim you.',
    skills: ['survival', 'hunting'],
    min_levels: [40, 40],
    bonus_type: 'endurance',
    value: 25,
    condition: { type: 'both_above', threshold: 40 },
    visual_effect: 'endless-breath',
  },

  // COMBAT + PROCESSING
  {
    id: 'evasion_salvage_processing',
    name: 'Calm in Chaos',
    description: 'You process while the battle rages. Unshakeable.',
    skills: ['evasion', 'salvage_processing'],
    min_levels: [40, 40],
    bonus_type: 'speed',
    value: 20,
    condition: { type: 'both_above', threshold: 40 },
    visual_effect: 'calm-forge',
  },

  // COMBAT + CRAFTING
  {
    id: 'evasion_haberdashery',
    name: 'Battle Hatter',
    description: 'You stitch mid-combat. The hat is ready when the fight ends.',
    skills: ['evasion', 'haberdashery'],
    min_levels: [40, 40],
    bonus_type: 'craft_speed',
    value: 30,
    condition: { type: 'both_above', threshold: 40 },
    visual_effect: 'battle-stitch',
  },
  {
    id: 'harpooning_runecrafting',
    name: 'Runic Harpoon',
    description: 'Your harpoon carries the rune. The hit writes fate.',
    skills: ['harpooning', 'runecrafting'],
    min_levels: [60, 60],
    bonus_type: 'quality',
    value: 35,
    condition: { type: 'both_above', threshold: 60 },
    visual_effect: 'runic-harpoon',
  },
  {
    id: 'survival_haberdashery',
    name: 'Survival Stitch',
    description: 'The hat keeps you alive. Stitched with will.',
    skills: ['survival', 'haberdashery'],
    min_levels: [40, 40],
    bonus_type: 'sanity_shield',
    value: 25,
    condition: { type: 'both_above', threshold: 40 },
    visual_effect: 'survival-stitch',
  },
  {
    id: 'survival_enchanting',
    name: 'Will Enchanted',
    description: 'Your will powers the enchantment. Sanity is mana.',
    skills: ['survival', 'enchanting'],
    min_levels: [50, 50],
    bonus_type: 'enchant_success',
    value: 20,
    condition: { type: 'both_above', threshold: 50 },
    visual_effect: 'will-enchant',
  },

  // SOCIAL/ECONOMIC + CRAFTING
  {
    id: 'trading_haberdashery',
    name: 'Market Hatter',
    description: 'You know what sells. The market bends to your brim.',
    skills: ['trading', 'haberdashery'],
    min_levels: [40, 40],
    bonus_type: 'market_fee_reduction',
    value: 20,
    condition: { type: 'both_above', threshold: 40 },
    visual_effect: 'market-hat',
  },
  {
    id: 'trading_enchanting',
    name: 'Enchanted Commerce',
    description: 'Magic sells itself. You just set the price.',
    skills: ['trading', 'enchanting'],
    min_levels: [50, 50],
    bonus_type: 'market_fee_reduction',
    value: 15,
    condition: { type: 'both_above', threshold: 50 },
    visual_effect: 'magic-market',
  },
  {
    id: 'negotiation_haberdashery',
    name: 'Hatter\'s Tongue',
    description: 'Your hats speak for themselves. And so do you.',
    skills: ['negotiation', 'haberdashery'],
    min_levels: [40, 40],
    bonus_type: 'negotiation_bonus',
    value: 25,
    condition: { type: 'both_above', threshold: 40 },
    visual_effect: 'silver-tongue',
  },
  {
    id: 'guild_management_haberdashery',
    name: 'Crew Hatter',
    description: 'Every crew needs a hatter. You make the fleet famous.',
    skills: ['guild_management', 'haberdashery'],
    min_levels: [40, 40],
    bonus_type: 'party_xp_share',
    value: 20,
    condition: { type: 'both_above', threshold: 40 },
    visual_effect: 'crew-hat',
  },
  {
    id: 'guild_management_trading',
    name: 'Merchant Fleet',
    description: 'Your fleet moves markets. The Exchange remembers.',
    skills: ['guild_management', 'trading'],
    min_levels: [50, 50],
    bonus_type: 'shared_liquidity',
    value: 15,
    condition: { type: 'both_above', threshold: 50 },
    visual_effect: 'fleet-market',
  },

  // ULTIMATE SYNERGIES (High Level Only)
  {
    id: 'masterwork_lore',
    name: 'The Historian\'s Masterpiece',
    description: 'The hat writes its own history. Legend made manifest.',
    skills: ['masterwork', 'lore'],
    min_levels: [90, 90],
    bonus_type: 'rarity_preservation',
    value: 100,
    condition: { type: 'both_above', threshold: 90 },
    visual_effect: 'living-history',
  },
  {
    id: 'masterwork_scholarship',
    name: 'The Philosopher\'s Crown',
    description: 'Wisdom becomes crown. The wearer knows all.',
    skills: ['masterwork', 'scholarship'],
    min_levels: [90, 90],
    bonus_type: 'fate_weave',
    value: 50,
    condition: { type: 'both_above', threshold: 90 },
    visual_effect: 'philosopher-crown',
  },
  {
    id: 'masterwork_runecrafting',
    name: 'The World-Rune Crown',
    description: 'Reality inscribed. The crown rewrites the world.',
    skills: ['masterwork', 'runecrafting'],
    min_levels: [95, 95],
    bonus_type: 'rarity_preservation',
    value: 100,
    condition: { type: 'both_above', threshold: 95 },
    visual_effect: 'world-rune-crown',
  },
  {
    id: 'lore_scholarship_masterwork',
    name: 'The Trinity of Truth',
    description: 'Lore, Wisdom, Mastery. The hat that knows all.',
    skills: ['lore', 'scholarship', 'masterwork'],
    min_levels: { lore: 90, scholarship: 90, masterwork: 90 },
    bonus_type: 'fate_weave',
    value: 100,
    condition: { type: 'all_above', threshold: 90 },
    visual_effect: 'trinity-crown',
  },

  // SPECIAL: MASTERING SYNERGIES (Level 99 only)
  {
    id: 'mastering_all_crafting',
    name: 'The Universal Artificer',
    description: 'You craft anything. Any material. Any form. Perfection.',
    skills: ['mastering', 'haberdashery', 'enchanting', 'alchemy', 'runecrafting'],
    min_levels: { mastering: 99, haberdashery: 99, enchanting: 99, alchemy: 99, runecrafting: 99 },
    bonus_type: 'fate_weave',
    value: 100,
    condition: { type: 'all_above', threshold: 99 },
    visual_effect: 'universal-artificer',
  },
  {
    id: 'mastering_all_gathering',
    name: 'The Depth\'s Master',
    description: 'The Loch gives all. Nothing escapes your net.',
    skills: ['mastering', 'dredging', 'salvaging', 'foraging', 'hunting', 'navigation'],
    min_levels: { mastering: 99, dredging: 99, salvaging: 99, foraging: 99, hunting: 99, navigation: 99 },
    bonus_type: 'reality_anchor',
    value: 100,
    condition: { type: 'all_above', threshold: 99 },
    visual_effect: 'depths-master',
  },
  {
    id: 'mastering_all_knowledge',
    name: 'The Omniscient',
    description: 'You know all. The Loch has no secrets from you.',
    skills: ['mastering', 'lore', 'scholarship', 'sonar_tuning'],
    min_levels: { mastering: 99, lore: 99, scholarship: 99, sonar_tuning: 99 },
    bonus_type: 'fate_weave',
    value: 100,
    condition: { type: 'all_above', threshold: 99 },
    visual_effect: 'omniscient',
  },
  {
    id: 'mastering_all_combat',
    name: 'The Apex Predator',
    description: 'Nothing hunts you. You hunt everything.',
    skills: ['mastering', 'evasion', 'harpooning', 'survival'],
    min_levels: { mastering: 99, evasion: 99, harpooning: 99, survival: 99 },
    bonus_type: 'invincibility',
    value: 100,
    condition: { type: 'all_above', threshold: 99 },
    visual_effect: 'apex-predator',
  },
  {
    id: 'mastering_all_economic',
    name: 'The Market Maker',
    description: 'The Exchange is yours. Prices obey.',
    skills: ['mastering', 'trading', 'negotiation', 'guild_management'],
    min_levels: { mastering: 99, trading: 99, negotiation: 99, guild_management: 99 },
    bonus_type: 'market_control',
    value: 100,
    condition: { type: 'all_above', threshold: 99 },
    visual_effect: 'market-master',
  },

  // THE ULTIMATE SYNERGY
  {
    id: 'mastering_omega',
    name: 'Ω - THE FINAL SYNERGY',
    description: 'All skills at 99. The Ledger is complete. The Queen acknowledges you.',
    skills: ['mastering', 'dredging', 'salvaging', 'foraging', 'hunting', 'navigation', 'salvage_processing', 'fiber_working', 'bone_carving', 'metallurgy', 'haberdashery', 'enchanting', 'alchemy', 'runecrafting', 'masterwork', 'lore', 'sonar_tuning', 'scholarship', 'trading', 'negotiation', 'guild_management', 'evasion', 'harpooning', 'survival'],
    min_levels: { mastering: 99, dredging: 99, salvaging: 99, foraging: 99, hunting: 99, navigation: 99, salvage_processing: 99, fiber_working: 99, bone_carving: 99, metallurgy: 99, haberdashery: 99, enchanting: 99, alchemy: 99, runecrafting: 99, masterwork: 99, lore: 99, sonar_tuning: 99, scholarship: 99, trading: 99, negotiation: 99, guild_management: 99, evasion: 99, harpooning: 99, survival: 99 },
    bonus_type: 'omega_state',
    value: 100,
    condition: { type: 'all_above', threshold: 99 },
    visual_effect: 'omega-ascension',
  },
];

// ============================================================================
// 3-SKILL COMBOS (Advanced)
// ============================================================================

export const SKILL_COMBOS: SkillCombo[] = [
  {
    id: 'the_abyssal_artificer',
    name: 'The Abyssal Artificer',
    description: 'You craft from the deep. Every material, every technique, perfected.',
    skills: ['dredging', 'salvage_processing', 'haberdashery', 'enchanting', 'runecrafting'],
    min_levels: { dredging: 70, salvage_processing: 70, haberdashery: 70, enchanting: 70, runecrafting: 70 },
    active_effect: {
      type: 'unlock_ability',
      value: 1,
      targets: ['self'],
      cooldown: 3600,
    },
    passive_effects: [
      { type: 'craft_quality', value: 50, targets: ['self'] },
      { type: 'enchant_success', value: 50, targets: ['self'] },
      { type: 'rarity_preservation', value: 100, targets: ['self'] },
    ],
    visual: { particle_effect: 'artificer-aura', shader: 'artificer-shader', aura_color: '#4400ff', title_prefix: '[Artificer] ', title_color: '#4400ff' },
  },
  {
    id: 'the_depths_merchant',
    name: 'The Depths Merchant',
    description: 'You buy the deep. You sell the surface. The market obeys.',
    skills: ['dredging', 'salvaging', 'trading', 'negotiation', 'navigation'],
    min_levels: { dredging: 60, salvaging: 60, trading: 60, negotiation: 60, navigation: 60 },
    active_effect: { type: 'unlock_ability', value: 1, targets: ['self'], cooldown: 1800 },
    passive_effects: [
      { type: 'market_fee_reduction', value: 50, targets: ['self'] },
      { type: 'market_insight', value: 100, targets: ['self'] },
      { type: 'resource_yield', value: 50, targets: ['self'] },
    ],
    visual: { particle_effect: 'merchant-aura', shader: 'merchant-shader', aura_color: '#ffd700', title_prefix: '[Merchant] ', title_color: '#ffd700' },
  },
  {
    id: 'the_cryptid_scholar',
    name: 'The Cryptid Scholar',
    description: 'You know every beast. Every drop. Every secret. They fear your knowledge.',
    skills: ['hunting', 'lore', 'scholarship', 'bone_carving', 'alchemy'],
    min_levels: { hunting: 70, lore: 70, scholarship: 70, bone_carving: 70, alchemy: 70 },
    active_effect: { type: 'unlock_ability', value: 1, targets: ['self'], cooldown: 1800 },
    passive_effects: [
      { type: 'rare_drop_chance', value: 100, targets: ['self'] },
      { type: 'discovery', value: 100, targets: ['self'] },
      { type: 'quality', value: 50, targets: ['self'] },
    ],
    visual: { particle_effect: 'scholar-aura', shader: 'scholar-shader', aura_color: '#00ffff', title_prefix: '[Scholar] ', title_color: '#00ffff' },
  },
  {
    id: 'the_kelp_warden',
    name: 'The Kelp Warden',
    description: 'The forest is yours. Every frond, every creature, serves the Warden.',
    skills: ['foraging', 'fiber_working', 'haberdashery', 'alchemy', 'navigation'],
    min_levels: { foraging: 70, fiber_working: 70, haberdashery: 70, alchemy: 70, navigation: 70 },
    active_effect: { type: 'unlock_ability', value: 1, targets: ['self'], cooldown: 1800 },
    passive_effects: [
      { type: 'resource_yield', value: 100, targets: ['self'] },
      { type: 'craft_speed', value: 50, targets: ['self'] },
      { type: 'efficiency', value: 50, targets: ['party'] },
    ],
    visual: { particle_effect: 'kelp-aura', shader: 'kelp-shader', aura_color: '#00ff88', title_prefix: '[Warden] ', title_color: '#00ff88' },
  },
  {
    id: 'the_wreck_sovereign',
    name: 'The Wreck Sovereign',
    description: 'Every wreck is your domain. The dead serve. The metal obeys.',
    skills: ['salvaging', 'salvage_processing', 'metallurgy', 'bone_carving', 'negotiation'],
    min_levels: { salvaging: 70, salvage_processing: 70, metallurgy: 70, bone_carving: 70, negotiation: 70 },
    active_effect: { type: 'unlock_ability', value: 1, targets: ['self'], cooldown: 1800 },
    passive_effects: [
      { type: 'resource_yield', value: 100, targets: ['self'] },
      { type: 'quality', value: 50, targets: ['self'] },
      { type: 'efficiency', value: 50, targets: ['guild'] },
    ],
    visual: { particle_effect: 'wreck-aura', shader: 'wreck-shader', aura_color: '#8800ff', title_prefix: '[Sovereign] ', title_color: '#8800ff' },
  },
  {
    id: 'the_apex_predator',
    name: 'The Apex Predator',
    description: 'Nothing hunts you. You hunt everything. The deep fears your shadow.',
    skills: ['hunting', 'evasion', 'harpooning', 'survival', 'navigation'],
    min_levels: { hunting: 70, evasion: 70, harpooning: 70, survival: 70, navigation: 70 },
    active_effect: { type: 'unlock_ability', value: 1, targets: ['self'], cooldown: 1800 },
    passive_effects: [
      { type: 'damage', value: 50, targets: ['self'] },
      { type: 'evasion', value: 50, targets: ['self'] },
      { type: 'crit_chance', value: 100, targets: ['self'] },
    ],
    visual: { particle_effect: 'predator-aura', shader: 'predator-shader', aura_color: '#ff4444', title_prefix: '[Apex] ', title_color: '#ff4444' },
  },
  {
    id: 'the_sephirotic_adept',
    name: 'The Sephirotic Adept',
    description: 'The Tree of Life grows in your mind. The Sephiroth bow to your will.',
    skills: ['lore', 'scholarship', 'sonar_tuning', 'runecrafting', 'alchemy', 'enchanting'],
    min_levels: { lore: 80, scholarship: 80, sonar_tuning: 80, runecrafting: 80, alchemy: 80 },
    active_effect: { type: 'unlock_ability', value: 1, targets: ['self'], cooldown: 3600 },
    passive_effects: [
      { type: 'fate_weave', value: 100, targets: ['self'] },
      { type: 'reality_anchor', value: 100, targets: ['self'] },
    ],
    visual: { particle_effect: 'sephirotic-aura', shader: 'sephirotic-shader', aura_color: '#ff00ff', title_prefix: '[Adept] ', title_color: '#ff00ff' },
  },

  // SPECIAL: THE ULTIMATE COMBOS (Require Mastering)
  {
    id: 'the_ledger_keeper',
    name: 'The Ledger Keeper',
    description: 'You are the Ledger. Every hat, every trade, every soul recorded.',
    skills: ['mastering', 'lore', 'scholarship', 'trading', 'runecrafting'],
    min_levels: { mastering: 99, lore: 99, scholarship: 99, trading: 99, runecrafting: 99 },
    active_effect: { type: 'unlock_ability', value: 1, targets: ['self'], cooldown: 0 },
    passive_effects: [
      { type: 'fate_weave', value: 100, targets: ['self'] },
      { type: 'reality_anchor', value: 100, targets: ['global'] },
      { type: 'market_control', value: 100, targets: ['global'] },
    ],
    visual: { particle_effect: 'ledger-aura', shader: 'ledger-shader', aura_color: '#ffd700', title_prefix: '[Ledger] ', title_color: '#ffd700' },
  },
  {
    id: 'the_omega_ascendant',
    name: 'The Ω Ascendant',
    description: 'All skills at 99. The convergence complete. The Queen awaits.',
    skills: ['mastering', 'dredging', 'salvaging', 'foraging', 'hunting', 'navigation', 'salvage_processing', 'fiber_working', 'bone_carving', 'metallurgy', 'haberdashery', 'enchanting', 'alchemy', 'runecrafting', 'masterwork', 'lore', 'sonar_tuning', 'scholarship', 'trading', 'negotiation', 'guild_management', 'evasion', 'harpooning', 'survival'],
    min_levels: { mastering: 99, dredging: 99, salvaging: 99, foraging: 99, hunting: 99, navigation: 99, salvage_processing: 99, fiber_working: 99, bone_carving: 99, metallurgy: 99, haberdashery: 99, enchanting: 99, alchemy: 99, runecrafting: 99, masterwork: 99, lore: 99, sonar_tuning: 99, scholarship: 99, trading: 99, negotiation: 99, guild_management: 99, evasion: 99, harpooning: 99, survival: 99 },
    active_effect: { type: 'unlock_ability', value: 1, targets: ['self'], cooldown: 0 },
    passive_effects: [
      { type: 'omega_state', value: 100, targets: ['self'] },
      { type: 'divine_insight', value: 100, targets: ['global'] },
      { type: 'reality_author', value: 100, targets: ['global'] },
    ],
    visual: { particle_effect: 'omega-ascension', shader: 'omega-shader', aura_color: '#ffffff', title_prefix: '[Ω] ', title_color: '#ffffff', title_suffix: ' — THE CONVERGENCE' },
  },
];

// Helper functions
export function getSynergiesForSkill(skillId: SkillId): SkillSynergy[] {
  return PREDEFINED_SYNERGIES.filter(s => s.skills.includes(skillId));
}

export function getActiveSynergies(playerSkills: Record<string, { level: number; xp: number }>): SkillSynergy[] {
  return PREDEFINED_SYNERGIES.filter(synergy => {
    if (Array.isArray(synergy.min_levels)) {
      const [skillA, skillB] = synergy.skills;
      const [minA, minB] = synergy.min_levels;
      return (playerSkills[skillA]?.level ?? 0) >= minA && (playerSkills[skillB]?.level ?? 0) >= minB;
    } else {
      return Object.entries(synergy.min_levels).every(([skillId, minLevel]) => {
        return (playerSkills[skillId]?.level ?? 0) >= minLevel;
      });
    }
  });
}

export function getActiveCombos(playerSkills: Record<string, { level: number; xp: number }>): SkillCombo[] {
  return SKILL_COMBOS.filter(combo => {
    return Object.entries(combo.min_levels).every(([skillId, minLevel]) => {
      return playerSkills[skillId]?.level >= minLevel;
    });
  });
}

export function calculateSynergyBonus(synergy: SkillSynergy, levelA: number, levelB: number): number {
  const avgLevel = (levelA + levelB) / 2;
  const levelFactor = Math.min(avgLevel / 100, 1);
  return synergy.value * levelFactor;
}