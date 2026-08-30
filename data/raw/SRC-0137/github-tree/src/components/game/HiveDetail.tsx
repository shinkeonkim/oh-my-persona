import { useState } from 'react';
import { type Hive, type InspectionCard, getVarroaStatus, type QueenStatus } from '@/game/types';
import { useGame } from '@/game/GameContext';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import InspectionModal from './InspectionModal';

interface HiveDetailProps {
  hive: Hive;
  onClose: () => void;
}

const queenStatusLabels: Record<QueenStatus, { label: string; color: string }> = {
  healthy: { label: '건강', color: 'text-safe' },
  aging: { label: '노화', color: 'text-warning' },
  absent: { label: '부재', color: 'text-danger' },
  replacing: { label: '교체 중', color: 'text-primary' },
  laying_worker: { label: '동봉산란', color: 'text-danger' },
};

export default function HiveDetail({ hive, onClose }: HiveDetailProps) {
  const {
    state, doHarvest, doFeed, doAddFrame, doInstallSuper, doTreatVarroa,
    doInspect, doEquipTrap, doEquipNet, doMarkQueen, doReplaceQueen, doResolveLayingWorker,
  } = useGame();
  const [inspectionCards, setInspectionCards] = useState<InspectionCard[] | null>(null);

  if (!state) return null;
  const { gold } = state;
  const varroaStatus = getVarroaStatus(hive.varroaLevel);
  const honeyPercent = (hive.honeyStored / hive.honeyCapacity) * 100;
  const beePercent = Math.min(100, (hive.beeCount / 60000) * 100);
  const isDead = hive.beeCount === 0;
  const qs = queenStatusLabels[hive.queenStatus];

  const handleInspect = () => {
    const cards = doInspect(hive.id);
    setInspectionCards(cards);
  };

  return (
    <>
      <AnimatePresence>
        <motion.div
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-foreground/40 backdrop-blur-sm p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, y: 30 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.9, y: 30 }}
            transition={{ type: 'spring', damping: 25, stiffness: 350 }}
            onClick={(e) => e.stopPropagation()}
            className="game-panel w-full max-w-md max-h-[85vh] overflow-y-auto p-0"
          >
            {/* Header */}
            <div className="relative px-5 pt-5 pb-3 border-b-2 border-border/60">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <span className="text-3xl animate-float">🏠</span>
                  <div>
                    <h2 className="font-serif text-xl font-bold text-foreground">{hive.name}</h2>
                    <div className="flex items-center gap-1.5 mt-0.5">
                      <span className={`inline-block w-2 h-2 rounded-full ${isDead ? 'bg-danger' : 'bg-safe'}`} />
                      <span className="text-[10px] text-muted-foreground font-medium">{isDead ? '소멸' : '활성'}</span>
                    </div>
                  </div>
                </div>
                <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-secondary transition-colors border border-border/60">
                  <X className="w-4 h-4 text-muted-foreground" />
                </button>
              </div>
            </div>

            <div className="p-5 space-y-4">
              {isDead && (
                <div className="bg-danger/10 border-2 border-danger/30 rounded-xl p-3 text-sm text-danger font-medium">
                  ⚠️ 봉군이 소멸했습니다.
                </div>
              )}

              {hive.queenStatus === 'laying_worker' && (
                <div className="bg-danger/10 border-2 border-danger/30 rounded-xl p-3 text-sm text-danger font-medium">
                  🥚 동봉산란이 진행 중입니다! 긴급 대응이 필요합니다.
                </div>
              )}

              {/* Stats Grid */}
              <div className="grid grid-cols-2 gap-2 text-center">
                <Stat icon="🐝" label="봉군" value={`${(hive.beeCount / 1000).toFixed(1)}k`} />
                <Stat icon="📋" label="프레임" value={`${hive.frameCount}/${hive.maxFrames}장`} />
                <Stat icon="👑" label="여왕" value={qs.label} color={qs.color} />
                <Stat icon="🥚" label="육아" value={`${hive.broodHealth.toFixed(0)}%`} />
              </div>

              {/* Queen Info */}
              <div className="game-panel !border !rounded-lg p-3 space-y-2">
                <p className="game-section-title !text-xs !mb-1 !pb-1">👑 여왕 정보</p>
                <InfoRow label="건강" value={`${hive.queenHealth}%`} danger={hive.queenHealth < 50} />
                <InfoRow label="나이" value={`${hive.queenAge.toFixed(1)}년`} />
                <InfoRow label="마킹" value={hive.queenMarked ? '✅ 완료' : '❌ 미완'} />
              </div>

              {/* Progress Bars */}
              <div className="space-y-2.5">
                <BarStat label="🍯 저밀" value={`${hive.honeyStored.toFixed(1)}/${hive.honeyCapacity}kg`} percent={honeyPercent} barClass="honey-gradient" />
                <BarStat label="🐝 봉군" value={`${(hive.beeCount / 1000).toFixed(1)}k`} percent={beePercent} barClass="bg-primary" />
                <BarStat label="🦠 바로아" value={`${Math.round(hive.varroaLevel)}%`}
                  percent={hive.varroaLevel}
                  barClass={varroaStatus === 'safe' ? 'bg-safe' : varroaStatus === 'caution' ? 'bg-warning' : 'bg-danger'}
                  valueClass={varroaStatus === 'safe' ? 'text-safe' : varroaStatus === 'caution' ? 'text-warning' : 'text-danger'} />
              </div>

              {hive.swarmRisk > 10 && (
                <div className="bg-warning/10 border border-warning/30 rounded-xl p-2.5 text-xs text-foreground font-medium">
                  ⚠️ 분봉 위험도: <span className="font-bold text-warning">{Math.round(hive.swarmRisk)}%</span>
                </div>
              )}

              {/* Equipment */}
              <div className="flex flex-wrap gap-1.5 text-[10px]">
                <EquipBadge active={hive.hasSuper} label="계상" />
                <EquipBadge active={hive.hasQueenExcluder} label="격왕판" />
                <EquipBadge active={hive.hasHornetTrap} label="말벌 트랩" />
                <EquipBadge active={hive.hasHornetNet} label="말벌 그물" />
                <EquipBadge active={hive.queenMarked} label="여왕 마킹" />
              </div>

              {/* Actions */}
              <div className="space-y-2">
                <p className="game-section-title">🎮 행동</p>
                <GameBtn onClick={handleInspect} disabled={isDead} icon="🔍" label="벌통 점검" desc="상태 카드를 확인합니다" />
                <GameBtn onClick={() => doHarvest(hive.id)} disabled={hive.honeyStored < 1 || isDead} icon="🍯" label="채밀하기" desc={`${hive.honeyStored.toFixed(1)}kg 수확`} primary />
                <GameBtn onClick={() => doFeed(hive.id)} disabled={gold < (state.research['auto_feeder'] ? 21 : 30) || isDead} icon="🥤" label="급이" desc={`${state.research['auto_feeder'] ? 21 : 30}골드`} />
                <GameBtn onClick={() => doAddFrame(hive.id)} disabled={hive.frameCount >= hive.maxFrames || gold < 40} icon="📋" label="소초 추가" desc="40골드" />
                {!hive.hasSuper && <GameBtn onClick={() => doInstallSuper(hive.id)} disabled={gold < 100 || isDead} icon="📦" label="계상 설치" desc="100골드" />}
              </div>

              {/* Queen Management */}
              <div className="space-y-1.5">
                <p className="game-section-title">👑 여왕 관리</p>
                {!hive.queenMarked && hive.queenStatus !== 'absent' && hive.queenStatus !== 'laying_worker' && state.research['queen_marking'] && (
                  <GameBtn onClick={() => doMarkQueen(hive.id)} disabled={false} icon="🏷️" label="여왕 마킹" desc="점검 시 발견 확률 ↑" small />
                )}
                {(hive.queenStatus === 'aging' || hive.queenStatus === 'absent') && (
                  <GameBtn onClick={() => doReplaceQueen(hive.id)} disabled={gold < 200} icon="👑" label="새 여왕 구입" desc="200골드 (성공률 85%)" small />
                )}
                {hive.queenStatus === 'laying_worker' && (
                  <>
                    <GameBtn onClick={() => doResolveLayingWorker(hive.id, 'merge')} disabled={state.hives.filter(h => h.id !== hive.id && h.beeCount > 0).length === 0} icon="🔄" label="합봉" desc="다른 벌통에 흡수" small />
                    <GameBtn onClick={() => doResolveLayingWorker(hive.id, 'buy_queen')} disabled={gold < 200} icon="👑" label="새 여왕 도입" desc={`200골드 ${(state.craftedItems['queen_cage'] || 0) > 0 ? '(왕롱 보유 ✅)' : '(왕롱 없음 — 위험!)'}`} small />
                    <GameBtn onClick={() => doResolveLayingWorker(hive.id, 'introduce_larva')} disabled={state.hives.filter(h => h.id !== hive.id && h.beeCount > 5000).length === 0} icon="🥚" label="유충 도입" desc="무료 (성공률 60%)" small />
                  </>
                )}
              </div>

              {/* Hornet Equipment */}
              {state.research['hornet_defense'] && (
                <div className="space-y-1.5">
                  <p className="game-section-title">🐝 말벌 방어</p>
                  {!hive.hasHornetTrap && (state.craftedItems['hornet_trap'] || 0) > 0 && (
                    <GameBtn onClick={() => doEquipTrap(hive.id)} disabled={false} icon="🪤" label="말벌 트랩 장착" desc="보유 트랩 사용" small />
                  )}
                  {!hive.hasHornetNet && (state.craftedItems['hornet_net'] || 0) > 0 && (
                    <GameBtn onClick={() => doEquipNet(hive.id)} disabled={false} icon="🥅" label="말벌 그물 장착" desc="보유 그물 사용" small />
                  )}
                </div>
              )}

              {/* Varroa Treatment */}
              <div className="space-y-1.5">
                <p className="game-section-title">🦠 방제</p>
                <GameBtn onClick={() => doTreatVarroa(hive.id, 'amitraz')} disabled={gold < 50} icon="💊" label="아미트라즈" desc="50골드 / -45" small />
                <GameBtn onClick={() => doTreatVarroa(hive.id, 'oxalic')} disabled={gold < 20} icon="💨" label="옥살산" desc={`20골드 / -${35 + (state.research['organic_treatment'] ? 15 : 0)}`} small />
                <GameBtn onClick={() => doTreatVarroa(hive.id, 'drone_removal')} disabled={isDead} icon="🔪" label="수벌방 제거" desc="무료 / -12" small />
              </div>
            </div>
          </motion.div>
        </motion.div>
      </AnimatePresence>

      {inspectionCards && (
        <InspectionModal hiveId={hive.id} cards={inspectionCards} onClose={() => setInspectionCards(null)} />
      )}
    </>
  );
}

