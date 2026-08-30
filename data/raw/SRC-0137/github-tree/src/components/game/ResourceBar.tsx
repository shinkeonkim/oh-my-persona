import { useGame } from '@/game/GameContext';
import { SEASON_NAMES, SEASON_EMOJIS, DAYS_PER_SEASON, HONEY_NAMES, HONEY_ICONS, type HoneyType, REGIONS } from '@/game/types';

export default function ResourceBar() {
  const { state } = useGame();
  if (!state) return null;
  const daysInSeason = DAYS_PER_SEASON[state.gameSpeed];

  const honeyTypes: HoneyType[] = ['acacia', 'chestnut', 'wildflower', 'mixed'];
  const hasHoney = honeyTypes.some(t => (state.honeyByType[t] || 0) >= 0.1);
  const regionInfo = REGIONS.find(r => r.id === state.region);
  const seasonProgress = (state.dayInSeason / daysInSeason) * 100;

  return (
    <div className="game-panel px-3 py-2.5 space-y-2">
      {/* Top row: resources + season */}
      <div className="flex flex-wrap items-center gap-2.5 text-sm font-bold">
        <ResourceChip icon="💰" value={state.gold.toLocaleString()} color="text-primary" />
        <ResourceChip icon="🍯" value={`${state.honey.toFixed(1)}kg`} />
        <ResourceChip icon="🕯️" value={String(state.wax)} />
        {state.royalJelly > 0 && <ResourceChip icon="👑" value={String(state.royalJelly)} />}
        <div className="ml-auto flex items-center gap-1.5 bg-secondary/80 rounded-lg px-2 py-1">
          <span className="animate-season-pulse text-sm">{SEASON_EMOJIS[state.season]}</span>
          <span className="font-serif font-bold text-foreground text-xs">
            {state.year}년 {SEASON_NAMES[state.season]}
          </span>
        </div>
      </div>

      {/* Season progress bar */}
      <div className="xp-bar">
        <div className="xp-bar-fill" style={{ width: `${seasonProgress}%` }} />
      </div>

      {/* Bottom row: honey types + level */}
      <div className="flex flex-wrap items-center gap-2 text-[10px] text-muted-foreground">
        {hasHoney && honeyTypes.map(t => {
          const amt = state.honeyByType[t] || 0;
          if (amt < 0.1) return null;
          return (
            <span key={t} className="flex items-center gap-0.5 bg-secondary/50 rounded px-1 py-0.5">
              {HONEY_ICONS[t]}{amt.toFixed(1)}
            </span>
          );
        })}
        <span className="ml-auto flex items-center gap-1.5 font-bold">
          <span className="bg-primary/15 text-primary rounded px-1.5 py-0.5">⭐Lv.{state.level}</span>
          {state.fame > 0 && <span className="bg-honey/10 text-honey-dark rounded px-1.5 py-0.5">명성 {state.fame}</span>}
          {regionInfo && regionInfo.id !== 'default' && <span>{regionInfo.icon}{regionInfo.name}</span>}
        </span>
      </div>
    </div>
  );
}

function ResourceChip({ icon, value, color }: { icon: string; value: string; color?: string }) {
  return (
    <div className="flex items-center gap-1 bg-secondary/60 rounded-lg px-2 py-0.5">
      <span className="text-xs">{icon}</span>
      <span className={`text-foreground text-xs ${color || ''}`}>{value}</span>
    </div>
  );
}
