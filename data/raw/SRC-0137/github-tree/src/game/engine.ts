import {
  GameState, Hive, Season, OfflineReport, GameEvent, InspectionCard, InspectionCardType,
  HoneyType, Region, PrestigeData,
  SEASON_ORDER, SEASON_PRODUCTION_MULTIPLIER,
  SEASON_VARROA_GROWTH, DAYS_PER_SEASON, INSPECTION_CARDS,
  getVarroaProductionPenalty, RESEARCH_TREE, CRAFT_RECIPES, REGIONS,
  getSeasonHoneyType, HONEY_PRICES,
} from './types';

const SAVE_KEY = 'beekeeping_sim_save';

const DEFAULT_HONEY_BY_TYPE = (): Record<HoneyType, number> => ({ acacia: 0, chestnut: 0, wildflower: 0, mixed: 0 });
const DEFAULT_PRESTIGE = (): PrestigeData => ({
  totalPrestigeResets: 0, lifetimeFame: 0,
  permanentBonuses: { productionBoost: 0, startingGold: 0, researchCarryover: [] },
});

export function createNewHive(id: string, name: string): Hive {
  return {
    id, name,
    beeCount: 10000, frameCount: 4, maxFrames: 10,
    honeyStored: 0, honeyCapacity: 20,
    varroaLevel: 5, queenHealth: 90, queenAge: 0, broodHealth: 85,
    lastInspection: 0, hasSuper: false, hasQueenExcluder: false,
    productionEfficiency: 1,
    hasHornetTrap: false, hasHornetNet: false, swarmRisk: 0,
    queenMarked: false, queenStatus: 'healthy', layingWorkerDay: 0,
    honeyByType: DEFAULT_HONEY_BY_TYPE(),
  };
}

export function createInitialState(prestige?: PrestigeData, region?: Region): GameState {
  const p = prestige || DEFAULT_PRESTIGE();
  return {
    gold: 500 + p.permanentBonuses.startingGold,
    honey: 0, wax: 0, royalJelly: 0, fame: 0,
    honeyByType: DEFAULT_HONEY_BY_TYPE(),
    hives: [createNewHive('hive-1', '첫 번째 벌통')],
    maxHiveSlots: 3,
    season: 'spring', dayInSeason: 1, year: 1, totalGameDays: 1,
    gameSpeed: 'normal',
    extractorLevel: 1, smokerLevel: 1, suitLevel: 1,
    level: 1, experience: 0,
    lastOnlineTime: Date.now(),
    totalHoneyHarvested: 0, totalGoldEarned: 0, hivesLost: 0, yearsCompleted: 0,
    tutorialStep: 0, tutorialComplete: false,
    events: [],
    research: Object.fromEntries(p.permanentBonuses.researchCarryover.map(r => [r, true])),
    craftedItems: {}, notifications: [],
    region: region || 'default',
    prestige: p,
  };
}

export function saveGame(state: GameState): void {
  try {
    localStorage.setItem(SAVE_KEY, JSON.stringify({ ...state, lastOnlineTime: Date.now() }));
  } catch (e) { console.error('Save failed', e); }
}

