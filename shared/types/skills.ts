// Shared types for Abyssal Assets - Skills System

export type SkillCategory = 
  | 'gathering'
  | 'processing'
  | 'crafting'
  | 'knowledge'
  | 'social_economic'
  | 'combat_survival';

export type SkillId = 
  // Gathering (5)
  | 'dredging'
  | 'salvaging'
  | 'foraging'
  | 'hunting'
  | 'navigation'
  // Processing (4)
  | 'salvage_processing'
  | 'fiber_working'
  | 'bone_carving'
  | 'metallurgy'
  // Crafting (5)
  | 'haberdashery'
  | 'enchanting'
  | 'alchemy'
  | 'runecrafting'
  | 'masterwork'
  // Knowledge (4)
  | 'lore'
  | 'scholarship'
  | 'sonar_tuning'
  | 'mastering'
  // Social/Economic (3)
  | 'trading'
  | 'negotiation'
  | 'guild_management'
  // Combat/Survival (3)
  | 'evasion'
  | 'harpooning'
  | 'survival';

import { SynergyBonusType } from './synergies';

export interface Skill {
  id: SkillId;
  name: string;
  category: SkillCategory;
  description: string;
  icon: string;
  max_level: 99;
  virtual_max_level: 120;
  base_xp: number;
  xp_curve_factor: number; // 1.15 default
  unlocks: SkillUnlock[];
  synergies: SkillDefSynergy[];
  specialization_branches: SpecializationBranch[];
}

export interface SkillUnlock {
  level: number;
  type: 'recipe' | 'zone' | 'technique' | 'ability' | 'passive' | 'cosmetic';
  description: string;
  data: Record<string, any>;
}

export interface SkillDefSynergy {
  skill_id: SkillId;
  bonus_type: SynergyBonusType;
  value: number; // percentage
  condition?: string; // e.g., "both_above_50"
}

export interface SpecializationBranch {
  id: string;
  name: string;
  description: string;
  unlock_level: number;
  perks: SpecializationPerk[];
}

export interface SpecializationPerk {
  level: number;
  name: string;
  description: string;
  effect: PerkEffect;
}

export interface PerkEffect {
  type: 'stat_bonus' | 'unlock' | 'chance' | 'efficiency' | 'quality';
  target: string;
  value: number | boolean | string;
}

export interface SkillProgress {
  skill_id: SkillId;
  level: number;
  xp: number;
  virtual_level: number;
  virtual_xp: number;
  total_xp: number;
}

export interface PlayerSkills {
  skills: Record<SkillId, SkillProgress>;
  total_level: number;
  virtual_total_level: number;
  specialization_choices: Record<string, string>; // category -> branch_id
}

// XP Curve Calculation
// xp_for_level(n) = base_xp * (curve_factor ^ (n - 1))
export function xpForLevel(baseXp: number, curveFactor: number, level: number): number {
  return Math.floor(baseXp * Math.pow(curveFactor, level - 1));
}

export function totalXpForLevel(baseXp: number, curveFactor: number, level: number): number {
  let total = 0;
  for (let i = 1; i <= level; i++) {
    total += xpForLevel(baseXp, curveFactor, i);
  }
  return total;
}

export function levelFromXp(baseXp: number, curveFactor: number, xp: number): number {
  let level = 0;
  let remaining = xp;
  while (remaining >= xpForLevel(baseXp, curveFactor, level + 1)) {
    level++;
    remaining -= xpForLevel(baseXp, curveFactor, level);
  }
  return level;
}

