export type Season = 'spring' | 'summer' | 'fall' | 'winter';
export type GameSpeed = 'fast' | 'normal' | 'slow';
export type VarroaLevel = 'safe' | 'caution' | 'danger' | 'critical' | 'collapse';
export type HoneyType = 'acacia' | 'chestnut' | 'wildflower' | 'mixed';
export type QueenStatus = 'healthy' | 'aging' | 'absent' | 'replacing' | 'laying_worker';
export type Region = 'default' | 'jeju' | 'gyeongnam' | 'gangwon';

export interface Hive {
  id: string;
  name: string;
  beeCount: number;
  frameCount: number;
  maxFrames: number;
  honeyStored: number;
  honeyCapacity: number;
  varroaLevel: number;
  queenHealth: number;
  queenAge: number;
  broodHealth: number;
  lastInspection: number;
  hasSuper: boolean;
  hasQueenExcluder: boolean;
  productionEfficiency: number;
  hasHornetTrap: boolean;
  hasHornetNet: boolean;
  swarmRisk: number;
  // Phase 3
  queenMarked: boolean;
  queenStatus: QueenStatus;
  layingWorkerDay: number; // 0 = no laying worker, >0 = day it started
  honeyByType: Record<HoneyType, number>;
}

// ─── Events ───
export type GameEventType = 'swarming' | 'hornet_scout' | 'hornet_attack' | 'inspection_ready' | 'laying_worker' | 'queen_aging';

export interface GameEvent {
  id: string;
  type: GameEventType;
  hiveId: string;
  hiveName: string;
  createdAt: number;
  expiresAt: number;
  resolved: boolean;
  data?: Record<string, unknown>;
}

// ─── Inspection Cards ───
export type InspectionCardType =
  | 'healthy_brood' | 'queen_found' | 'queen_cell' | 'varroa_detected'
  | 'honey_capped' | 'laying_worker' | 'wax_moth' | 'strong_colony' | 'low_stores'
  | 'drone_brood_excess' | 'queen_absent';

export interface InspectionCard {
  type: InspectionCardType;
  icon: string;
  title: string;
  description: string;
  effect: 'positive' | 'negative' | 'neutral' | 'choice';
  actions?: { label: string; actionId: string }[];
}

// ─── Research ───
export interface ResearchNode {
  id: string;
  name: string;
  icon: string;
  description: string;
  category: 'pest' | 'queen' | 'harvest' | 'management';
  cost: { gold: number; wax?: number; royalJelly?: number };
  prereqs: string[];
  effect: string;
  unlocked: boolean;
  researched: boolean;
}

// ─── Crafting ───
export interface CraftRecipe {
  id: string;
  name: string;
  icon: string;
  description: string;
  inputs: { wax?: number; honey?: number; gold?: number };
  output: { type: 'item' | 'gold' | 'equipment'; name: string; value: number };
  unlocked: boolean;
}

// ─── Region ───
export interface RegionInfo {
  id: Region;
  name: string;
  icon: string;
  description: string;
  specialHoney: HoneyType;
  seasonBonus: Partial<Record<Season, number>>;
  unlockFame: number;
}

export const REGIONS: RegionInfo[] = [
  { id: 'default', name: '중부 (기본)', icon: '🏡', description: '균형 잡힌 사계절 양봉', specialHoney: 'acacia', seasonBonus: {}, unlockFame: 0 },
  { id: 'jeju', name: '제주도', icon: '🏝️', description: '유채꿀 특산, 따뜻한 기후로 겨울 폐사율 감소', specialHoney: 'wildflower', seasonBonus: { spring: 0.3, winter: -0.3 }, unlockFame: 50 },
  { id: 'gyeongnam', name: '경남', icon: '🌿', description: '아카시아 최조기 개화, 봄 생산량 +40%', specialHoney: 'acacia', seasonBonus: { spring: 0.4 }, unlockFame: 100 },
  { id: 'gangwon', name: '강원도', icon: '🏔️', description: '피나무꿀 특산, 여름 생산 +30%, 겨울 혹독', specialHoney: 'mixed', seasonBonus: { summer: 0.3, winter: 0.5 }, unlockFame: 150 },
];

