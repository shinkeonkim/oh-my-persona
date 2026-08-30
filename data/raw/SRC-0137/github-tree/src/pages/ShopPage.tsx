import { useState } from 'react';
import { useGame } from '@/game/GameContext';
import BottomNav from '@/components/game/BottomNav';
import ResourceBar from '@/components/game/ResourceBar';
import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { HONEY_NAMES, HONEY_ICONS, HONEY_PRICES, type HoneyType } from '@/game/types';

export default function ShopPage() {
  const { state, doSell, doSellByType, doBuyHive, doExpandSlots, doUpgradeExtractor, doCraft } = useGame();
  const navigate = useNavigate();
  const [sellTab, setSellTab] = useState<'bulk' | 'type'>('type');
  if (!state) return null;

  const hiveCost = 300;
  const slotCost = state.maxHiveSlots * 200;
  const extractorCost = state.extractorLevel * 200;
  const premium = state.research['honey_grading'] ? 1.15 : 1;

  const canCraft = (id: string) => {
    if (id === 'candle') return state.research['wax_processing'] && state.wax >= 3;
    if (id === 'foundation') return state.research['wax_processing'] && state.wax >= 2;
    if (id === 'propolis_tincture') return state.research['wax_processing'] && state.honey >= 3 && state.wax >= 1;
    if (id === 'hornet_trap') return state.research['hornet_defense'] && state.gold >= 80;
    if (id === 'hornet_net') return state.research['hornet_defense'] && state.gold >= 200;
    if (id === 'queen_cage') return state.research['queen_rearing'] && state.gold >= 150 && state.wax >= 1;
    return false;
  };

  const honeyTypes: HoneyType[] = ['acacia', 'chestnut', 'wildflower', 'mixed'];

  return (
    <div className="min-h-screen bg-background flex flex-col pb-16">
      <header className="flex items-center gap-2 px-4 pt-4 pb-2">
        <button onClick={() => navigate('/')} className="p-1.5 rounded-lg hover:bg-secondary"><ArrowLeft className="w-5 h-5 text-muted-foreground" /></button>
        <h1 className="font-serif text-xl font-bold text-foreground">🏪 양봉 상점</h1>
      </header>

      <div className="px-3 mb-3"><ResourceBar /></div>

      <main className="flex-1 px-3 pb-4 overflow-y-auto space-y-5">
        {/* Sell honey */}
        <div>
          <h3 className="game-section-title">🍯 꿀 판매</h3>
          <div className="flex gap-1 mb-2.5">
            <button onClick={() => setSellTab('type')}
              className={`flex-1 py-1.5 rounded-lg text-xs font-bold transition-all ${sellTab === 'type' ? 'honey-gradient text-primary-foreground game-btn' : 'bg-secondary text-muted-foreground'}`}>
              종류별 판매
            </button>
            <button onClick={() => setSellTab('bulk')}
              className={`flex-1 py-1.5 rounded-lg text-xs font-bold transition-all ${sellTab === 'bulk' ? 'honey-gradient text-primary-foreground game-btn' : 'bg-secondary text-muted-foreground'}`}>
              일괄 판매
            </button>
          </div>

          {sellTab === 'type' ? (
            <div className="space-y-2">
              {honeyTypes.map(type => {
                const amount = state.honeyByType[type] || 0;
                const price = Math.floor(HONEY_PRICES[type] * premium);
                if (amount < 0.1) return null;
                return (
                  <div key={type} className="game-panel p-3">
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-xs font-bold text-foreground">{HONEY_ICONS[type]} {HONEY_NAMES[type]}</span>
                      <span className="text-xs text-muted-foreground font-medium">{amount.toFixed(1)}kg</span>
                    </div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] text-primary font-bold bg-primary/10 rounded px-1.5 py-0.5">{price}골드/kg</span>
                    </div>
                    <div className="grid grid-cols-3 gap-1.5">
                      {[1, Math.floor(amount / 2), Math.floor(amount)].map((amt, i) => (
                        <button key={i} onClick={() => doSellByType(type, amt)} disabled={amount < amt || amt === 0}
                          className="py-2 rounded-lg border-2 border-border text-[10px] font-bold hover:border-primary hover:bg-primary/5 disabled:opacity-40 disabled:cursor-not-allowed transition-all text-foreground">
                          {i === 2 ? '전부' : `${amt}kg`}
                          <div className="text-[9px] text-primary">{(amt * price).toLocaleString()}💰</div>
                        </button>
                      ))}
                    </div>
                  </div>
                );
              })}
              {Object.values(state.honeyByType).every(v => v < 0.1) && (
                <p className="text-center text-xs text-muted-foreground py-6 font-medium">🍯 판매할 꿀이 없습니다</p>
              )}
            </div>
          ) : (
            <>
              <div className="game-panel p-3 mb-2 text-sm">
                <div className="flex justify-between"><span className="text-muted-foreground">보유</span><span className="font-bold text-foreground">{state.honey.toFixed(1)}kg</span></div>
              </div>
              <div className="grid grid-cols-3 gap-2">
                {[1, 5, Math.floor(state.honey)].map(amt => (
                  <button key={amt} onClick={() => doSell(amt)} disabled={state.honey < amt || amt === 0}
                    className="p-2.5 rounded-lg border-2 border-border text-sm font-bold hover:border-primary hover:bg-primary/5 disabled:opacity-40 disabled:cursor-not-allowed transition-all text-foreground">
                    {amt === Math.floor(state.honey) ? '전부' : `${amt}kg`}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>

        {/* Buy */}
        <div>
          <h3 className="game-section-title">🛒 구매 / 업그레이드</h3>
          <div className="space-y-1.5">
            <ShopItem icon="🏠" name="새 벌통" desc={`${state.hives.length}/${state.maxHiveSlots}`} cost={hiveCost}
              canBuy={state.gold >= hiveCost && state.hives.length < state.maxHiveSlots} onBuy={doBuyHive} />
            <ShopItem icon="📐" name="슬롯 확장" desc={`→ ${state.maxHiveSlots + 1}통`} cost={slotCost}
              canBuy={state.gold >= slotCost} onBuy={doExpandSlots} />
            <ShopItem icon="⚙️" name="채밀기 Lv.↑" desc={`Lv.${state.extractorLevel}→${state.extractorLevel + 1}`} cost={extractorCost}
              canBuy={state.gold >= extractorCost && state.extractorLevel < 5} onBuy={doUpgradeExtractor} />
          </div>
        </div>

        {/* Crafting */}
        <div>
          <h3 className="game-section-title">🔨 가공 / 크래프팅</h3>
          <div className="space-y-1.5">
            {[
              { id: 'candle', icon: '🕯️', name: '밀랍 양초', desc: '밀랍 3 → 150골드', unlocked: !!state.research['wax_processing'] },
              { id: 'foundation', icon: '📋', name: '소초 제작', desc: '밀랍 2 → 소초 1', unlocked: !!state.research['wax_processing'] },
              { id: 'propolis_tincture', icon: '💧', name: '프로폴리스 팅크', desc: '꿀3 + 밀랍1 → 200골드', unlocked: !!state.research['wax_processing'] },
              { id: 'hornet_trap', icon: '🪤', name: '말벌 트랩', desc: '80골드', unlocked: !!state.research['hornet_defense'] },
              { id: 'hornet_net', icon: '🥅', name: '말벌 그물', desc: '200골드', unlocked: !!state.research['hornet_defense'] },
              { id: 'queen_cage', icon: '🏰', name: '왕롱', desc: '150골드 + 밀랍1', unlocked: !!state.research['queen_rearing'] },
            ].map(item => (
              item.unlocked ? (
                <button key={item.id} onClick={() => doCraft(item.id)} disabled={!canCraft(item.id)}
                  className="w-full game-panel flex items-center gap-3 p-3 hover:border-primary/30 disabled:opacity-40 disabled:cursor-not-allowed transition-all text-left">
                  <span className="text-xl drop-shadow-sm">{item.icon}</span>
                  <div className="flex-1">
                    <div className="font-bold text-xs text-foreground">{item.name}</div>
                    <div className="text-[10px] text-muted-foreground">{item.desc}</div>
                  </div>
                  {(state.craftedItems[item.id] || 0) > 0 && (
                    <span className="text-[10px] bg-primary/15 text-primary font-bold rounded-full px-2 py-0.5">×{state.craftedItems[item.id]}</span>
                  )}
                </button>
              ) : (
                <div key={item.id} className="game-panel flex items-center gap-3 p-3 opacity-30 grayscale">
                  <span className="text-xl">🔒</span>
                  <div className="flex-1"><div className="font-bold text-xs text-muted-foreground">{item.name}</div><div className="text-[10px] text-muted-foreground">연구 필요</div></div>
                </div>
              )
            ))}
          </div>
        </div>
      </main>

      <BottomNav />
    </div>
  );
}

function ShopItem({ icon, name, desc, cost, canBuy, onBuy }: { icon: string; name: string; desc: string; cost: number; canBuy: boolean; onBuy: () => void }) {
  return (
    <button onClick={onBuy} disabled={!canBuy}
      className="w-full game-panel flex items-center gap-3 p-3 hover:border-primary/30 disabled:opacity-40 disabled:cursor-not-allowed transition-all text-left">
      <span className="text-xl drop-shadow-sm">{icon}</span>
      <div className="flex-1"><div className="font-bold text-xs text-foreground">{name}</div><div className="text-[10px] text-muted-foreground">{desc}</div></div>
      <div className="text-xs font-bold text-primary bg-primary/10 rounded-lg px-2 py-1">{cost}💰</div>
    </button>
  );
}
