import { useState } from 'react';
import { useGame } from '@/game/GameContext';
import ResourceBar from '@/components/game/ResourceBar';
import HiveCard from '@/components/game/HiveCard';
import HiveDetail from '@/components/game/HiveDetail';
import SeasonInfo from '@/components/game/SeasonInfo';
import BottomNav from '@/components/game/BottomNav';
import ApiaryScene from '@/components/game/ApiaryScene';
import EventModal from '@/components/game/EventModal';
import OfflineReportModal from '@/components/game/OfflineReportModal';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import type { GameEvent } from '@/game/types';

const Index = () => {
  const {
    state, offlineReport, showOfflineReport, dismissReport, doBuyHive, clearNotifications,
  } = useGame();
  const navigate = useNavigate();

  const [selectedHiveId, setSelectedHiveId] = useState<string | null>(null);
  const [activeEvent, setActiveEvent] = useState<GameEvent | null>(null);

  if (!state) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="text-center">
          <div className="text-4xl mb-3 animate-bee">🐝</div>
          <p className="text-muted-foreground font-serif">양봉장을 준비하는 중...</p>
        </div>
      </div>
    );
  }

  const selectedHive = state.hives.find(h => h.id === selectedHiveId) || null;
  const emptySlots = state.maxHiveSlots - state.hives.length;
  const unresolvedEvents = state.events.filter(e => !e.resolved);

  return (
    <div className="min-h-screen bg-background flex flex-col pb-16">
      {/* Title */}
      <header className="text-center pt-3 pb-1 px-4">
        <h1 className="font-serif text-xl font-bold text-foreground tracking-wide">🐝 나의 작은 양봉장</h1>
      </header>

      {/* Resource Bar */}
      <div className="px-3 mb-2">
        <ResourceBar />
      </div>

      {/* Notifications */}
      {state.notifications.length > 0 && (
        <div className="px-3 mb-2">
          <div className="game-panel p-2.5 space-y-1 border-honey/30">
            {state.notifications.slice(-3).map((n, i) => (
              <p key={i} className="text-xs text-foreground">📢 {n}</p>
            ))}
            <button onClick={clearNotifications} className="text-[10px] text-muted-foreground hover:text-foreground font-medium">✕ 알림 지우기</button>
          </div>
        </div>
      )}

      {/* Event alerts */}
      {unresolvedEvents.length > 0 && (
        <div className="px-3 mb-2 space-y-1.5">
          {unresolvedEvents.map(event => (
            <motion.button
              key={event.id}
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              onClick={() => setActiveEvent(event)}
              className={`w-full game-panel p-2.5 text-left text-xs font-bold animate-pulse ${
                event.type === 'hornet_attack' ? 'border-danger/50 bg-danger/5' :
                event.type === 'swarming' ? 'border-warning/50 bg-warning/5' :
                'border-honey/50 bg-honey/5'
              }`}>
              {event.type === 'swarming' && `🐝 ${event.hiveName}에서 분봉 발생! 탭하여 대응하세요`}
              {event.type === 'hornet_scout' && `⚠️ ${event.hiveName} 근처 정찰 말벌! 탭하여 대응`}
              {event.type === 'hornet_attack' && `🚨 ${event.hiveName}에 말벌 습격 중! 긴급 대응 필요!`}
            </motion.button>
          ))}
        </div>
      )}

      {/* Main apiary area */}
      <main className="flex-1 px-3 pb-3 overflow-y-auto">
        <ApiaryScene season={state.season}>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <AnimatePresence>
              {state.hives.map((hive, i) => (
                <motion.div key={hive.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
                  <HiveCard
                    hive={hive}
                    onClick={() => setSelectedHiveId(hive.id)}
                    hasEvent={unresolvedEvents.some(e => e.hiveId === hive.id)}
                  />
                </motion.div>
              ))}
            </AnimatePresence>

            {Array.from({ length: emptySlots }).map((_, i) => (
              <motion.button key={`empty-${i}`} onClick={doBuyHive}
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                className="game-panel p-3 border-dashed border-2 flex flex-col items-center justify-center gap-1.5
                  text-muted-foreground hover:text-foreground hover:border-primary/40 transition-colors min-h-[180px]">
                <span className="text-2xl">➕</span>
                <span className="text-[10px] font-bold">벌통 추가</span>
                <span className="text-[10px] text-primary font-bold">300💰</span>
              </motion.button>
            ))}

            {state.maxHiveSlots < 6 && (
              <button onClick={() => navigate('/shop')}
                className="game-panel p-3 border-dashed border-2 flex flex-col items-center justify-center gap-1.5 text-muted-foreground/50 min-h-[180px]">
                <span className="text-2xl">🔒</span>
                <span className="text-[10px] font-bold">슬롯 확장</span>
              </button>
            )}
          </div>
        </ApiaryScene>

        <SeasonInfo />
      </main>

      <BottomNav />

      {/* Modals */}
      {selectedHive && (
        <HiveDetail hive={selectedHive} onClose={() => setSelectedHiveId(null)} />
      )}

      {activeEvent && (
        <EventModal event={activeEvent} onClose={() => setActiveEvent(null)} />
      )}

      {showOfflineReport && offlineReport && (
        <OfflineReportModal report={offlineReport} onDismiss={dismissReport} />
      )}
    </div>
  );
};

export default Index;