// ─── Prestige ───
export interface PrestigeData {
  totalPrestigeResets: number;
  lifetimeFame: number;
  permanentBonuses: {
    productionBoost: number; // % bonus
    startingGold: number;
    researchCarryover: string[]; // research IDs kept
  };
}

// ─── Game State ───
export interface GameState {
  gold: number;
  honey: number;
  wax: number;
  royalJelly: number;
  fame: number;

  // Honey by type
  honeyByType: Record<HoneyType, number>;

  hives: Hive[];
  maxHiveSlots: number;

  season: Season;
  dayInSeason: number;
  year: number;
  totalGameDays: number;
  gameSpeed: GameSpeed;

  extractorLevel: number;
  smokerLevel: number;
  suitLevel: number;

  level: number;
  experience: number;

  lastOnlineTime: number;
  totalHoneyHarvested: number;
  totalGoldEarned: number;
  hivesLost: number;
  yearsCompleted: number;

  tutorialStep: number;
  tutorialComplete: boolean;

  // Phase 2
  events: GameEvent[];
  research: Record<string, boolean>;
  craftedItems: Record<string, number>;
  notifications: string[];

  // Phase 3
  region: Region;
  prestige: PrestigeData;
}

export interface OfflineReport {
  duration: string;
  honeyProduced: number;
  varroaChanges: { hiveId: string; hiveName: string; oldLevel: number; newLevel: number }[];
  beeChanges: { hiveId: string; hiveName: string; change: number }[];
  seasonChanges: string[];
  alerts: string[];
}

// ─── Constants ───
export const SEASON_ORDER: Season[] = ['spring', 'summer', 'fall', 'winter'];

export const SEASON_NAMES: Record<Season, string> = {
  spring: '봄', summer: '여름', fall: '가을', winter: '겨울',
};

export const SEASON_EMOJIS: Record<Season, string> = {
  spring: '🌸', summer: '☀️', fall: '🍂', winter: '❄️',
};

export const SEASON_PRODUCTION_MULTIPLIER: Record<Season, number> = {
  spring: 3.0, summer: 1.2, fall: 0.8, winter: 0,
};

export const SEASON_VARROA_GROWTH: Record<Season, number> = {
  spring: 2, summer: 4, fall: 1, winter: 0.5,
};

export const DAYS_PER_SEASON: Record<GameSpeed, number> = {
  fast: 3, normal: 7, slow: 14,
};

export const VARROA_THRESHOLDS = { safe: 20, caution: 40, danger: 60, critical: 80 };

export function getVarroaStatus(level: number): VarroaLevel {
  if (level <= VARROA_THRESHOLDS.safe) return 'safe';
  if (level <= VARROA_THRESHOLDS.caution) return 'caution';
  if (level <= VARROA_THRESHOLDS.danger) return 'danger';
  if (level <= VARROA_THRESHOLDS.critical) return 'critical';
  return 'collapse';
}

export function getVarroaProductionPenalty(level: number): number {
  if (level <= 20) return 0;
  if (level <= 40) return 0.1;
  if (level <= 60) return 0.3;
  if (level <= 80) return 0.6;
  return 0.95;
}

// ─── Honey pricing ───
export const HONEY_PRICES: Record<HoneyType, number> = {
  acacia: 120,
  chestnut: 100,
  wildflower: 90,
  mixed: 70,
};

export const HONEY_NAMES: Record<HoneyType, string> = {
  acacia: '아카시아꿀',
  chestnut: '밤꿀',
  wildflower: '잡화꿀',
  mixed: '혼합꿀',
};

export const HONEY_ICONS: Record<HoneyType, string> = {
  acacia: '🍯',
  chestnut: '🌰',
  wildflower: '🌸',
  mixed: '🫙',
};

