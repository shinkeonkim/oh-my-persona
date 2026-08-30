import { createContext, useContext, useState, useEffect, useCallback, useRef, type ReactNode } from 'react';
import { GameState, GameSpeed, OfflineReport, InspectionCard, InspectionCardType, HoneyType, Region } from './types';
import {
  createInitialState, saveGame, loadGame, deleteGame,
  advanceDay, calculateOfflineProgress, checkLevelUp,
  harvestHoney, sellHoney, sellHoneyByType, treatVarroa, feedBees,
  addFrame, installSuper, buyHive, expandSlots, upgradeExtractor,
  resolveSwarmEvent, resolveHornetEvent, resolveQueenAgingEvent,
  purchaseResearch, craftItem,
  generateInspectionCards, applyInspectionAction, equipHornetTrap, equipHornetNet,
  markQueen, replaceQueen, resolveLayingWorker, performPrestige,
} from './engine';

const AUTO_SAVE_INTERVAL = 30_000;
const GAME_TICK_INTERVAL = 10_000;

interface GameContextType {
  state: GameState | null;
  offlineReport: OfflineReport | null;
  showOfflineReport: boolean;
  dismissReport: () => void;
  dispatch: (action: (s: GameState) => GameState) => void;
  doHarvest: (hiveId: string) => void;
  doSell: (amount: number) => void;
  doSellByType: (type: HoneyType, amount: number) => void;
  doTreatVarroa: (hiveId: string, method: 'amitraz' | 'oxalic' | 'drone_removal') => void;
  doFeed: (hiveId: string) => void;
  doAddFrame: (hiveId: string) => void;
  doInstallSuper: (hiveId: string) => void;
  doBuyHive: () => void;
  doExpandSlots: () => void;
  doUpgradeExtractor: () => void;
  doSave: () => void;
  doReset: () => void;
  doSetSpeed: (speed: GameSpeed) => void;
  doResolveSwarm: (eventId: string, action: 'capture' | 'ignore') => void;
  doResolveHornet: (eventId: string, action: 'kill' | 'trap' | 'ignore') => void;
  doResolveQueenAging: (eventId: string, action: 'replace' | 'ignore') => void;
  doResearch: (researchId: string) => void;
  doCraft: (recipeId: string) => void;
  doInspect: (hiveId: string) => InspectionCard[];
  doApplyCard: (hiveId: string, cardType: InspectionCardType, actionId?: string) => void;
  doEquipTrap: (hiveId: string) => void;
  doEquipNet: (hiveId: string) => void;
  doMarkQueen: (hiveId: string) => void;
  doReplaceQueen: (hiveId: string) => void;
  doResolveLayingWorker: (hiveId: string, action: 'merge' | 'introduce_larva' | 'buy_queen' | 'abandon') => void;
  doPrestige: (region: Region) => void;
  clearNotifications: () => void;
}

const GameContext = createContext<GameContextType | null>(null);

