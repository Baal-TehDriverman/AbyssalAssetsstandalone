// Shared types for Abyssal Assets - Quests System

export type QuestType = 
  | 'main_saga'
  | 'skill_saga'
  | 'guild_saga'
  | 'daily_whim'
  | 'world_event'
  | 'hidden'
  | 'player_created';

export type QuestStatus = 'available' | 'active' | 'completed' | 'failed' | 'hidden';

export type QuestPhase = 'nigredo' | 'albedo' | 'citrinitas' | 'rubedo' | 'projection';

export type QuestObjectiveType = 
  | 'kill'           // Kill X monsters
  | 'collect'        // Gather X items
  | 'craft'          // Craft X items
  | 'dredge'         // Dredge X times
  | 'trade'          // Buy/sell X value
  | 'explore'        // Visit location
  | 'dialogue'       // Talk to NPC
  | 'skill_level'    // Reach skill level
  | 'clout'          // Reach clout threshold
  | 'zone_unlock'    // Unlock zone
  | 'discover'       // Find hidden location/item
  | 'dialogue_choice' // Make story choice
  | 'craft_specific' // Craft specific item
  | 'deliver'        // Deliver item to NPC
  | 'party'          // Complete with party
  | 'pvp'            // Win PvP matches
  | 'custom';        // Custom scripted

export interface QuestObjective {
  id: string;
  type: QuestObjectiveType;
  description: string;
  target: string;           // monster_id, item_id, location_id, skill_id, etc.
  count: number;
  current_count: number;
  required: boolean;
  hidden: boolean;          // Hidden until previous objective complete
  rewards?: QuestReward[];
}

export interface QuestReward {
  type: 'item' | 'currency' | 'xp' | 'clout' | 'skill_xp' | 'unlock' | 'title' | 'cosmetic' | 'zone_access' | 'skill_unlock' | 'recipe';
  item_id?: string;
  quantity?: number;
  skill_id?: string;
  xp_amount?: number;
  clout_amount?: number;
  currency_type?: 'soul_coins' | 'abyssal_coins';
  currency_amount?: number;
  unlock_type?: 'zone' | 'skill' | 'recipe' | 'area' | 'vendor';
  unlock_id?: string;
  cosmetic_id?: string;
  title?: string;
}

export interface QuestPhaseData {
  phase: QuestPhase;
  title: string;
  description: string;
  objectives: QuestObjective[];
  required_completion: number; // How many objectives to advance
  rewards: QuestReward[];
  choices?: QuestChoice[];     // For Rubedo phase
}

export interface QuestChoice {
  id: string;
  text: string;
  description: string;
  consequences: QuestConsequence[];
  requirements?: QuestRequirement[];
}

export interface QuestConsequence {
  type: 'quest_state' | 'world_state' | 'faction_rep' | 'item_gain' | 'skill_xp' | 'permanent_unlock' | 'story_flag';
  target: string;
  value: any;
}

export interface QuestRequirement {
  type: 'skill_level' | 'item' | 'quest_completed' | 'clout' | 'zone' | 'choice_made';
  target: string;
  value: number | string | boolean;
}

export interface Quest {
  id: string;
  title: string;
  description: string;
  type: QuestType;
  saga_id?: string;           // For saga grouping
  act?: number;               // For main saga acts
  act_title?: string;
  level_requirement: number;
  skill_requirements: Record<string, number>; // skill_id -> level
  quest_requirements: string[]; // quest IDs that must be completed
  zone_requirement?: string;
  start_npc?: string;
  end_npc?: string;
  phases: QuestPhaseData[];
  repeatable: boolean;
  cooldown_hours?: number;
  time_limit_hours?: number;
  recommended_level: number;
  group_size: { min: number; max: number };
  rewards: QuestReward[];
  failure_consequences: QuestConsequence[];
  lore_entries: string[];     // Lore entry IDs unlocked
  hidden: boolean;
  world_event: boolean;
  daily_whim: boolean;
}

export interface QuestProgress {
  quest_id: string;
  status: QuestStatus;
  current_phase: number;
  objectives: Record<string, number>; // objective_id -> current_count
  started_at: string;
  updated_at: string;
  completed_at?: string;
  choices_made: Record<string, string>; // phase -> choice_id
  current_objectives: string[]; // IDs of active objectives
  failed: boolean;
  failure_reason?: string;
}

export interface Saga {
  id: string;
  name: string;
  description: string;
  type: 'main' | 'skill' | 'guild' | 'hidden';
  skill_id?: string;          // For skill sagas
  acts: SagaAct[];
  rewards: QuestReward[];
  completion_rewards: QuestReward[];
  hidden: boolean;
  prerequisites: string[];    // Other saga IDs
}

export interface SagaAct {
  act_number: number;
  title: string;
  description: string;
  quest_id: string;
  unlocks: string[];          // Quest IDs unlocked on completion
  rewards: QuestReward[];
  lore_entries: string[];
}