// Default skill configurations
export const SKILL_DEFAULTS: Record<SkillId, Omit<Skill, 'id'>> = {
  // GATHERING
  dredging: {
    name: 'Dredging',
    category: 'gathering',
    description: 'Extract resources from the Loch depths using sonar-guided extraction.',
    icon: 'skill-dredging',
    max_level: 99,
    virtual_max_level: 120,
    base_xp: 100,
    xp_curve_factor: 1.15,
    unlocks: [
      { level: 1, type: 'ability', description: 'Basic Dredge', data: { action: 'dredge_basic' } },
      { level: 10, type: 'technique', description: 'Deep Dredge', data: { action: 'dredge_deep', depth_bonus: 50 } },
      { level: 20, type: 'recipe', description: 'Sonar Ping', data: { item: 'sonar_ping' } },
      { level: 30, type: 'zone', description: 'Standard Depths Access', data: { zone: 'standard' } },
      { level: 40, type: 'technique', description: 'Precision Dredge', data: { precision_bonus: 0.1 } },
      { level: 50, type: 'zone', description: 'Deep Zone Access', data: { zone: 'deep' } },
      { level: 60, type: 'ability', description: 'Party Dredge', data: { action: 'dredge_party', max_party: 3 } },
      { level: 70, type: 'zone', description: 'Abyssal Zone Access', data: { zone: 'abyssal' } },
      { level: 80, type: 'technique', description: 'Master Dredge', data: { precision_bonus: 0.25, rare_boost: 0.5 } },
      { level: 90, type: 'zone', description: 'VIP Trench Access', data: { zone: 'trench' } },
      { level: 99, type: 'cosmetic', description: 'Skillcape: Dredger', data: { cape: 'cape_dredging' } },
    ],
    synergies: [
      { skill_id: 'sonar_tuning', bonus_type: 'xp_boost', value: 15, condition: 'both_above_50' },
      { skill_id: 'navigation', bonus_type: 'efficiency', value: 10, condition: 'both_above_30' },
      { skill_id: 'hunting', bonus_type: 'drop_rate', value: 25, condition: 'both_above_70' },
    ],
    specialization_branches: [
      {
        id: 'deep_delver',
        name: 'Deep Delver',
        description: 'Master the abyssal depths. Deeper, darker, richer.',
        unlock_level: 10,
        perks: [
          { level: 10, name: 'Pressure Adaptation', description: 'No depth penalty', effect: { type: 'stat_bonus', target: 'depth_penalty', value: 100 } },
          { level: 30, name: 'Abyssal Sense', description: 'See rare nodes at 2x range', effect: { type: 'stat_bonus', target: 'node_range', value: 200 } },
          { level: 50, name: 'Abyssal Mastery', description: 'Double loot in Abyssal zone', effect: { type: 'chance', target: 'double_loot_abyssal', value: 10 } },
        ],
      },
      {
        id: 'sonar_savant',
        name: 'Sonar Savant',
        description: 'Master the frequencies. See what others cannot.',
        unlock_level: 10,
        perks: [
          { level: 10, name: 'Perfect Pitch', description: 'Sonar mini-game 50% slower', effect: { type: 'efficiency', target: 'sonar_speed', value: 50 } },
          { level: 30, name: 'Frequency Memory', description: 'Remember last 5 successful angles', effect: { type: 'unlock', target: 'angle_memory', value: 5 } },
          { level: 50, name: 'Resonant Frequency', description: 'Auto-hit target zone 10% of time', effect: { type: 'chance', target: 'auto_hit', value: 10 } },
        ],
      },
    ],
  },

  salvaging: {
    name: 'Salvaging',
    category: 'gathering',
    description: 'Recover artifacts, metals, and mysteries from sunken wrecks.',
    icon: 'skill-salvaging',
    max_level: 99,
    virtual_max_level: 120,
    base_xp: 120,
    xp_curve_factor: 1.14,
    unlocks: [],
    synergies: [
      { skill_id: 'salvage_processing', bonus_type: 'efficiency', value: 20, condition: 'both_above_30' },
      { skill_id: 'metallurgy', bonus_type: 'quality', value: 15, condition: 'both_above_50' },
    ],
    specialization_branches: [],
  },

  foraging: {
    name: 'Foraging',
    category: 'gathering',
    description: 'Harvest kelp, coral, bioluminescent flora, and abyssal fungi.',
    icon: 'skill-foraging',
    max_level: 99,
    virtual_max_level: 120,
    base_xp: 90,
    xp_curve_factor: 1.16,
    unlocks: [],
    synergies: [
      { skill_id: 'fiber_working', bonus_type: 'efficiency', value: 20, condition: 'both_above_30' },
      { skill_id: 'alchemy', bonus_type: 'quality', value: 15, condition: 'both_above_50' },
    ],
    specialization_branches: [],
  },

  hunting: {
    name: 'Hunting',
    category: 'gathering',
    description: 'Track, stalk, and harvest the Loch\'s cryptid inhabitants.',
    icon: 'skill-hunting',
    max_level: 99,
    virtual_max_level: 120,
    base_xp: 150,
    xp_curve_factor: 1.13,
    unlocks: [],
    synergies: [
      { skill_id: 'lore', bonus_type: 'drop_rate', value: 25, condition: 'both_above_50' },
      { skill_id: 'harpooning', bonus_type: 'damage', value: 20, condition: 'both_above_30' },
      { skill_id: 'survival', bonus_type: 'evasion', value: 15, condition: 'both_above_40' },
    ],
    specialization_branches: [
      {
        id: 'cryptid_tracker',
        name: 'Cryptid Tracker',
        description: 'Follow the faintest trail. Smell the blood in the water.',
        unlock_level: 10,
        perks: [
          { level: 10, name: 'Fresh Trail', description: 'See monster tracks for 5 min after passage', effect: { type: 'unlock', target: 'track_duration', value: 300 } },
          { level: 30, name: 'Weak Point Mastery', description: '+50% crit chance on studied monsters', effect: { type: 'stat_bonus', target: 'crit_chance_studied', value: 50 } },
          { level: 50, name: 'Apex Predator', description: 'Monsters flee or submit. No aggression below level gap', effect: { type: 'unlock', target: 'intimidation', value: 1 } },
        ],
      },
      {
        id: 'trophy_collector',
        name: 'Trophy Collector',
        description: 'Every kill a prize. Every part a purpose.',
        unlock_level: 10,
        perks: [
          { level: 10, name: 'Clean Kill', description: '+25% material yield', effect: { type: 'efficiency', target: 'material_yield', value: 25 } },
          { level: 30, name: 'Rare Part Sense', description: 'See rare drop indicators on monsters', effect: { type: 'unlock', target: 'rare_drop_indicator', value: true } },
          { level: 50, name: 'Master Skinner', description: 'Guaranteed rare drop on crit kill', effect: { type: 'chance', target: 'guaranteed_rare_crit', value: 100 } },
        ],
      },
    ],
  },

  navigation: {
    name: 'Navigation',
    category: 'gathering',
    description: 'Chart the uncharted. Find the unfindable. Never lost.',
    icon: 'skill-navigation',
    max_level: 99,
    virtual_max_level: 120,
    base_xp: 80,
    xp_curve_factor: 1.17,
    unlocks: [],
    synergies: [
      { skill_id: 'dredging', bonus_type: 'efficiency', value: 10, condition: 'both_above_30' },
      { skill_id: 'trading', bonus_type: 'speed', value: 15, condition: 'both_above_50' },
    ],
    specialization_branches: [],
  },

  // PROCESSING
  salvage_processing: {
    name: 'Salvage Processing',
    category: 'processing',
    description: 'Break down recovered wreckage into pure materials.',
    icon: 'skill-salvage-processing',
    max_level: 99,
    virtual_max_level: 120,
    base_xp: 110,
    xp_curve_factor: 1.15,
    unlocks: [],
    synergies: [
      { skill_id: 'salvaging', bonus_type: 'efficiency', value: 20, condition: 'both_above_30' },
      { skill_id: 'metallurgy', bonus_type: 'quality', value: 15, condition: 'both_above_50' },
    ],
    specialization_branches: [],
  },

  fiber_working: {
    name: 'Fiber Working',
    category: 'processing',
    description: 'Spin kelp, abyssal silk, and cryptid silk into threads of power.',
    icon: 'skill-fiber-working',
    max_level: 99,
    virtual_max_level: 120,
    base_xp: 100,
    xp_curve_factor: 1.15,
    unlocks: [],
    synergies: [
      { skill_id: 'foraging', bonus_type: 'efficiency', value: 20, condition: 'both_above_30' },
      { skill_id: 'haberdashery', bonus_type: 'quality', value: 20, condition: 'both_above_50' },
    ],
    specialization_branches: [],
  },

  bone_carving: {
    name: 'Bone Carving',
    category: 'processing',
    description: 'Shape cryptid bone, ivory, and chitin into tools and art.',
    icon: 'skill-bone-carving',
    max_level: 99,
    virtual_max_level: 120,
    base_xp: 130,
    xp_curve_factor: 1.14,
    unlocks: [],
    synergies: [
      { skill_id: 'hunting', bonus_type: 'efficiency', value: 20, condition: 'both_above_30' },
      { skill_id: 'runecrafting', bonus_type: 'quality', value: 20, condition: 'both_above_50' },
    ],
    specialization_branches: [],
  },

  metallurgy: {
    name: 'Metallurgy',
    category: 'processing',
    description: 'Smelt sunken alloys, abyssal ores, and meteoritic iron.',
    icon: 'skill-metallurgy',
    max_level: 99,
    virtual_max_level: 120,
    base_xp: 140,
    xp_curve_factor: 1.13,
    unlocks: [],
    synergies: [
      { skill_id: 'salvaging', bonus_type: 'quality', value: 15, condition: 'both_above_50' },
      { skill_id: 'salvage_processing', bonus_type: 'efficiency', value: 15, condition: 'both_above_50' },
      { skill_id: 'haberdashery', bonus_type: 'quality', value: 10, condition: 'both_above_50' },
    ],
    specialization_branches: [],
  },

  // CRAFTING
  haberdashery: {
    name: 'Haberdashery',
    category: 'crafting',
    description: 'Stitch, shape, and crown. The art of the perfect fit.',
    icon: 'skill-haberdashery',
    max_level: 99,
    virtual_max_level: 120,
    base_xp: 100,
    xp_curve_factor: 1.15,
    unlocks: [],
    synergies: [
      { skill_id: 'fiber_working', bonus_type: 'quality', value: 20, condition: 'both_above_50' },
      { skill_id: 'enchanting', bonus_type: 'success_rate', value: 20, condition: 'both_above_50' },
      { skill_id: 'alchemy', bonus_type: 'quality', value: 15, condition: 'both_above_50' },
      { skill_id: 'metallurgy', bonus_type: 'quality', value: 10, condition: 'both_above_50' },
    ],
    specialization_branches: [
      {
        id: 'master_hatter',
        name: 'Master Hatter',
        description: 'The perfect hat for every head. The perfect fit for every soul.',
        unlock_level: 10,
        perks: [
          { level: 10, name: 'Perfect Fit', description: '+10% stat bonuses on crafted hats', effect: { type: 'stat_bonus', target: 'crafted_stats', value: 10 } },
          { level: 30, name: 'Signature Style', description: 'Crafter\'s mark gives +5% value', effect: { type: 'stat_bonus', target: 'value_bonus', value: 5 } },
          { level: 50, name: 'Living Stitch', description: 'Hats gain 1 essence charge per day', effect: { type: 'unlock', target: 'essence_regen', value: 1 } },
        ],
      },
    ],
  },

  enchanting: {
    name: 'Enchanting',
    category: 'crafting',
    description: 'Weave magic into the weave. Fate into felt. Destiny into brim.',
    icon: 'skill-enchanting',
    max_level: 99,
    virtual_max_level: 120,
    base_xp: 120,
    xp_curve_factor: 1.14,
    unlocks: [],
    synergies: [
      { skill_id: 'haberdashery', bonus_type: 'success_rate', value: 20, condition: 'both_above_50' },
      { skill_id: 'alchemy', bonus_type: 'quality', value: 15, condition: 'both_above_50' },
      { skill_id: 'runecrafting', bonus_type: 'quality', value: 20, condition: 'both_above_50' },
    ],
    specialization_branches: [],
  },

  alchemy: {
    name: 'Alchemy',
    category: 'crafting',
    description: 'Transmute lead to gold. Hat to legend. Essence into essence.',
    icon: 'skill-alchemy',
    max_level: 99,
    virtual_max_level: 120,
    base_xp: 130,
    xp_curve_factor: 1.13,
    unlocks: [],
    synergies: [
      { skill_id: 'foraging', bonus_type: 'quality', value: 15, condition: 'both_above_50' },
      { skill_id: 'enchanting', bonus_type: 'quality', value: 15, condition: 'both_above_50' },
      { skill_id: 'runecrafting', bonus_type: 'quality', value: 15, condition: 'both_above_50' },
      { skill_id: 'lore', bonus_type: 'discovery', value: 20, condition: 'both_above_50' },
    ],
    specialization_branches: [],
  },

  runecrafting: {
    name: 'Runecrafting',
    category: 'crafting',
    description: 'Inscribe reality into the brim. Rewrite the Loch\'s laws.',
    icon: 'skill-runecrafting',
    max_level: 99,
    virtual_max_level: 120,
    base_xp: 150,
    xp_curve_factor: 1.12,
    unlocks: [],
    synergies: [
      { skill_id: 'bone_carving', bonus_type: 'quality', value: 20, condition: 'both_above_50' },
      { skill_id: 'enchanting', bonus_type: 'quality', value: 20, condition: 'both_above_50' },
      { skill_id: 'alchemy', bonus_type: 'quality', value: 15, condition: 'both_above_50' },
      { skill_id: 'scholarship', bonus_type: 'discovery', value: 25, condition: 'both_above_70' },
    ],
    specialization_branches: [],
  },

  masterwork: {
    name: 'Masterwork',
    category: 'crafting',
    description: 'The pinnacle. Mythic-tier construction. Hats that make history.',
    icon: 'skill-masterwork',
    max_level: 99,
    virtual_max_level: 120,
    base_xp: 200,
    xp_curve_factor: 1.1,
    unlocks: [],
    synergies: [
      { skill_id: 'haberdashery', bonus_type: 'quality', value: 25, condition: 'both_above_90' },
      { skill_id: 'enchanting', bonus_type: 'success_rate', value: 25, condition: 'both_above_90' },
      { skill_id: 'runecrafting', bonus_type: 'quality', value: 25, condition: 'both_above_90' },
      { skill_id: 'alchemy', bonus_type: 'success_rate', value: 25, condition: 'both_above_90' },
    ],
    specialization_branches: [],
  },

  // KNOWLEDGE
  lore: {
    name: 'Lore',
    category: 'knowledge',
    description: 'The Loch remembers. So do you. Every cryptid, every current, every secret.',
    icon: 'skill-lore',
    max_level: 99,
    virtual_max_level: 120,
    base_xp: 80,
    xp_curve_factor: 1.18,
    unlocks: [],
    synergies: [
      { skill_id: 'hunting', bonus_type: 'drop_rate', value: 25, condition: 'both_above_50' },
      { skill_id: 'scholarship', bonus_type: 'discovery', value: 25, condition: 'both_above_70' },
      { skill_id: 'alchemy', bonus_type: 'discovery', value: 20, condition: 'both_above_50' },
    ],
    specialization_branches: [],
  },

  sonar_tuning: {
    name: 'Sonar Tuning',
    category: 'knowledge',
    description: 'Master the frequencies. See what others cannot. Hear the deep.',
    icon: 'skill-sonar-tuning',
    max_level: 99,
    virtual_max_level: 120,
    base_xp: 90,
    xp_curve_factor: 1.16,
    unlocks: [],
    synergies: [
      { skill_id: 'dredging', bonus_type: 'xp_boost', value: 15, condition: 'both_above_50' },
      { skill_id: 'navigation', bonus_type: 'efficiency', value: 15, condition: 'both_above_30' },
    ],
    specialization_branches: [],
  },

  scholarship: {
    name: 'Scholarship',
    category: 'knowledge',
    description: 'Ancient texts. Fate weaving. The math behind the magic.',
    icon: 'skill-scholarship',
    max_level: 99,
    virtual_max_level: 120,
    base_xp: 120,
    xp_curve_factor: 1.13,
    unlocks: [],
    synergies: [
      { skill_id: 'lore', bonus_type: 'discovery', value: 25, condition: 'both_above_70' },
      { skill_id: 'runecrafting', bonus_type: 'discovery', value: 25, condition: 'both_above_70' },
      { skill_id: 'alchemy', bonus_type: 'discovery', value: 20, condition: 'both_above_50' },
    ],
    specialization_branches: [],
  },

  mastering: {
    name: 'Mastering',
    category: 'knowledge',
    description: 'Mastery of all arts. The culmination of your journey.',
    icon: 'skill-mastering',
    max_level: 99,
    virtual_max_level: 120,
    base_xp: 250,
    xp_curve_factor: 1.1,
    unlocks: [],
    synergies: [],
    specialization_branches: [],
  },

  // SOCIAL/ECONOMIC
  trading: {
    name: 'Trading',
    category: 'social_economic',
    description: 'Buy low. Sell high. Move markets. The Exchange is your canvas.',
    icon: 'skill-trading',
    max_level: 99,
    virtual_max_level: 120,
    base_xp: 70,
    xp_curve_factor: 1.20,
    unlocks: [],
    synergies: [
      { skill_id: 'negotiation', bonus_type: 'fee_reduction', value: 15, condition: 'both_above_50' },
      { skill_id: 'navigation', bonus_type: 'speed', value: 15, condition: 'both_above_50' },
      { skill_id: 'lore', bonus_type: 'market_insight', value: 15, condition: 'both_above_50' },
    ],
    specialization_branches: [],
  },

  negotiation: {
    name: 'Negotiation',
    category: 'social_economic',
    description: 'Words are weapons. Prices are suggestions. Everything is negotiable.',
    icon: 'skill-negotiation',
    max_level: 99,
    virtual_max_level: 120,
    base_xp: 80,
    xp_curve_factor: 1.18,
    unlocks: [],
    synergies: [
      { skill_id: 'trading', bonus_type: 'fee_reduction', value: 15, condition: 'both_above_50' },
      { skill_id: 'hunting', bonus_type: 'pacify', value: 20, condition: 'both_above_50' },
    ],
    specialization_branches: [],
  },

  guild_management: {
    name: 'Guild Management',
    category: 'social_economic',
    description: 'Lead the Crew. Build the Fortress. The Exchange remembers loyalty.',
    icon: 'skill-guild-management',
    max_level: 99,
    virtual_max_level: 120,
    base_xp: 100,
    xp_curve_factor: 1.15,
    unlocks: [],
    synergies: [
      { skill_id: 'navigation', bonus_type: 'party_efficiency', value: 20, condition: 'both_above_50' },
      { skill_id: 'trading', bonus_type: 'shared_liquidity', value: 10, condition: 'both_above_50' },
    ],
    specialization_branches: [],
  },

  // COMBAT/SURVIVAL
  evasion: {
    name: 'Evasion',
    category: 'combat_survival',
    description: 'Don\'t get hit. The best defense is not being there.',
    icon: 'skill-evasion',
    max_level: 99,
    virtual_max_level: 120,
    base_xp: 120,
    xp_curve_factor: 1.14,
    unlocks: [],
    synergies: [
      { skill_id: 'hunting', bonus_type: 'crit_chance', value: 15, condition: 'both_above_50' },
      { skill_id: 'survival', bonus_type: 'stamina', value: 20, condition: 'both_above_50' },
    ],
    specialization_branches: [],
  },

  harpooning: {
    name: 'Harpooning',
    category: 'combat_survival',
    description: 'One shot. One kill. Part targeting. The perfect throw.',
    icon: 'skill-harpooning',
    max_level: 99,
    virtual_max_level: 120,
    base_xp: 130,
    xp_curve_factor: 1.13,
    unlocks: [],
    synergies: [
      { skill_id: 'hunting', bonus_type: 'damage', value: 20, condition: 'both_above_50' },
      { skill_id: 'evasion', bonus_type: 'reposition', value: 15, condition: 'both_above_30' },
    ],
    specialization_branches: [],
  },

  survival: {
    name: 'Survival',
    category: 'combat_survival',
    description: 'Oxygen. Pressure. Sanity. The deep doesn\'t forgive. You endure.',
    icon: 'skill-survival',
    max_level: 99,
    virtual_max_level: 120,
    base_xp: 110,
    xp_curve_factor: 1.15,
    unlocks: [],
    synergies: [
      { skill_id: 'evasion', bonus_type: 'stamina', value: 20, condition: 'both_above_50' },
      { skill_id: 'hunting', bonus_type: 'endurance', value: 15, condition: 'both_above_50' },
    ],
    specialization_branches: [],
  },
};

// All skill IDs in order
export const ALL_SKILL_IDS: SkillId[] = [
  'dredging', 'salvaging', 'foraging', 'hunting', 'navigation',
  'salvage_processing', 'fiber_working', 'bone_carving', 'metallurgy',
  'haberdashery', 'enchanting', 'alchemy', 'runecrafting', 'masterwork',
  'lore', 'sonar_tuning', 'scholarship', 'mastering',
  'trading', 'negotiation', 'guild_management',
  'evasion', 'harpooning', 'survival',
];

export const SKILLS_BY_CATEGORY: Record<SkillCategory, SkillId[]> = {
  gathering: ['dredging', 'salvaging', 'foraging', 'hunting', 'navigation'],
  processing: ['salvage_processing', 'fiber_working', 'bone_carving', 'metallurgy'],
  crafting: ['haberdashery', 'enchanting', 'alchemy', 'runecrafting', 'masterwork'],
  knowledge: ['lore', 'sonar_tuning', 'scholarship', 'mastering'],
  social_economic: ['trading', 'negotiation', 'guild_management'],
  combat_survival: ['evasion', 'harpooning', 'survival'],
};