// Which honey type is produced in which season
export function getSeasonHoneyType(season: Season): HoneyType {
  switch (season) {
    case 'spring': return 'acacia';
    case 'summer': return 'chestnut';
    case 'fall': return 'wildflower';
    case 'winter': return 'mixed';
  }
}

// ─── Research Definitions ───
export const RESEARCH_TREE: ResearchNode[] = [
  // Pest management
  { id: 'organic_treatment', name: '유기 방제법', icon: '🌿', description: '옥살산 효과 +15', category: 'pest', cost: { gold: 300 }, prereqs: [], effect: 'oxalic_boost', unlocked: true, researched: false },
  { id: 'ipm_basics', name: 'IPM 기초', icon: '🔬', description: '바로아 성장 속도 -20%', category: 'pest', cost: { gold: 500, wax: 5 }, prereqs: ['organic_treatment'], effect: 'varroa_slow', unlocked: false, researched: false },
  { id: 'mesh_floor', name: '망사 밑판', icon: '🕸️', description: '바로아 자동 감소 -3/일', category: 'pest', cost: { gold: 400, wax: 3 }, prereqs: ['organic_treatment'], effect: 'mesh_floor', unlocked: false, researched: false },
  { id: 'hornet_defense', name: '말벌 방어 연구', icon: '🛡️', description: '말벌 트랩/그물 해금', category: 'pest', cost: { gold: 600 }, prereqs: ['ipm_basics'], effect: 'hornet_items', unlocked: false, researched: false },
  // Queen
  { id: 'queen_marking', name: '여왕 표시법', icon: '👑', description: '점검 시 여왕 발견 확률 +30%', category: 'queen', cost: { gold: 200 }, prereqs: [], effect: 'queen_marking', unlocked: true, researched: false },
  { id: 'queen_rearing', name: '여왕 육성', icon: '🥚', description: '인공왕대 기술 해금', category: 'queen', cost: { gold: 800, royalJelly: 2 }, prereqs: ['queen_marking'], effect: 'queen_rearing', unlocked: false, researched: false },
  { id: 'laying_worker_detection', name: '동봉산란 감지', icon: '🔍', description: '점검 시 동봉산란 조기 감지', category: 'queen', cost: { gold: 400 }, prereqs: ['queen_marking'], effect: 'laying_detect', unlocked: false, researched: false },
  // Harvest
  { id: 'advanced_uncapping', name: '고급 탈개도', icon: '🔪', description: '채밀 효율 +10%', category: 'harvest', cost: { gold: 400 }, prereqs: [], effect: 'harvest_boost', unlocked: true, researched: false },
  { id: 'wax_processing', name: '밀랍 가공', icon: '🕯️', description: '크래프팅 해금: 양초, 소초', category: 'harvest', cost: { gold: 350, wax: 5 }, prereqs: ['advanced_uncapping'], effect: 'crafting_wax', unlocked: false, researched: false },
  { id: 'honey_grading', name: '꿀 등급 분류', icon: '🏆', description: '고품질 꿀 판매가 +15%', category: 'harvest', cost: { gold: 600, wax: 3 }, prereqs: ['advanced_uncapping'], effect: 'honey_premium', unlocked: false, researched: false },
  // Management
  { id: 'auto_feeder', name: '자동 급이기', icon: '🤖', description: '급이 비용 -30%', category: 'management', cost: { gold: 500 }, prereqs: [], effect: 'feed_discount', unlocked: true, researched: false },
  { id: 'temp_sensor', name: '온도 센서', icon: '🌡️', description: '겨울 폐사율 -30%', category: 'management', cost: { gold: 700, wax: 3 }, prereqs: ['auto_feeder'], effect: 'winter_survival', unlocked: false, researched: false },
];

