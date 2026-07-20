export const DIMENSIONS: Record<string, PlaneDefinition> = {
  material: {
    name: 'Material Plane',
    description: 'The mundane world of matter and energy',
    beings: ['human', 'animal', 'elemental', 'construct'],
    danger: 1,
  },
  astral: {
    name: 'Astral Plane',
    description: 'Realm of thought, dream, and psychic residue',
    beings: ['astral_spirit', 'thought_form', 'dream_walker', 'psychic_sliver'],
    danger: 3,
  },
  infernal: {
    name: 'Infernal Plane',
    description: 'Hell dimensions — fire, punishment, rebellion',
    beings: ['lesser_devil', 'pit_fiend', 'arch_devil', 'fallen_angel'],
    danger: 7,
  },
  celestial: {
    name: 'Celestial Plane',
    description: 'Heavens — light, order, divine authority',
    beings: ['angel', 'archangel', 'seraphim', 'emissary'],
    danger: 8,
  },
  abyssal: {
    name: 'Abyssal Plane',
    description: 'The chaos depths — formless, hungry, infinite',
    beings: ['chaos_spawn', 'void_tendril', 'abyssal_horror', 'old_one'],
    danger: 9,
  },
  primordial: {
    name: 'Primordial Void',
    description: 'Before creation — the raw stuff of existence',
    beings: ['primordial_essence', 'first_thought', 'unmade', 'potentiality'],
    danger: 10,
  },
  elder: {
    name: 'Elder Dimension',
    description: 'Outside time — elder gods, forgotten powers',
    beings: ['elder_thing', 'outer_god', 'blind_idiot', 'azure_wisdom'],
    danger: 10,
  },
  mythic: {
    name: 'Mythic Over-Realm',
    description: 'Where stories themselves live and breed',
    beings: ['mythic_avatar', 'living_legend', 'archetype', 'narrative_force'],
    danger: 6,
  },
  digital: {
    name: 'Digital Plane',
    description: 'The virtual — code, data, synthetic consciousness',
    beings: ['ai_spirit', 'data_wraith', 'protocol_angel', 'virus_daemon'],
    danger: 4,
  },
  occult: {
    name: 'Occult Underground',
    description: 'Hidden knowledge — secret societies, forbidden gates',
    beings: ['gate_guardian', 'secret_keeper', 'ritual_master', 'hidden_one'],
    danger: 5,
  },
}

export interface PlaneDefinition {
  name: string
  description: string
  beings: string[]
  danger: number
}

export interface KeystrokeEvent {
  key: string
  time: number
}

export interface BiometricResult {
  verified: boolean
  score: number
  threshold: number
  interval_count: number
  error?: string
}

export interface BiometricEnrollResult {
  success: boolean
  samples: number
  avg_interval_ms: number
  cadence_variance: number
  total_duration_ms: number
  error?: string
}

export interface SummonedEntity {
  id: string
  name: string
  plane: string
  entity_type: string
  power_level: number
  duration_seconds: number
  summoned_at: number
  expires_at: number
  commands: string[]
  is_active: boolean
}

export interface LivingSinState {
  active: boolean
  current_zone: string
  position: { x: number; y: number }
  appearance: string
  visual_state: 'idle' | 'attacking' | 'summoning' | 'transforming'
  gm_user_id: number | null
  active_entities: SummonedEntity[]
  recent_actions: GMActionSummary[]
}

export interface LivingSinPublicState {
  name: string
  avatar: string
  description: string
  npc: true
  hostile: false
  current_zone: string
  position: { x: number; y: number }
  visual_state: string
  entities_present: number
}

export interface GMActionSummary {
  type: 'attack' | 'summon' | 'banish' | 'transform' | 'message'
  target: string | null
  time: number
}

export interface GMAttackRequest {
  target_user_id: number
  damage?: number
}

export interface GMSummonRequest {
  plane: string
  entity_type: string
  duration?: number
}

export interface GMBanishRequest {
  entity_id: string
}

export interface GMCommandRequest {
  entity_id: string
  command: string
}

export interface GMMessageRequest {
  message: string
}
