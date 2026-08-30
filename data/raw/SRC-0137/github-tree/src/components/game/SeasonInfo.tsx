import { SEASON_NAMES, type Season } from '@/game/types';
import { useGame } from '@/game/GameContext';

const seasonTips: Record<Season, string[]> = {
  spring: [
    '🌸 아카시아 유밀기가 다가옵니다! 봉군을 키우세요.',
    '📋 소초를 투입하여 공간을 확보하세요.',
    '⚠️ 분봉에 주의하세요 — 벌이 많아지면 왕대를 확인!',
    '💊 바로아 1차 방제 시기입니다.',
  ],
  summer: [
    '🍯 밤꿀 채밀 시기입니다.',
    '🦠 7~8월 바로아 집중 방제 — 연중 가장 중요!',
    '🐝 말벌 출현에 대비하세요.',
    '🌧️ 장마철 환기 관리에 유의하세요.',
  ],
  fall: [
    '🍂 월동 준비를 서두르세요!',
    '🍯 가을 잡화꿀 채밀 마지막 기회.',
    '📊 저밀량을 확인하고 부족하면 급이하세요.',
    '💊 바로아 3차 방제를 잊지 마세요.',
  ],
  winter: [
    '❄️ 벌들이 월동 중입니다.',
    '🔬 연구실에서 새 기술을 연구하세요!',
    '🔨 상점에서 장비를 크래프팅하세요.',
    '🍯 벌들이 저밀을 소비 중 — 충분한지 확인!',
  ],
};

export default function SeasonInfo() {
  const { state } = useGame();
  if (!state) return null;
  const tips = seasonTips[state.season];

  return (
    <div className="game-panel p-3">
      <h3 className="font-serif font-bold text-foreground text-sm mb-1.5">
        📅 {SEASON_NAMES[state.season]} 양봉 가이드
      </h3>
      <ul className="space-y-1">
        {tips.map((tip, i) => (
          <li key={i} className="text-[11px] text-muted-foreground leading-relaxed">{tip}</li>
        ))}
      </ul>
    </div>
  );
}