// ─── Craft Recipes ───
export const CRAFT_RECIPES: CraftRecipe[] = [
  { id: 'candle', name: '밀랍 양초', icon: '🕯️', description: '밀랍으로 양초를 만들어 판매', inputs: { wax: 3 }, output: { type: 'gold', name: '골드', value: 150 }, unlocked: false },
  { id: 'foundation', name: '소초 제작', icon: '📋', description: '밀랍으로 소초를 만들어 비용 절감', inputs: { wax: 2 }, output: { type: 'item', name: '소초', value: 1 }, unlocked: false },
  { id: 'propolis_tincture', name: '프로폴리스 팅크', icon: '💧', description: '꿀로 건강 제품 제작', inputs: { honey: 3, wax: 1 }, output: { type: 'gold', name: '골드', value: 200 }, unlocked: false },
  { id: 'hornet_trap', name: '말벌 트랩', icon: '🪤', description: '설탕물 트랩으로 말벌 포획', inputs: { gold: 80 }, output: { type: 'equipment', name: '말벌 트랩', value: 1 }, unlocked: false },
  { id: 'hornet_net', name: '말벌 그물', icon: '🥅', description: '벌통 입구 방어 그물', inputs: { gold: 200 }, output: { type: 'equipment', name: '말벌 그물', value: 1 }, unlocked: false },
  { id: 'queen_cage', name: '왕롱', icon: '🏰', description: '새 여왕 도입용 케이지', inputs: { gold: 150, wax: 1 }, output: { type: 'equipment', name: '왕롱', value: 1 }, unlocked: false },
];

// ─── Inspection Card Pool ───
export const INSPECTION_CARDS: Record<InspectionCardType, Omit<InspectionCard, 'type'>> = {
  healthy_brood: { icon: '🐝', title: '건강한 육아 패턴', description: '벌들이 건강하게 자라고 있습니다.', effect: 'positive' },
  queen_found: { icon: '👑', title: '여왕 발견!', description: '여왕벌이 건강하게 산란 중입니다.', effect: 'positive', actions: [{ label: '마킹하기', actionId: 'mark_queen' }, { label: '확인', actionId: 'ok' }] },
  queen_cell: { icon: '⚠️', title: '왕대 발견!', description: '분봉의 전조가 보입니다.', effect: 'choice', actions: [{ label: '제거 (분봉 억제)', actionId: 'remove_cell' }, { label: '방치 (분봉 허용)', actionId: 'allow_swarm' }] },
  varroa_detected: { icon: '🔴', title: '바로아 감지', description: '응애가 소비 위에 보입니다.', effect: 'negative' },
  honey_capped: { icon: '🍯', title: '밀개판 완성!', description: '채밀 가능 상태입니다!', effect: 'positive' },
  laying_worker: { icon: '🥚', title: '동봉산란 징후', description: '수벌 편중 산란이 관찰됩니다. 긴급 대응이 필요합니다!', effect: 'negative', actions: [{ label: '합봉', actionId: 'merge' }, { label: '유충 도입', actionId: 'introduce_larva' }, { label: '새 여왕 구입', actionId: 'buy_queen' }] },
  wax_moth: { icon: '🐛', title: '벌집 나방 발견', description: '약군에서 나방이 발견되었습니다.', effect: 'negative' },
  strong_colony: { icon: '💪', title: '강군 상태', description: '봉군이 매우 활발합니다!', effect: 'positive' },
  low_stores: { icon: '📉', title: '저밀 부족', description: '겨울 대비 꿀이 부족합니다.', effect: 'negative' },
  drone_brood_excess: { icon: '🔶', title: '수벌방 과다', description: '비정상적인 수벌방이 많습니다. 동봉산란 가능성!', effect: 'negative', actions: [{ label: '정밀 확인', actionId: 'check_laying' }] },
  queen_absent: { icon: '❓', title: '여왕 미발견', description: '여왕벌을 찾을 수 없습니다!', effect: 'negative', actions: [{ label: '새 여왕 구입', actionId: 'buy_queen' }, { label: '변성왕대 유도', actionId: 'emergency_cell' }] },
};

export interface ShopItem {
  id: string;
  name: string;
  description: string;
  cost: number;
  category: 'hive' | 'equipment' | 'treatment' | 'feed';
  icon: string;
  effect: (state: GameState) => GameState;
  canBuy: (state: GameState) => boolean;
}