/* ── Sub-components ── */

function Stat({ icon, label, value, color }: { icon: string; label: string; value: string; color?: string }) {
  return (
    <div className="game-panel !border !rounded-lg p-2.5">
      <div className="text-lg mb-0.5">{icon}</div>
      <div className={`font-bold text-sm ${color || 'text-foreground'}`}>{value}</div>
      <div className="text-[10px] text-muted-foreground">{label}</div>
    </div>
  );
}

function InfoRow({ label, value, danger }: { label: string; value: string; danger?: boolean }) {
  return (
    <div className="flex justify-between text-xs text-muted-foreground">
      <span>{label}</span>
      <span className={`font-bold ${danger ? 'text-danger' : 'text-foreground'}`}>{value}</span>
    </div>
  );
}

function BarStat({ label, value, percent, barClass, valueClass }: {
  label: string; value: string; percent: number; barClass: string; valueClass?: string;
}) {
  return (
    <div>
      <div className="flex justify-between text-[11px] mb-1 text-muted-foreground">
        <span>{label}</span><span className={`font-bold ${valueClass || 'text-foreground'}`}>{value}</span>
      </div>
      <div className="h-2.5 bg-secondary rounded-full overflow-hidden border border-border/40">
        <div className={`h-full rounded-full transition-all duration-500 ${barClass}`} style={{ width: `${Math.min(100, percent)}%` }} />
      </div>
    </div>
  );
}

