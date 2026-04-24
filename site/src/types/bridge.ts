export interface AuthUser {
  email: string;
  display_name: string;
}

export interface AuthSnapshot {
  configured: boolean;
  authenticated: boolean;
  pending_confirmation: boolean;
  message: string;
  user: AuthUser | null;
}

export interface CategoryFilters {
  draft: boolean;
  lane: boolean;
  macro: boolean;
  objective: boolean;
  economy: boolean;
  recovery: boolean;
}

export interface SettingsSnapshot {
  volume: number;
  voice_enabled: boolean;
  objectives_enabled: boolean;
  hardcore_enabled: boolean;
  voice_preset: string;
  voice_personality: string;
  category_filters: CategoryFilters;
  solo_focus: boolean;
  macro_interval: number;
  minimap_interval: number;
  economy_interval: number;
  item_check_interval: number;
  farm_threshold: number;
  vision_threshold: number;
  preferred_champion_pool: string[];
  prioritize_pool_picks: boolean;
  voice_catalog?: {
    personalities: Array<{
      id: string;
      label: string;
      engine: string;
      tier: string;
      description: string;
      provider: string;
    }>;
    presets: Array<{
      id: string;
      label: string;
      description: string;
    }>;
    tiers: Array<{
      id: string;
      label: string;
      monthly_price_brl: number;
      highlights: string[];
    }>;
  };
}

export interface MemoryEntry {
  title: string;
  note: string;
  tone: "success" | "urgent" | "warning" | "system" | "normal";
  meta?: string;
}

export interface TimelineEntry {
  clock: string;
  phase: string;
  category: string;
  severity: "success" | "urgent" | "warning" | "system" | "normal";
  kind: string;
  text: string;
  impact: string;
  priority: string;
  metadata: Record<string, unknown>;
}

export interface JungleNote {
  title: string;
  clock: string;
  detail: string;
}

export interface JungleIntel {
  enemy_jungler_name: string | null;
  enemy_jungler_champion: string | null;
  our_jungler_name: string | null;
  last_seen_clock: string;
  last_seen_source: string | null;
  probable_side: string;
  confidence: number;
  first_gank: Record<string, unknown> | null;
  objective_presence: {
    dragon: number;
    herald: number;
    baron: number;
    horde: number;
  };
  notes: JungleNote[];
  last_impacted_lane: string;
}

export interface DraftRecommendationsSnapshot {
  role: string;
  enemy_preview: string[];
  recommendations: Array<{
    champion: string;
    score: number;
    reasons: string[];
    comp_style: string;
    build_focus: string[];
    power_spikes: string[];
  }>;
}

export interface PostGameSummary {
  title: string;
  result: string;
  duration: string;
  scoreline: string;
  focus: string;
  confidence: string;
  reads: string[];
  memory: MemoryEntry[];
  timeline: TimelineEntry[];
  insights: {
    headline: string;
    opening: string;
    strengths: string[];
    improvements: string[];
    key_moments: string[];
    next_steps: string[];
    adaptive: {
      headline: string;
      repeated_patterns: string[];
      recovered_patterns: string[];
      phase_pressure: string[];
    };
  };
}

export interface PythonApi {
  register_user: (email: string, password: string, displayName: string) => Promise<AuthSnapshot>;
  login_user: (email: string, password: string) => Promise<AuthSnapshot>;
  logout_user: () => Promise<AuthSnapshot>;
  set_volume: (value: number) => void;
  toggle_voice: (state: boolean) => void;
  toggle_objectives: (state: boolean) => void;
  toggle_hardcore: (state: boolean) => void;
  set_voice_preset: (preset: string) => void;
  toggle_solo_focus: (state: boolean) => void;
  set_macro_interval: (value: number) => void;
  set_minimap_interval: (value: number) => void;
  set_economy_interval: (value: number) => void;
  set_item_check_interval: (value: number) => void;
  set_farm_threshold: (value: number) => void;
  set_vision_threshold: (value: number) => void;
  set_voice_personality: (personality: string) => void;
  set_preferred_champion_pool: (pool: string[]) => void;
  toggle_prioritize_pool_picks: (state: boolean) => void;
  set_category_enabled: (category: string, state: boolean) => void;
  set_category_preset: (preset: string) => void;
  get_auth_snapshot: () => Promise<AuthSnapshot>;
  get_settings_snapshot: () => Promise<SettingsSnapshot>;
  notify_ui_ready: () => void;
}

declare global {
  interface Window {
    pywebview?: {
      api: PythonApi;
    };
    hydrateAuthState: (snapshot: AuthSnapshot) => void;
    updateGameState: (phase: string, summonerName?: string | null, championName?: string | null) => void;
    hydrateSettings: (snapshot: SettingsSnapshot) => void;
    updateJungleIntel: (payload: JungleIntel) => void;
    updateDraftRecommendations: (payload: DraftRecommendationsSnapshot | null) => void;
    updatePostGameSummary: (summary: PostGameSummary) => void;
    appendPostGameMemory: (entry: MemoryEntry) => void;
    addAILog: (message: string, type?: string) => void;
    playTTSUpdate: (message: string, type?: string, category?: string | null) => void;
    addPreGameStat: (name: string, champion: string, rank: string, winrate: string) => void;
    setCoachTaxonomyFocus: (categoryId: string) => void;
  }
}