export function loadGame(): GameState | null {
  try {
    const raw = localStorage.getItem(SAVE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as GameState;
    // Migrate old saves
    if (!parsed.events) parsed.events = [];
    if (!parsed.research) parsed.research = {};
    if (!parsed.craftedItems) parsed.craftedItems = {};
    if (!parsed.notifications) parsed.notifications = [];
    if (!parsed.honeyByType) parsed.honeyByType = DEFAULT_HONEY_BY_TYPE();
    if (!parsed.region) parsed.region = 'default';
    if (!parsed.prestige) parsed.prestige = DEFAULT_PRESTIGE();
    for (const h of parsed.hives) {
      if (h.hasHornetTrap === undefined) h.hasHornetTrap = false;
      if (h.hasHornetNet === undefined) h.hasHornetNet = false;
      if (h.swarmRisk === undefined) h.swarmRisk = 0;
      if (h.queenMarked === undefined) h.queenMarked = false;
      if (h.queenStatus === undefined) h.queenStatus = h.queenHealth > 0 ? 'healthy' : 'absent';
      if (h.layingWorkerDay === undefined) h.layingWorkerDay = 0;
      if (!h.honeyByType) h.honeyByType = DEFAULT_HONEY_BY_TYPE();
    }
    return parsed;
  } catch (e) { console.error('Load failed', e); return null; }
}

export function deleteGame(): void { localStorage.removeItem(SAVE_KEY); }

// ─── Region bonus ───
function getRegionBonus(region: Region, season: Season): number {
  const r = REGIONS.find(rg => rg.id === region);
  return r?.seasonBonus[season] || 0;
}

// ─── Production ───
function hiveProductionPerTick(hive: Hive, season: Season, research: Record<string, boolean>, region: Region, prestige: PrestigeData): number {
  if (season === 'winter') return 0;
  const baseProd = 0.02;
  const beeFactor = hive.beeCount / 40000;
  const queenFactor = hive.queenStatus === 'laying_worker' ? 0.1 : hive.queenHealth / 100;
  const broodFactor = hive.broodHealth / 100;
  const seasonMult = SEASON_PRODUCTION_MULTIPLIER[season] * (1 + getRegionBonus(region, season));
  const varroaPenalty = 1 - getVarroaProductionPenalty(hive.varroaLevel);
  const superBonus = hive.hasSuper ? 1.3 : 1;
  const harvestBoost = research['advanced_uncapping'] ? 1.1 : 1;
  const prestigeBoost = 1 + prestige.permanentBonuses.productionBoost / 100;
  return baseProd * beeFactor * queenFactor * broodFactor * seasonMult * varroaPenalty * superBonus * harvestBoost * prestigeBoost;
}

function winterConsumptionPerTick(hive: Hive, research: Record<string, boolean>, region: Region): number {
  const base = 0.005 * (hive.beeCount / 40000);
  const regionMult = 1 + getRegionBonus(region, 'winter');
  const researchMult = research['temp_sensor'] ? 0.7 : 1;
  return base * regionMult * researchMult;
}

// ─── Tick ───
export function tickGame(state: GameState): GameState {
  let s = { ...state, hives: state.hives.map(h => ({ ...h, honeyByType: { ...h.honeyByType } })) };
  const daysPerSeason = DAYS_PER_SEASON[s.gameSpeed];
  const ticksPerDay = 60;
  const varroaSlow = s.research['ipm_basics'] ? 0.8 : 1;
  const meshReduction = s.research['mesh_floor'] ? 3 / ticksPerDay : 0;
  const honeyType = getSeasonHoneyType(s.season);

  for (const hive of s.hives) {
    if (hive.beeCount <= 0) continue;

    if (s.season === 'winter') {
      hive.honeyStored -= winterConsumptionPerTick(hive, s.research, s.region);
      if (hive.honeyStored < 0) {
        hive.honeyStored = 0;
        hive.beeCount = Math.max(0, hive.beeCount - 200);
      }
    } else {
      const produced = hiveProductionPerTick(hive, s.season, s.research, s.region, s.prestige);
      hive.honeyStored = Math.min(hive.honeyCapacity, hive.honeyStored + produced);
      hive.honeyByType[honeyType] = (hive.honeyByType[honeyType] || 0) + produced;
    }

    // Varroa
    const varroaGrowth = (SEASON_VARROA_GROWTH[s.season] * varroaSlow / ticksPerDay) - meshReduction;
    hive.varroaLevel = Math.max(0, Math.min(100, hive.varroaLevel + varroaGrowth));

    if (hive.varroaLevel > 60) {
      hive.beeCount = Math.max(0, hive.beeCount - Math.floor((hive.varroaLevel - 60) * 2));
      hive.broodHealth = Math.max(0, hive.broodHealth - 0.05);
    }
    if (hive.varroaLevel > 80) {
      hive.beeCount = Math.max(0, hive.beeCount - Math.floor((hive.varroaLevel - 80) * 10));
    }

    // Pop growth
    if (s.season !== 'winter' && hive.queenHealth > 0 && hive.queenStatus !== 'laying_worker') {
      const growthRate = (hive.queenHealth / 100) * (hive.broodHealth / 100) * 50;
      const maxBees = hive.frameCount * 8000;
      if (hive.beeCount < maxBees) hive.beeCount = Math.min(maxBees, hive.beeCount + growthRate);
    }

    // Laying worker progression
    if (hive.queenStatus === 'laying_worker') {
      hive.beeCount = Math.max(0, hive.beeCount - 30);
      hive.broodHealth = Math.max(0, hive.broodHealth - 0.1);
    }

    // Queen aging
    if (hive.queenStatus === 'healthy' && hive.queenAge > 2) {
      hive.queenStatus = 'aging';
      hive.queenHealth = Math.max(30, hive.queenHealth - 0.01);
    }

    // Queen absent → laying worker
    if (hive.queenStatus === 'absent' && hive.layingWorkerDay === 0) {
      // Start countdown - will become laying worker after ~3 game days
      hive.layingWorkerDay = s.totalGameDays;
    }
    if (hive.layingWorkerDay > 0 && hive.queenStatus === 'absent' && s.totalGameDays - hive.layingWorkerDay > 3) {
      hive.queenStatus = 'laying_worker';
    }

    // Swarm risk (spring)
    if (s.season === 'spring') {
      const density = hive.beeCount / (hive.frameCount * 8000);
      hive.swarmRisk = Math.min(100, Math.max(0,
        (density > 0.7 ? (density - 0.7) * 200 : 0)
        + (hive.queenAge > 2 ? 10 : 0)
        - (hive.hasSuper ? 15 : 0)
      ));
    } else {
      hive.swarmRisk = Math.max(0, hive.swarmRisk - 2);
    }

    hive.queenAge += 1 / (ticksPerDay * daysPerSeason * 4);
    hive.productionEfficiency = (hive.beeCount / 40000) * (hive.queenHealth / 100) * (1 - getVarroaProductionPenalty(hive.varroaLevel));

    if (hive.beeCount <= 0) { hive.beeCount = 0; hive.queenHealth = 0; hive.broodHealth = 0; hive.queenStatus = 'absent'; }
  }
  return s;
}

// ─── Day advance + events ───
export function advanceDay(state: GameState): { state: GameState; newSeason: boolean; newYear: boolean } {
  let s = { ...state, events: [...state.events], notifications: [...state.notifications] };
  const ticksPerDay = 60;
  for (let i = 0; i < ticksPerDay; i++) s = tickGame(s);

  s.totalGameDays += 1;
  s.dayInSeason += 1;

  s = generateEvents(s);
  s.events = s.events.filter(e => e.resolved || e.expiresAt > s.totalGameDays);

  const daysPerSeason = DAYS_PER_SEASON[s.gameSpeed];
  let newSeason = false, newYear = false;

  if (s.dayInSeason > daysPerSeason) {
    s.dayInSeason = 1;
    const idx = SEASON_ORDER.indexOf(s.season);
    if (idx === 3) { s.season = 'spring'; s.year += 1; s.yearsCompleted += 1; newYear = true; s.fame += 10; }
    else { s.season = SEASON_ORDER[idx + 1]; }
    newSeason = true;
  }

  return { state: s, newSeason, newYear };
}

function generateEvents(s: GameState): GameState {
  const newEvents: GameEvent[] = [];

  for (const hive of s.hives) {
    if (hive.beeCount <= 0) continue;

    // Swarming event (spring)
    if (s.season === 'spring' && hive.swarmRisk > 30) {
      const chance = hive.swarmRisk / 100 * 0.15;
      if (Math.random() < chance && !s.events.some(e => e.type === 'swarming' && e.hiveId === hive.id && !e.resolved)) {
        newEvents.push({
          id: `swarm-${hive.id}-${s.totalGameDays}`, type: 'swarming',
          hiveId: hive.id, hiveName: hive.name,
          createdAt: s.totalGameDays, expiresAt: s.totalGameDays + 3, resolved: false,
        });
        s.notifications.push(`🐝 ${hive.name}에서 분봉 징후가 감지되었습니다!`);
      }
    }

    // Hornet events (summer-fall)
    if ((s.season === 'summer' || s.season === 'fall') && !hive.hasHornetNet) {
      const hornetChance = s.season === 'fall' ? 0.12 : 0.06;
      if (Math.random() < hornetChance && !s.events.some(e => (e.type === 'hornet_scout' || e.type === 'hornet_attack') && e.hiveId === hive.id && !e.resolved)) {
        const isAttack = Math.random() < 0.3;
        newEvents.push({
          id: `hornet-${hive.id}-${s.totalGameDays}`, type: isAttack ? 'hornet_attack' : 'hornet_scout',
          hiveId: hive.id, hiveName: hive.name,
          createdAt: s.totalGameDays, expiresAt: s.totalGameDays + 2, resolved: false,
        });
        s.notifications.push(isAttack
          ? `🐝🔴 ${hive.name}에 장수말벌이 습격 중입니다!`
          : `⚠️ ${hive.name} 근처에서 정찰 말벌이 발견되었습니다!`);
      }
    }

    // Laying worker event
    if (hive.queenStatus === 'laying_worker' && !s.events.some(e => e.type === 'laying_worker' && e.hiveId === hive.id && !e.resolved)) {
      newEvents.push({
        id: `laying-${hive.id}-${s.totalGameDays}`, type: 'laying_worker',
        hiveId: hive.id, hiveName: hive.name,
        createdAt: s.totalGameDays, expiresAt: s.totalGameDays + 10, resolved: false,
      });
      s.notifications.push(`🥚 ${hive.name}에서 동봉산란이 시작되었습니다! 긴급 대응이 필요합니다.`);
    }

    // Queen aging warning
    if (hive.queenStatus === 'aging' && hive.queenAge > 2.5 && !s.events.some(e => e.type === 'queen_aging' && e.hiveId === hive.id && !e.resolved)) {
      newEvents.push({
        id: `queenage-${hive.id}-${s.totalGameDays}`, type: 'queen_aging',
        hiveId: hive.id, hiveName: hive.name,
        createdAt: s.totalGameDays, expiresAt: s.totalGameDays + 14, resolved: false,
      });
      s.notifications.push(`👑 ${hive.name}의 여왕이 노화되고 있습니다. 교체를 고려하세요.`);
    }
  }

  s.events = [...s.events, ...newEvents];
  return s;
}

// ─── Inspection ───
export function generateInspectionCards(hive: Hive, season: Season, research: Record<string, boolean>): InspectionCard[] {
  const cards: InspectionCard[] = [];
  const pool: { type: InspectionCardType; weight: number }[] = [];

  pool.push({ type: 'healthy_brood', weight: hive.broodHealth > 70 ? 30 : 10 });

  if (hive.queenStatus !== 'absent' && hive.queenStatus !== 'laying_worker') {
    pool.push({ type: 'queen_found', weight: (research['queen_marking'] || hive.queenMarked) ? 40 : 20 });
  } else {
    pool.push({ type: 'queen_absent', weight: 50 });
  }

  pool.push({ type: 'varroa_detected', weight: hive.varroaLevel > 20 ? hive.varroaLevel : 5 });
  pool.push({ type: 'honey_capped', weight: hive.honeyStored / hive.honeyCapacity > 0.7 ? 40 : 5 });
  if (season === 'spring' && hive.swarmRisk > 20) pool.push({ type: 'queen_cell', weight: hive.swarmRisk });

  // Laying worker detection
  if (hive.queenStatus === 'laying_worker') {
    pool.push({ type: 'laying_worker', weight: 60 });
  } else if (hive.queenStatus === 'absent' && research['laying_worker_detection']) {
    pool.push({ type: 'drone_brood_excess', weight: 40 });
  }

  if (hive.beeCount < 5000) pool.push({ type: 'wax_moth', weight: 30 });
  if (hive.beeCount > 30000) pool.push({ type: 'strong_colony', weight: 25 });
  if (hive.honeyStored < 3 && (season === 'fall' || season === 'winter')) pool.push({ type: 'low_stores', weight: 35 });

  const count = 3 + Math.floor(Math.random() * 3);
  const totalWeight = pool.reduce((s, p) => s + p.weight, 0);
  const picked = new Set<InspectionCardType>();

  for (let i = 0; i < count && picked.size < pool.length; i++) {
    let r = Math.random() * totalWeight;
    for (const p of pool) {
      if (picked.has(p.type)) continue;
      r -= p.weight;
      if (r <= 0) { picked.add(p.type); break; }
    }
  }

  for (const type of picked) {
    const def = INSPECTION_CARDS[type];
    cards.push({ type, ...def });
  }

  return cards;
}

// ─── Actions ───
export function harvestHoney(state: GameState, hiveId: string): GameState {
  const s = { ...state, hives: state.hives.map(h => ({ ...h, honeyByType: { ...h.honeyByType } })), honeyByType: { ...state.honeyByType } };
  const hive = s.hives.find(h => h.id === hiveId);
  if (!hive || hive.honeyStored < 1) return s;
  const extractionEff = 0.6 + s.extractorLevel * 0.08 + (s.research['advanced_uncapping'] ? 0.1 : 0);
  const harvested = hive.honeyStored * Math.min(1, extractionEff);
  const waxGained = Math.floor(harvested / 5);

  // Distribute harvested honey by type proportionally
  const totalInHive = Object.values(hive.honeyByType).reduce((a, b) => a + b, 0);
  if (totalInHive > 0) {
    for (const type of Object.keys(hive.honeyByType) as HoneyType[]) {
      const ratio = hive.honeyByType[type] / totalInHive;
      const amount = harvested * ratio;
      s.honeyByType[type] = (s.honeyByType[type] || 0) + amount;
      hive.honeyByType[type] *= (1 - Math.min(1, extractionEff));
    }
  } else {
    // Fallback: all goes to season type
    const ht = getSeasonHoneyType(s.season);
    s.honeyByType[ht] = (s.honeyByType[ht] || 0) + harvested;
  }

  hive.honeyStored *= (1 - Math.min(1, extractionEff));
  s.honey += harvested; s.wax += waxGained;
  s.totalHoneyHarvested += harvested; s.experience += Math.floor(harvested * 10);

  // Small chance of royal jelly
  if (Math.random() < 0.1) { s.royalJelly += 1; s.notifications = [...s.notifications, '✨ 로열젤리 1개를 획득했습니다!']; }

  return s;
}

export function sellHoneyByType(state: GameState, honeyType: HoneyType, amount: number): GameState {
  if ((state.honeyByType[honeyType] || 0) < amount) return state;
  const s = { ...state, honeyByType: { ...state.honeyByType } };
  const premium = s.research['honey_grading'] ? 1.15 : 1;
  const price = Math.floor(HONEY_PRICES[honeyType] * premium);
  const revenue = Math.floor(amount * price);
  s.honeyByType[honeyType] -= amount;
  s.honey -= amount;
  s.gold += revenue; s.totalGoldEarned += revenue; s.experience += Math.floor(revenue / 10);
  s.fame += Math.floor(revenue / 500);
  return s;
}

export function sellHoney(state: GameState, amount: number): GameState {
  if (state.honey < amount) return state;
  const s = { ...state, honeyByType: { ...state.honeyByType } };
  // Sell proportionally from all types
  const total = Object.values(s.honeyByType).reduce((a, b) => a + b, 0);
  let totalRevenue = 0;
  const premium = s.research['honey_grading'] ? 1.15 : 1;
  if (total > 0) {
    for (const type of Object.keys(s.honeyByType) as HoneyType[]) {
      const ratio = s.honeyByType[type] / total;
      const sold = amount * ratio;
      const price = Math.floor(HONEY_PRICES[type] * premium);
      totalRevenue += sold * price;
      s.honeyByType[type] -= sold;
    }
  } else {
    totalRevenue = amount * 70;
  }
  const revenue = Math.floor(totalRevenue);
  s.honey -= amount; s.gold += revenue; s.totalGoldEarned += revenue; s.experience += Math.floor(revenue / 10);
  s.fame += Math.floor(revenue / 500);
  return s;
}

export function treatVarroa(state: GameState, hiveId: string, method: 'amitraz' | 'oxalic' | 'drone_removal'): GameState {
  const s = { ...state, hives: state.hives.map(h => ({ ...h })) };
  const hive = s.hives.find(h => h.id === hiveId);
  if (!hive) return s;
  const oxalicBoost = s.research['organic_treatment'] ? 15 : 0;
  switch (method) {
    case 'amitraz': if (s.gold < 50) return state; s.gold -= 50; hive.varroaLevel = Math.max(0, hive.varroaLevel - 45); break;
    case 'oxalic': if (s.gold < 20) return state; s.gold -= 20; hive.varroaLevel = Math.max(0, hive.varroaLevel - 35 - oxalicBoost); break;
    case 'drone_removal': hive.varroaLevel = Math.max(0, hive.varroaLevel - 12); break;
  }
  s.experience += 20;
  return s;
}

export function feedBees(state: GameState, hiveId: string): GameState {
  const cost = state.research['auto_feeder'] ? 21 : 30;
  if (state.gold < cost) return state;
  const s = { ...state, hives: state.hives.map(h => ({ ...h })) };
  const hive = s.hives.find(h => h.id === hiveId);
  if (!hive) return s;
  s.gold -= cost;
  hive.honeyStored = Math.min(hive.honeyCapacity, hive.honeyStored + 3);
  s.experience += 5;
  return s;
}

export function addFrame(state: GameState, hiveId: string): GameState {
  if (state.gold < 40) return state;
  const s = { ...state, hives: state.hives.map(h => ({ ...h })) };
  const hive = s.hives.find(h => h.id === hiveId);
  if (!hive || hive.frameCount >= hive.maxFrames) return state;
  s.gold -= 40; hive.frameCount += 1; hive.honeyCapacity += 2;
  return s;
}

export function installSuper(state: GameState, hiveId: string): GameState {
  if (state.gold < 100) return state;
  const s = { ...state, hives: state.hives.map(h => ({ ...h })) };
  const hive = s.hives.find(h => h.id === hiveId);
  if (!hive || hive.hasSuper) return state;
  s.gold -= 100; hive.hasSuper = true; hive.honeyCapacity += 10;
  return s;
}

export function buyHive(state: GameState): GameState {
  if (state.gold < 300 || state.hives.length >= state.maxHiveSlots) return state;
  const s = { ...state };
  s.gold -= 300;
  s.hives = [...s.hives, createNewHive(`hive-${Date.now()}`, `${s.hives.length + 1}번 벌통`)];
  s.experience += 50;
  return s;
}

export function expandSlots(state: GameState): GameState {
  const cost = state.maxHiveSlots * 200;
  if (state.gold < cost) return state;
  return { ...state, gold: state.gold - cost, maxHiveSlots: state.maxHiveSlots + 1 };
}

export function upgradeExtractor(state: GameState): GameState {
  if (state.extractorLevel >= 5) return state;
  const cost = state.extractorLevel * 200;
  if (state.gold < cost) return state;
  return { ...state, gold: state.gold - cost, extractorLevel: state.extractorLevel + 1 };
}

export function checkLevelUp(state: GameState): GameState {
  const xpNeeded = state.level * 200;
  if (state.experience >= xpNeeded) return { ...state, level: state.level + 1, experience: state.experience - xpNeeded };
  return state;
}

export function getHiveStatus(hive: Hive): 'green' | 'yellow' | 'orange' | 'red' {
  if (hive.beeCount === 0) return 'red';
  if (hive.queenStatus === 'laying_worker') return 'red';
  if (hive.varroaLevel > 60 || hive.queenHealth < 30 || hive.queenStatus === 'absent') return 'red';
  if (hive.varroaLevel > 40 || hive.queenHealth < 60 || hive.honeyStored < 2) return 'orange';
  if (hive.varroaLevel > 20 || hive.queenHealth < 80) return 'yellow';
  return 'green';
}

// ─── Queen management ───
export function markQueen(state: GameState, hiveId: string): GameState {
  const s = { ...state, hives: state.hives.map(h => ({ ...h })) };
  const hive = s.hives.find(h => h.id === hiveId);
  if (!hive || hive.queenStatus === 'absent' || hive.queenStatus === 'laying_worker') return s;
  hive.queenMarked = true;
  s.experience += 10;
  return s;
}

export function replaceQueen(state: GameState, hiveId: string): GameState {
  if (state.gold < 200) return state;
  const s = { ...state, hives: state.hives.map(h => ({ ...h })), notifications: [...state.notifications] };
  const hive = s.hives.find(h => h.id === hiveId);
  if (!hive) return s;

  s.gold -= 200;
  // Success rate depends on current queen status
  const successRate = hive.queenStatus === 'laying_worker' ? 0.5 : 0.85;
  if (Math.random() < successRate) {
    hive.queenHealth = 95;
    hive.queenAge = 0;
    hive.queenMarked = false;
    hive.queenStatus = 'healthy';
    hive.layingWorkerDay = 0;
    hive.broodHealth = Math.min(100, hive.broodHealth + 20);
    s.notifications.push(`👑 ${hive.name}에 새 여왕이 성공적으로 도입되었습니다!`);
    s.experience += 50;
  } else {
    s.notifications.push(`❌ ${hive.name}의 새 여왕 도입이 실패했습니다. 벌들이 여왕을 거부했습니다.`);
  }
  return s;
}

export function rearQueen(state: GameState, hiveId: string, donorHiveId: string): GameState {
  if (!state.research['queen_rearing']) return state;
  const s = { ...state, hives: state.hives.map(h => ({ ...h })), notifications: [...state.notifications] };
  const hive = s.hives.find(h => h.id === hiveId);
  const donor = s.hives.find(h => h.id === donorHiveId);
  if (!hive || !donor || donor.beeCount < 5000) return s;

  // Takes time but is free - 60% success
  if (Math.random() < 0.6) {
    hive.queenHealth = 85;
    hive.queenAge = 0;
    hive.queenMarked = false;
    hive.queenStatus = 'replacing';
    hive.layingWorkerDay = 0;
    s.notifications.push(`🥚 ${hive.name}에서 변성왕대 육성이 시작되었습니다. (약 25일 후 완료)`);
  } else {
    s.notifications.push(`❌ ${hive.name}의 변성왕대 육성이 실패했습니다.`);
  }
  s.experience += 30;
  return s;
}

// ─── Laying worker resolution ───
export function resolveLayingWorker(state: GameState, hiveId: string, action: 'merge' | 'introduce_larva' | 'buy_queen' | 'abandon'): GameState {
  const s = { ...state, hives: state.hives.map(h => ({ ...h })), events: state.events.map(e => ({ ...e })), notifications: [...state.notifications] };
  const hive = s.hives.find(h => h.id === hiveId);
  if (!hive) return s;

  // Resolve related events
  s.events.filter(e => e.type === 'laying_worker' && e.hiveId === hiveId).forEach(e => e.resolved = true);

  switch (action) {
    case 'merge': {
      // Merge into strongest hive
      const target = s.hives.filter(h => h.id !== hiveId && h.beeCount > 0).sort((a, b) => b.beeCount - a.beeCount)[0];
      if (target) {
        target.beeCount += Math.floor(hive.beeCount * 0.7);
        hive.beeCount = 0; hive.queenHealth = 0; hive.queenStatus = 'absent'; hive.layingWorkerDay = 0;
        s.notifications.push(`🔄 ${hive.name}을 ${target.name}에 합봉했습니다. (성공률 90%)`);
      } else {
        s.notifications.push(`❌ 합봉할 벌통이 없습니다.`);
      }
      break;
    }
    case 'introduce_larva': {
      const donor = s.hives.filter(h => h.id !== hiveId && h.beeCount > 5000 && h.queenStatus === 'healthy').sort((a, b) => b.beeCount - a.beeCount)[0];
      if (donor && Math.random() < 0.6) {
        hive.queenStatus = 'replacing';
        hive.layingWorkerDay = 0;
        s.notifications.push(`🥚 ${donor.name}에서 유충을 도입하여 변성왕대를 유도합니다.`);
      } else if (!donor) {
        s.notifications.push(`❌ 유충을 제공할 건강한 벌통이 없습니다.`);
      } else {
        s.notifications.push(`❌ 변성왕대 유도가 실패했습니다.`);
      }
      break;
    }
    case 'buy_queen': {
      if (s.gold < 200) { s.notifications.push(`❌ 골드가 부족합니다. (200골드 필요)`); break; }
      s.gold -= 200;
      // 절식 후 도입 시 85%, 직접 투입 시 40%
      const hasCage = (s.craftedItems['queen_cage'] || 0) > 0;
      const success = hasCage ? 0.85 : 0.4;
      if (hasCage) s.craftedItems = { ...s.craftedItems, queen_cage: s.craftedItems['queen_cage'] - 1 };
      if (Math.random() < success) {
        hive.queenHealth = 95; hive.queenAge = 0; hive.queenMarked = false;
        hive.queenStatus = 'healthy'; hive.layingWorkerDay = 0;
        hive.broodHealth = Math.min(100, hive.broodHealth + 15);
        s.notifications.push(`👑 새 여왕 도입 성공! ${hasCage ? '(왕롱 사용)' : '(직접 투입 — 위험!)'}`);
      } else {
        s.notifications.push(`❌ 새 여왕이 살해되었습니다... ${hasCage ? '' : '왕롱을 사용하면 성공률이 높아집니다.'}`);
      }
      break;
    }
    case 'abandon':
      s.notifications.push(`💀 ${hive.name}을 방치합니다. 봉군이 서서히 소멸합니다.`);
      break;
  }
  s.experience += 20;
  return s;
}

// ─── Event resolution ───
export function resolveSwarmEvent(state: GameState, eventId: string, action: 'capture' | 'ignore'): GameState {
  const s = { ...state, hives: state.hives.map(h => ({ ...h })), events: state.events.map(e => ({ ...e })), notifications: [...state.notifications] };
  const event = s.events.find(e => e.id === eventId);
  if (!event) return s;
  event.resolved = true;
  const hive = s.hives.find(h => h.id === event.hiveId);
  if (!hive) return s;

  if (action === 'capture') {
    const successRate = Math.min(0.9, 0.4 + s.level * 0.05);
    if (Math.random() < successRate && s.hives.length < s.maxHiveSlots) {
      const newBees = Math.floor(hive.beeCount * 0.4);
      hive.beeCount -= newBees; hive.swarmRisk = 0;
      s.hives.push({ ...createNewHive(`hive-${Date.now()}`, `분봉군 ${s.hives.length + 1}`), beeCount: newBees });
      s.notifications.push(`✅ 분봉 포획 성공! 새 봉군을 얻었습니다.`);
      s.experience += 100; s.fame += 5;
    } else {
      hive.beeCount = Math.floor(hive.beeCount * 0.5); hive.swarmRisk = 0;
      s.notifications.push(`❌ 분봉 포획 실패... 벌의 50%를 잃었습니다.`);
    }
  } else {
    hive.beeCount = Math.floor(hive.beeCount * 0.5); hive.swarmRisk = 0;
    s.notifications.push(`🐝 ${hive.name}에서 분봉이 일어나 벌의 50%가 떠났습니다.`);
  }
  return s;
}

export function resolveHornetEvent(state: GameState, eventId: string, action: 'kill' | 'trap' | 'ignore'): GameState {
  const s = { ...state, hives: state.hives.map(h => ({ ...h })), events: state.events.map(e => ({ ...e })), notifications: [...state.notifications] };
  const event = s.events.find(e => e.id === eventId);
  if (!event) return s;
  event.resolved = true;
  const hive = s.hives.find(h => h.id === event.hiveId);
  if (!hive) return s;

  if (event.type === 'hornet_attack') {
    if (action === 'kill') {
      // Mini-game success — always succeed
      s.notifications.push(`✅ 장수말벌을 격퇴했습니다! 🎮`);
      s.experience += 100; s.fame += 5;
    } else if (action === 'trap' && hive.hasHornetTrap) {
      hive.beeCount = Math.floor(hive.beeCount * 0.85);
      s.notifications.push(`🪤 트랩이 일부를 포획했지만 약간의 피해가 있습니다.`);
    } else {
      hive.beeCount = Math.floor(hive.beeCount * 0.3);
      s.notifications.push(`💀 말벌 습격으로 ${hive.name}의 봉군이 큰 피해를 입었습니다!`);
    }
  } else {
    if (action === 'kill') {
      s.notifications.push(`✅ 정찰 말벌을 제거했습니다. 습격이 예방됩니다.`);
      s.experience += 30;
    } else {
      s.notifications.push(`⚠️ 정찰 말벌을 놓쳤습니다. 집단 습격이 올 수 있습니다.`);
    }
  }
  return s;
}

export function resolveQueenAgingEvent(state: GameState, eventId: string, action: 'replace' | 'ignore'): GameState {
  const s = { ...state, events: state.events.map(e => ({ ...e })), notifications: [...state.notifications] };
  const event = s.events.find(e => e.id === eventId);
  if (!event) return s;
  event.resolved = true;
  if (action === 'replace') {
    return replaceQueen(s, event.hiveId);
  }
  s.notifications.push(`⏳ ${event.hiveName}의 여왕 교체를 보류합니다.`);
  return s;
}

// ─── Research ───
export function purchaseResearch(state: GameState, researchId: string): GameState {
  const node = RESEARCH_TREE.find(r => r.id === researchId);
  if (!node || state.research[researchId]) return state;
  if (!node.prereqs.every(p => state.research[p])) return state;
  if (state.gold < node.cost.gold) return state;
  if ((node.cost.wax || 0) > state.wax) return state;
  if ((node.cost.royalJelly || 0) > state.royalJelly) return state;

  const s = { ...state, research: { ...state.research } };
  s.gold -= node.cost.gold;
  s.wax -= node.cost.wax || 0;
  s.royalJelly -= node.cost.royalJelly || 0;
  s.research[researchId] = true;
  s.experience += 50;
  return s;
}

// ─── Crafting ───
export function craftItem(state: GameState, recipeId: string): GameState {
  const recipe = CRAFT_RECIPES.find(r => r.id === recipeId);
  if (!recipe) return state;
  if (recipeId === 'candle' || recipeId === 'foundation' || recipeId === 'propolis_tincture') {
    if (!state.research['wax_processing']) return state;
  }
  if (recipeId === 'hornet_trap' || recipeId === 'hornet_net') {
    if (!state.research['hornet_defense']) return state;
  }
  if (recipeId === 'queen_cage') {
    if (!state.research['queen_rearing']) return state;
  }
  if ((recipe.inputs.wax || 0) > state.wax) return state;
  if ((recipe.inputs.honey || 0) > state.honey) return state;
  if ((recipe.inputs.gold || 0) > state.gold) return state;

  const s = { ...state, craftedItems: { ...state.craftedItems } };
  s.wax -= recipe.inputs.wax || 0;
  s.honey -= recipe.inputs.honey || 0;
  s.gold -= recipe.inputs.gold || 0;

  if (recipe.output.type === 'gold') {
    s.gold += recipe.output.value;
  } else {
    s.craftedItems[recipeId] = (s.craftedItems[recipeId] || 0) + 1;
  }
  s.experience += 20;
  return s;
}

// ─── Inspection card action ───
export function applyInspectionAction(state: GameState, hiveId: string, cardType: InspectionCardType, actionId?: string): GameState {
  const s = { ...state, hives: state.hives.map(h => ({ ...h })), notifications: [...state.notifications] };
  const hive = s.hives.find(h => h.id === hiveId);
  if (!hive) return s;

  switch (cardType) {
    case 'queen_cell':
      if (actionId === 'remove_cell') { hive.swarmRisk = Math.max(0, hive.swarmRisk - 30); }
      break;
    case 'healthy_brood': hive.broodHealth = Math.min(100, hive.broodHealth + 5); break;
    case 'queen_found':
      if (actionId === 'mark_queen') { hive.queenMarked = true; s.experience += 10; }
      hive.queenHealth = Math.min(100, hive.queenHealth + 3);
      break;
    case 'strong_colony': s.experience += 10; break;
    case 'laying_worker':
      if (actionId === 'merge') return resolveLayingWorker(s, hiveId, 'merge');
      if (actionId === 'introduce_larva') return resolveLayingWorker(s, hiveId, 'introduce_larva');
      if (actionId === 'buy_queen') return resolveLayingWorker(s, hiveId, 'buy_queen');
      break;
    case 'queen_absent':
      if (actionId === 'buy_queen') return replaceQueen(s, hiveId);
      if (actionId === 'emergency_cell') return rearQueen(s, hiveId, s.hives.find(h => h.id !== hiveId && h.beeCount > 5000)?.id || '');
      break;
    case 'drone_brood_excess':
      if (actionId === 'check_laying') {
        // Reveal laying worker status earlier
        if (hive.queenStatus === 'absent') {
          s.notifications.push(`🔍 정밀 검사 결과: 동봉산란 초기 징후를 발견했습니다!`);
          hive.queenStatus = 'laying_worker';
        }
      }
      break;
    default: break;
  }
  hive.lastInspection = s.totalGameDays;
  s.experience += 15;
  return s;
}

// ─── Prestige ───
export function performPrestige(state: GameState, targetRegion: Region): GameState {
  const fameToProdBoost = Math.floor(state.fame / 20); // 5% per 100 fame
  const fameToGold = Math.floor(state.fame * 2);
  const researchToKeep = Object.keys(state.research).filter(r => {
    // Keep basic researches
    return ['organic_treatment', 'queen_marking', 'advanced_uncapping', 'auto_feeder'].includes(r) && state.research[r];
  });

  const newPrestige: PrestigeData = {
    totalPrestigeResets: state.prestige.totalPrestigeResets + 1,
    lifetimeFame: state.prestige.lifetimeFame + state.fame,
    permanentBonuses: {
      productionBoost: state.prestige.permanentBonuses.productionBoost + fameToProdBoost,
      startingGold: state.prestige.permanentBonuses.startingGold + fameToGold,
      researchCarryover: [...new Set([...state.prestige.permanentBonuses.researchCarryover, ...researchToKeep])],
    },
  };

  return createInitialState(newPrestige, targetRegion);
}

// ─── Offline ───
export function calculateOfflineProgress(state: GameState): { newState: GameState; report: OfflineReport } {
  const now = Date.now();
  const elapsed = now - state.lastOnlineTime;
  const minutesElapsed = Math.min(elapsed / 60_000, 1440);
  const report: OfflineReport = { duration: formatDuration(elapsed), honeyProduced: 0, varroaChanges: [], beeChanges: [], seasonChanges: [], alerts: [] };
  if (minutesElapsed < 1) return { newState: { ...state, lastOnlineTime: now }, report };

  const oldHives = state.hives.map(h => ({ id: h.id, name: h.name, varroa: h.varroaLevel, bees: h.beeCount }));
  const oldHoney = state.hives.reduce((sum, h) => sum + h.honeyStored, 0);

  let s = { ...state };
  const daysToSimulate = Math.floor(minutesElapsed / 60);
  for (let d = 0; d < Math.min(daysToSimulate, 28); d++) {
    const result = advanceDay(s);
    s = result.state;
    if (result.newSeason) report.seasonChanges.push(s.season);
  }

  const newHoney = s.hives.reduce((sum, h) => sum + h.honeyStored, 0);
  report.honeyProduced = Math.max(0, newHoney - oldHoney);

  for (const oldH of oldHives) {
    const newH = s.hives.find(h => h.id === oldH.id);
    if (!newH) continue;
    if (Math.abs(newH.varroaLevel - oldH.varroa) > 3) report.varroaChanges.push({ hiveId: oldH.id, hiveName: oldH.name, oldLevel: Math.round(oldH.varroa), newLevel: Math.round(newH.varroaLevel) });
    const beeDiff = newH.beeCount - oldH.bees;
    if (Math.abs(beeDiff) > 500) report.beeChanges.push({ hiveId: oldH.id, hiveName: oldH.name, change: Math.round(beeDiff) });
    if (newH.beeCount === 0 && oldH.bees > 0) report.alerts.push(`⚠️ ${oldH.name}의 봉군이 소멸했습니다!`);
    if (newH.varroaLevel > 60 && oldH.varroa <= 60) report.alerts.push(`🔴 ${oldH.name}의 바로아 레벨이 위험 수준입니다!`);
  }

  s.lastOnlineTime = now;
  return { newState: s, report };
}

function formatDuration(ms: number): string {
  const minutes = Math.floor(ms / 60_000);
  if (minutes < 60) return `${minutes}분`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}시간 ${minutes % 60}분`;
  return `${Math.floor(hours / 24)}일 ${hours % 24}시간`;
}

// ─── Equip items to hives ───
export function equipHornetTrap(state: GameState, hiveId: string): GameState {
  if (!state.craftedItems['hornet_trap'] || state.craftedItems['hornet_trap'] < 1) return state;
  const s = { ...state, hives: state.hives.map(h => ({ ...h })), craftedItems: { ...state.craftedItems } };
  const hive = s.hives.find(h => h.id === hiveId);
  if (!hive || hive.hasHornetTrap) return state;
  hive.hasHornetTrap = true;
  s.craftedItems['hornet_trap'] -= 1;
  return s;
}

export function equipHornetNet(state: GameState, hiveId: string): GameState {
  if (!state.craftedItems['hornet_net'] || state.craftedItems['hornet_net'] < 1) return state;
  const s = { ...state, hives: state.hives.map(h => ({ ...h })), craftedItems: { ...state.craftedItems } };
  const hive = s.hives.find(h => h.id === hiveId);
  if (!hive || hive.hasHornetNet) return state;
  hive.hasHornetNet = true;
  s.craftedItems['hornet_net'] -= 1;
  return s;
}
