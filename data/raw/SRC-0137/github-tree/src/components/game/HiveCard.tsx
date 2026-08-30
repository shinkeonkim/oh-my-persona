import { type Hive, getVarroaStatus, type QueenStatus } from '@/game/types';
import { getHiveStatus } from '@/game/engine';
import { motion } from 'framer-motion';

interface HiveCardProps {
  hive: Hive;
  onClick: () => void;
  hasEvent?: boolean;
}

const statusColors = {
  green: 'bg-safe', yellow: 'bg-warning', orange: 'bg-honey-dark', red: 'bg-danger',
};

const statusLabels = {
  green: '양호', yellow: '주의', orange: '경고', red: '위험',
};

const queenIcons: Record<QueenStatus, string> = {
  healthy: '👑', aging: '⏳', absent: '❓', replacing: '🔄', laying_worker: '🥚',
};

export default function HiveCard({ hive, onClick, hasEvent }: HiveCardProps) {
  const status = getHiveStatus(hive);
  const isDead = hive.beeCount === 0;
  const honeyPercent = (hive.honeyStored / hive.honeyCapacity) * 100;
  const varroaStatus = getVarroaStatus(hive.varroaLevel);
  const beePercent = Math.min(100, (hive.beeCount / 60000) * 100);

  return (
    <motion.button
      whileHover={{ scale: 1.03, y: -2 }}
      whileTap={{ scale: 0.97 }}
      onClick={onClick}
      className={`game-panel p-3 w-full text-left transition-all relative overflow-hidden ${isDead ? 'opacity-50 grayscale' : ''}`}
    >
      {/* Status indicator strip */}
      <div className={`absolute top-0 left-0 right-0 h-1 ${statusColors[status]} ${status === 'red' ? 'animate-pulse' : ''}`} />

      {hasEvent && (
        <span className="absolute -top-1 -right-1 w-6 h-6 bg-danger rounded-full flex items-center justify-center text-[11px] animate-pulse z-10 ring-2 ring-card font-bold">❗</span>
      )}

      {/* Header */}
      <div className="flex items-center justify-between mb-2 mt-0.5">
        <h3 className="font-serif font-bold text-foreground text-sm truncate">{hive.name}</h3>
        <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded-md ${
          status === 'green' ? 'bg-safe/15 text-safe' :
          status === 'yellow' ? 'bg-warning/15 text-warning' :
          status === 'orange' ? 'bg-honey-dark/15 text-honey-dark' :
          'bg-danger/15 text-danger'
        }`}>{statusLabels[status]}</span>
      </div>

      {/* Hive icon */}
      <div className="text-center text-3xl mb-2 relative h-12 flex items-center justify-center">
        {isDead ? <span className="opacity-30 text-4xl">🏚️</span> : (
          <>
            <span className="drop-shadow-md text-4xl">🏠</span>
            <span className="absolute animate-bee text-sm" style={{ left: '20%', top: 0 }}>🐝</span>
            {hive.beeCount > 20000 && <span className="absolute animate-bee text-xs" style={{ left: '65%', top: 4, animationDelay: '1.2s' }}>🐝</span>}
            {hive.beeCount > 40000 && <span className="absolute animate-bee text-[10px]" style={{ left: '45%', top: 2, animationDelay: '2.5s' }}>🐝</span>}
          </>
        )}
      </div>

      {/* Stats */}
      <div className="space-y-1.5 text-[11px]">
        {/* Bee count bar */}
        <div>
          <div className="flex justify-between text-muted-foreground mb-0.5">
            <span>🐝 봉군</span><span className="text-foreground font-bold">{(hive.beeCount / 1000).toFixed(1)}k</span>
          </div>
          <div className="h-1.5 bg-secondary rounded-full overflow-hidden">
            <div className="h-full bg-accent/60 rounded-full transition-all duration-500" style={{ width: `${beePercent}%` }} />
          </div>
        </div>

        {/* Honey bar */}
        <div>
          <div className="flex justify-between text-muted-foreground mb-0.5">
            <span>🍯 꿀</span><span className="text-foreground font-bold">{hive.honeyStored.toFixed(1)}kg</span>
          </div>
          <div className="h-1.5 bg-secondary rounded-full overflow-hidden">
            <div className="h-full honey-gradient rounded-full transition-all duration-500" style={{ width: `${honeyPercent}%` }} />
          </div>
        </div>

        {/* Varroa + Queen row */}
        <div className="flex justify-between pt-0.5">
          <span className="flex items-center gap-0.5">
            🦠
            <span className={`font-bold ${varroaStatus === 'safe' ? 'text-safe' : varroaStatus === 'caution' ? 'text-warning' : 'text-danger'}`}>
              {Math.round(hive.varroaLevel)}%
            </span>
          </span>
          <span className="flex items-center gap-0.5">
            {queenIcons[hive.queenStatus]}
            <span className={`font-bold ${hive.queenStatus === 'healthy' ? 'text-safe' : hive.queenStatus === 'laying_worker' || hive.queenStatus === 'absent' ? 'text-danger' : 'text-warning'}`}>
              {hive.queenStatus === 'healthy' ? '건강' : hive.queenStatus === 'aging' ? '노화' : hive.queenStatus === 'absent' ? '부재' : hive.queenStatus === 'replacing' ? '교체중' : '동봉산란'}
            </span>
          </span>
        </div>

        {/* Equipment badges */}
        {(hive.hasHornetTrap || hive.hasHornetNet || hive.hasSuper || hive.queenMarked) && (
          <div className="flex flex-wrap gap-1 pt-0.5">
            {hive.hasHornetTrap && <Badge>🪤</Badge>}
            {hive.hasHornetNet && <Badge>🥅</Badge>}
            {hive.hasSuper && <Badge>📦</Badge>}
            {hive.queenMarked && <Badge>🏷️</Badge>}
          </div>
        )}
      </div>
    </motion.button>
  );
}

function Badge({ children }: { children: React.ReactNode }) {
  return (
    <span className="bg-secondary/80 rounded px-1 py-0.5 text-[9px]">{children}</span>
  );
}
