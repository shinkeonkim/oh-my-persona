import { useGame } from '@/game/GameContext';
import BottomNav from '@/components/game/BottomNav';
import { ArrowLeft, Save, Trash2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { type GameSpeed } from '@/game/types';

export default function SettingsPage() {
  const { state, doSave, doReset, doSetSpeed } = useGame();
  const navigate = useNavigate();
  if (!state) return null;

  return (
    <div className="min-h-screen bg-background flex flex-col pb-16">
      <header className="flex items-center gap-2 px-4 pt-4 pb-2">
        <button onClick={() => navigate('/')} className="p-1.5 rounded-lg hover:bg-secondary"><ArrowLeft className="w-5 h-5 text-muted-foreground" /></button>
        <h1 className="font-serif text-xl font-bold text-foreground">⚙️ 설정</h1>
      </header>

      <main className="flex-1 px-3 pb-4 overflow-y-auto space-y-5">
        {/* Speed */}
        <div className="game-panel p-4">
          <h3 className="game-section-title">⏱️ 게임 속도</h3>
          <div className="grid grid-cols-3 gap-2">
            {(['fast', 'normal', 'slow'] as GameSpeed[]).map(speed => (
              <button key={speed} onClick={() => doSetSpeed(speed)}
                className={`py-2.5 px-3 rounded-xl text-sm font-bold border-2 transition-all ${
                  state.gameSpeed === speed
                    ? 'honey-gradient text-primary-foreground border-honey-dark game-btn'
                    : 'border-border text-muted-foreground hover:bg-secondary'
                }`}>
                {speed === 'fast' ? '⚡빠름' : speed === 'normal' ? '▶️보통' : '🐌느림'}
              </button>
            ))}
          </div>
          <p className="text-xs text-muted-foreground mt-2 font-medium">
            계절당 {state.gameSpeed === 'fast' ? 3 : state.gameSpeed === 'normal' ? 7 : 14}일
          </p>
        </div>

        {/* Stats */}
        <div className="game-panel p-4">
          <h3 className="game-section-title">📊 통계</h3>
          <div className="space-y-2 text-sm">
            <Row label="총 수확 꿀" value={`${state.totalHoneyHarvested.toFixed(1)}kg`} />
            <Row label="총 수입" value={`${state.totalGoldEarned.toLocaleString()}💰`} />
            <Row label="완주 연도" value={`${state.yearsCompleted}년`} />
            <Row label="양봉가 레벨" value={`⭐ Lv.${state.level}`} />
            <Row label="해금 연구" value={`🔬 ${Object.keys(state.research).length}개`} />
          </div>
        </div>

        {/* Actions */}
        <div className="space-y-2.5">
          <button onClick={doSave}
            className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-accent text-accent-foreground font-bold text-sm game-btn">
            <Save className="w-4 h-4" /> 수동 저장
          </button>
          <button onClick={() => { if (confirm('정말 게임을 초기화하시겠습니까?')) { doReset(); navigate('/'); } }}
            className="w-full flex items-center justify-center gap-2 py-3 rounded-xl border-2 border-destructive text-destructive font-bold text-sm hover:bg-destructive/10 transition-colors">
            <Trash2 className="w-4 h-4" /> 게임 초기화
          </button>
        </div>
      </main>

      <BottomNav />
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-center py-0.5">
      <span className="text-muted-foreground">{label}</span>
      <span className="text-foreground font-bold">{value}</span>
    </div>
  );
}