export interface PlayerQuestState {
  active_quests: Record<string, QuestProgress>;
  completed_quests: Record<string, QuestProgress>;
  failed_quests: Record<string, QuestProgress>;
  daily_whims_completed: string[];     // Quest IDs completed today
  daily_whim_reset: string;            // Last reset timestamp
  saga_progress: Record<string, { current_act: number; completed_acts: number[] }>;
  story_flags: Record<string, boolean>;
  world_state_changes: Record<string, any>;
  lores_discovered: string[];
  daily_whim_streak: number;
  weekly_grand_whim_progress: number;
}

// Daily Whims
export interface DailyWhim {
  id: string;
  title: string;
  description: string;
  objectives: QuestObjective[];
  difficulty: 'simple' | 'moderate' | 'challenging' | 'group';
  estimated_time_minutes: number;
  rewards: QuestReward[];
  expires_at: string;
}

export interface WeeklyGrandWhim {
  id: string;
  title: string;
  description: string;
  objectives: QuestObjective[];
  rewards: QuestReward[];
  vault_key_fragments: number;
  expires_at: string;
}

// World Events
export type WorldEventType = 
  | 'nessie_surfaces'
  | 'algae_bloom'
  | 'kraken_awakens'
  | 'great_dredge'
  | 'cryptid_conclave'
  | 'great_purge'
  | 'liliths_feast'
  | 'custom';

export interface WorldEvent {
  id: string;
  type: WorldEventType;
  title: string;
  description: string;
  start_time: string;
  end_time: string;
  active: boolean;
  global_buffs?: GlobalBuff[];
  special_spawns?: SpecialSpawn[];
  exclusive_rewards?: QuestReward[];
  participation_rewards?: QuestReward[];
  leaderboard_rewards?: LeaderboardReward[];
  min_level?: number;
  requires_party?: boolean;
}

export interface GlobalBuff {
  type: 'drop_rate' | 'xp_gain' | 'clout_gain' | 'rare_drop' | 'craft_speed' | 'market_fee';
  value: number; // percentage
  description: string;
}

export interface SpecialSpawn {
  monster_id: string;
  zone: string;
  count: number;
  respawn_minutes: number;
  guaranteed_drops?: string[];
}

export interface LeaderboardReward {
  rank_range: [number, number]; // [1, 1] = 1st place
  rewards: QuestReward[];
}

// Quest Givers / NPCs
export interface NPC {
  id: string;
  name: string;
  title: string;
  zone: string;
  position: { x: number; y: number };
  sprite: string;
  dialogue_tree: DialogueNode[];
  quests_given: string[];
  shop_inventory?: string[]; // Item IDs
  services?: ('identify' | 'repair' | 'enchant' | 'transmute' | 'augment')[];
  faction?: string;
  faction_rep_requirements?: Record<string, number>;
  schedule?: NPCSchedule[]; // Time-based availability
}

export interface NPCSchedule {
  start_hour: number; // 0-23
  end_hour: number;
  days: number[]; // 0-6, 0 = Sunday
}

export interface DialogueNode {
  id: string;
  text: string;
  speaker: 'npc' | 'player';
  portrait?: string;
  choices?: DialogueChoice[];
  conditions?: DialogueCondition[];
  effects?: DialogueEffect[];
  next_node?: string;
  ends_conversation?: boolean;
}

export interface DialogueChoice {
  id: string;
  text: string;
  next_node?: string;
  conditions?: DialogueCondition[];
  effects?: DialogueEffect[];
  skill_check?: { skill_id: string; level: number };
  ends_conversation?: boolean;
}

export interface DialogueCondition {
  type: 'quest_status' | 'skill_level' | 'item_owned' | 'clout' | 'faction_rep' | 'story_flag' | 'time_of_day' | 'weather';
  target: string;
  operator: 'eq' | 'neq' | 'gt' | 'gte' | 'lt' | 'lte' | 'contains';
  value: string | number | boolean;
}

export interface DialogueEffect {
  type: 'give_item' | 'take_item' | 'give_xp' | 'give_clout' | 'give_currency' | 'start_quest' | 'complete_quest' | 'set_story_flag' | 'change_faction_rep' | 'unlock_recipe' | 'give_title' | 'teleport' | 'unlock_zone';
  target: string;
  value: string | number | boolean;
}

// Quest Rewards (Extended)
export type QuestRewardType = 
  | 'item'
  | 'currency'
  | 'xp'
  | 'clout'
  | 'skill_xp'
  | 'unlock'
  | 'title'
  | 'cosmetic'
  | 'zone_access'
  | 'skill_unlock'
  | 'recipe'
  | 'faction_rep'
  | 'story_flag'
  | 'cosmetic_override';

export interface QuestRewardDetail {
  type: QuestRewardType;
  item_id?: string;
  quantity?: number;
  skill_id?: string;
  xp_amount?: number;
  clout_amount?: number;
  currency_type?: 'soul_coins' | 'abyssal_coins';
  currency_amount?: number;
  unlock_type?: 'zone' | 'skill' | 'recipe' | 'area' | 'vendor' | 'cosmetic' | 'title';
  unlock_id?: string;
  cosmetic_id?: string;
  title?: string;
  story_flag?: string;
  faction?: string;
  rep_amount?: number;
}