export function GameProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<GameState | null>(null);
  const [offlineReport, setOfflineReport] = useState<OfflineReport | null>(null);
  const [showOfflineReport, setShowOfflineReport] = useState(false);
  const tickRef = useRef<ReturnType<typeof setInterval>>();
  const saveRef = useRef<ReturnType<typeof setInterval>>();

  useEffect(() => {
    try {
      const saved = loadGame();
      if (saved) {
        const { newState, report } = calculateOfflineProgress(saved);
        setState(checkLevelUp(newState));
        if (report.honeyProduced > 0.1 || report.alerts.length > 0 || report.seasonChanges.length > 0) {
          setOfflineReport(report);
          setShowOfflineReport(true);
        }
      } else {
        setState(createInitialState());
      }
    } catch (e) {
      console.error('Game init failed, resetting:', e);
      deleteGame();
      setState(createInitialState());
    }
  }, []);

  useEffect(() => {
    if (!state) return;
    tickRef.current = setInterval(() => {
      setState(prev => {
        if (!prev) return prev;
        const { state: newState } = advanceDay(prev);
        return checkLevelUp(newState);
      });
    }, GAME_TICK_INTERVAL);
    return () => clearInterval(tickRef.current);
  }, [state?.gameSpeed]);

  useEffect(() => {
    if (!state) return;
    saveRef.current = setInterval(() => {
      setState(prev => { if (prev) saveGame(prev); return prev; });
    }, AUTO_SAVE_INTERVAL);
    return () => clearInterval(saveRef.current);
  }, []);

  const dispatch = useCallback((action: (s: GameState) => GameState) => {
    setState(prev => prev ? checkLevelUp(action(prev)) : prev);
  }, []);

  const value: GameContextType = {
    state, offlineReport, showOfflineReport,
    dismissReport: useCallback(() => setShowOfflineReport(false), []),
    dispatch,
    doHarvest: useCallback((id: string) => dispatch(s => harvestHoney(s, id)), [dispatch]),
    doSell: useCallback((amt: number) => dispatch(s => sellHoney(s, amt)), [dispatch]),
    doSellByType: useCallback((type: HoneyType, amt: number) => dispatch(s => sellHoneyByType(s, type, amt)), [dispatch]),
    doTreatVarroa: useCallback((id: string, m: 'amitraz' | 'oxalic' | 'drone_removal') => dispatch(s => treatVarroa(s, id, m)), [dispatch]),
    doFeed: useCallback((id: string) => dispatch(s => feedBees(s, id)), [dispatch]),
    doAddFrame: useCallback((id: string) => dispatch(s => addFrame(s, id)), [dispatch]),
    doInstallSuper: useCallback((id: string) => dispatch(s => installSuper(s, id)), [dispatch]),
    doBuyHive: useCallback(() => dispatch(s => buyHive(s)), [dispatch]),
    doExpandSlots: useCallback(() => dispatch(s => expandSlots(s)), [dispatch]),
    doUpgradeExtractor: useCallback(() => dispatch(s => upgradeExtractor(s)), [dispatch]),
    doSave: useCallback(() => setState(prev => { if (prev) saveGame(prev); return prev; }), []),
    doReset: useCallback(() => { deleteGame(); setState(createInitialState()); }, []),
    doSetSpeed: useCallback((speed: GameSpeed) => dispatch(s => ({ ...s, gameSpeed: speed })), [dispatch]),
    doResolveSwarm: useCallback((eventId: string, action: 'capture' | 'ignore') => dispatch(s => resolveSwarmEvent(s, eventId, action)), [dispatch]),
    doResolveHornet: useCallback((eventId: string, action: 'kill' | 'trap' | 'ignore') => dispatch(s => resolveHornetEvent(s, eventId, action)), [dispatch]),
    doResolveQueenAging: useCallback((eventId: string, action: 'replace' | 'ignore') => dispatch(s => resolveQueenAgingEvent(s, eventId, action)), [dispatch]),
    doResearch: useCallback((id: string) => dispatch(s => purchaseResearch(s, id)), [dispatch]),
    doCraft: useCallback((id: string) => dispatch(s => craftItem(s, id)), [dispatch]),
    doInspect: useCallback((hiveId: string) => {
      if (!state) return [];
      const hive = state.hives.find(h => h.id === hiveId);
      if (!hive) return [];
      return generateInspectionCards(hive, state.season, state.research);
    }, [state]),
    doApplyCard: useCallback((hiveId: string, cardType: InspectionCardType, actionId?: string) => dispatch(s => applyInspectionAction(s, hiveId, cardType, actionId)), [dispatch]),
    doEquipTrap: useCallback((id: string) => dispatch(s => equipHornetTrap(s, id)), [dispatch]),
    doEquipNet: useCallback((id: string) => dispatch(s => equipHornetNet(s, id)), [dispatch]),
    doMarkQueen: useCallback((id: string) => dispatch(s => markQueen(s, id)), [dispatch]),
    doReplaceQueen: useCallback((id: string) => dispatch(s => replaceQueen(s, id)), [dispatch]),
    doResolveLayingWorker: useCallback((hiveId: string, action: 'merge' | 'introduce_larva' | 'buy_queen' | 'abandon') => dispatch(s => resolveLayingWorker(s, hiveId, action)), [dispatch]),
    doPrestige: useCallback((region: Region) => {
      setState(prev => {
        if (!prev) return prev;
        const newState = performPrestige(prev, region);
        saveGame(newState);
        return newState;
      });
    }, []),
    clearNotifications: useCallback(() => dispatch(s => ({ ...s, notifications: [] })), [dispatch]),
  };

  return <GameContext.Provider value={value}>{children}</GameContext.Provider>;
}

export function useGame() {
  const ctx = useContext(GameContext);
  if (!ctx) throw new Error('useGame must be used within GameProvider');
  return ctx;
}