function EquipBadge({ active, label }: { active: boolean; label: string }) {
  return (
    <span className={`px-2 py-0.5 rounded-full border font-medium ${active ? 'bg-accent/15 border-accent/40 text-accent-foreground' : 'bg-secondary border-border text-muted-foreground'}`}>
      {active ? '✅' : '❌'} {label}
    </span>
  );
}

function GameBtn({ onClick, disabled, icon, label, desc, small, primary }: {
  onClick: () => void; disabled: boolean; icon: string; label: string; desc: string; small?: boolean; primary?: boolean;
}) {
  return (
    <button onClick={onClick} disabled={disabled}
      className={`w-full flex items-center gap-2.5 ${small ? 'p-2' : 'p-2.5'} rounded-xl border-2 transition-all text-left
        ${primary
          ? 'honey-gradient border-primary/30 text-primary-foreground game-btn hover:brightness-105'
          : 'border-border/60 bg-card hover:bg-secondary/80 active:translate-y-0.5'}
        disabled:opacity-35 disabled:cursor-not-allowed disabled:active:translate-y-0`}>
      <span className={`${small ? 'text-base' : 'text-xl'}`}>{icon}</span>
      <div className="flex-1 min-w-0">
        <div className={`font-bold ${primary ? '' : 'text-foreground'} ${small ? 'text-[11px]' : 'text-xs'}`}>{label}</div>
        <div className={`${primary ? 'text-primary-foreground/70' : 'text-muted-foreground'} ${small ? 'text-[9px]' : 'text-[10px]'}`}>{desc}</div>
      </div>
    </button>
  );
}
