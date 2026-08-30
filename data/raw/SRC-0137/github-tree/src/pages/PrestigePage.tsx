import { useState } from 'react';
import { useGame } from '@/game/GameContext';
import BottomNav from '@/components/game/BottomNav';
import ResourceBar from '@/components/game/ResourceBar';
import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { REGIONS, type Region } from '@/game/types';
import { motion } from 'framer-motion';

export default function PrestigePage() {
  const { state, doPrestige } = useGame();
  const navigate = useNavigate();
  const [selectedRegion, setSelectedRegion] = useState<Region>('default');
  const [confirming, setConfirming] = useState(false);
  if (!state) return null;

  const fameToProdBoost = Math.floor(state.fame / 20);
  const fameToGold = Math.floor(state.fame * 2);

  return (
    <div className="min-h-screen bg-background flex flex-col pb-16">
      <header className="flex items-center gap-2 px-4 pt-4 pb-2">
        <button onClick={() => navigate('/')} className="p-1.5 rounded-lg hover:bg-secondary"><ArrowLeft className="w-5 h-5 text-muted-foreground" /></button>
        <h1 className="font-serif text-xl font-bold text-foreground">🌟 프레스티지</h1>
      </header>

      <div className="px-3 mb-3"><ResourceBar /></div>

      <main className="flex-1 px-3 pb-4 overflow-y-auto space-y-5">
        {/* Current status */}
        <div className="game-panel p-4">
          <h3 className="game-section-title">📊 현재 양봉장</h3>
          <div className="space-y-1.5 text-sm">
            <Row label="명성" value={`⭐ ${state.fame}`} />
            <Row label="지역" value={REGIONS.find(r => r.id === state.region)?.name || '중부'} />
            <Row label="프레스티지 횟수" value={`${state.prestige.totalPrestigeResets}회`} />
            <Row label="누적 명성" value={`${state.prestige.lifetimeFame}`} />
          </div>
        </div>

        {/* Current bonuses */}
        {state.prestige.totalPrestigeResets > 0 && (
          <div className="game-panel p-4 border-accent/30">
            <h3 className="game-section-title">💎 영구 보너스</h3>
            <div className="space-y-1.5 text-sm">
              <Row label="생산 보너스" value={`+${state.prestige.permanentBonuses.productionBoost}%`} />
              <Row label="시작 골드 보너스" value={`+${state.prestige.permanentBonuses.startingGold}💰`} />
              <Row label="유지 연구" value={`${state.prestige.permanentBonuses.researchCarryover.length}개`} />
            </div>
          </div>
        )}

        {/* Preview of new bonuses */}
        <div className="game-panel p-4 border-primary/30 bg-primary/3">
          <h3 className="game-section-title">🔮 리셋 시 보상 미리보기</h3>
          <div className="space-y-1.5 text-sm">
            <Row label="추가 생산 보너스" value={`+${fameToProdBoost}%`} />
            <Row label="추가 시작 골드" value={`+${fameToGold}💰`} />
            <Row label="유지되는 기본 연구" value="유기 방제, 여왕 표시, 고급 탈개도, 자동 급이" />
          </div>
          {state.fame < 10 && (
            <p className="text-[10px] text-warning mt-2 font-bold">⚠️ 명성이 10 이상일 때 프레스티지를 권장합니다.</p>
          )}
        </div>

        {/* Region selection */}
        <div>
          <h3 className="game-section-title">🗺️ 새 양봉장 지역 선택</h3>
          <div className="space-y-2">
            {REGIONS.map((region, i) => {
              const locked = state.prestige.lifetimeFame + state.fame < region.unlockFame;
              return (
                <motion.button
                  key={region.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  onClick={() => !locked && setSelectedRegion(region.id)}
                  disabled={locked}
                  className={`w-full game-panel p-3 text-left transition-all ${
                    selectedRegion === region.id ? 'border-primary/50 bg-primary/5 ring-1 ring-primary/20' : ''
                  } ${locked ? 'opacity-35 grayscale cursor-not-allowed' : ''}`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xl">{region.icon}</span>
                    <span className="font-bold text-sm text-foreground">{region.name}</span>
                    {locked && <span className="text-[10px] text-muted-foreground bg-secondary rounded px-1.5 py-0.5">🔒 명성 {region.unlockFame}</span>}
                    {selectedRegion === region.id && <span className="text-xs text-primary ml-auto font-bold">✓ 선택됨</span>}
                  </div>
                  <p className="text-[11px] text-muted-foreground">{region.description}</p>
                </motion.button>
              );
            })}
          </div>
        </div>

        {/* Prestige button */}
        {!confirming ? (
          <button onClick={() => setConfirming(true)}
            className="w-full py-3 rounded-xl honey-gradient text-primary-foreground game-btn text-sm">
            🌟 새 양봉장 시작 (프레스티지)
          </button>
        ) : (
          <div className="game-panel p-4 border-danger/40 bg-danger/5">
            <p className="text-xs text-foreground mb-3 font-medium">
              ⚠️ <strong>정말 프레스티지하시겠습니까?</strong><br />
              현재 양봉장의 모든 진행 상황이 리셋됩니다. 영구 보너스만 유지됩니다.
            </p>
            <div className="flex gap-2">
              <button onClick={() => { doPrestige(selectedRegion); navigate('/'); }}
                className="flex-1 py-2.5 rounded-xl bg-danger text-primary-foreground game-btn-danger text-xs">
                확인 - 리셋!
              </button>
              <button onClick={() => setConfirming(false)}
                className="flex-1 py-2.5 rounded-xl border-2 border-border text-muted-foreground text-xs font-bold hover:bg-secondary">
                취소
              </button>
            </div>
          </div>
        )}
      </main>

      <BottomNav />
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between">
      <span className="text-muted-foreground text-xs">{label}</span>
      <span className="text-foreground font-bold text-xs">{value}</span>
    </div>
  );
}
