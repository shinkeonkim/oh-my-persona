import { useGame } from '@/game/GameContext';
import BottomNav from '@/components/game/BottomNav';
import ResourceBar from '@/components/game/ResourceBar';
import { ArrowLeft, Lock, Check } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { RESEARCH_TREE, type ResearchNode } from '@/game/types';
import { motion } from 'framer-motion';

const categoryNames: Record<string, string> = {
  pest: '🦠 병해충 관리', queen: '👑 여왕 육성', harvest: '🍯 채밀 기술', management: '🔧 양봉장 관리',
};

export default function ResearchPage() {
  const { state, doResearch } = useGame();
  const navigate = useNavigate();
  if (!state) return null;

  const categories = ['pest', 'queen', 'harvest', 'management'];

  const isUnlocked = (node: ResearchNode) => {
    if (state.research[node.id]) return true;
    return node.prereqs.every(p => state.research[p]);
  };

  const canAfford = (node: ResearchNode) => {
    if (state.gold < node.cost.gold) return false;
    if ((node.cost.wax || 0) > state.wax) return false;
    if ((node.cost.royalJelly || 0) > state.royalJelly) return false;
    return true;
  };

  return (
    <div className="min-h-screen bg-background flex flex-col pb-16">
      <header className="flex items-center gap-2 px-4 pt-4 pb-2">
        <button onClick={() => navigate('/')} className="p-1.5 rounded-lg hover:bg-secondary"><ArrowLeft className="w-5 h-5 text-muted-foreground" /></button>
        <h1 className="font-serif text-xl font-bold text-foreground">🔬 연구실</h1>
      </header>

      <div className="px-3 mb-3"><ResourceBar /></div>

      {state.season === 'winter' && (
        <div className="px-3 mb-2">
          <div className="game-panel p-2.5 border-season-winter/30 bg-season-winter/5 text-xs text-foreground font-medium">
            ❄️ 겨울은 연구에 집중하기 좋은 시기입니다!
          </div>
        </div>
      )}

      <main className="flex-1 px-3 pb-4 overflow-y-auto space-y-5">
        {categories.map(cat => (
          <div key={cat}>
            <h3 className="game-section-title">{categoryNames[cat]}</h3>
            <div className="space-y-2">
              {RESEARCH_TREE.filter(n => n.category === cat).map((node, i) => {
                const done = !!state.research[node.id];
                const unlocked = isUnlocked(node);
                const affordable = canAfford(node);

                return (
                  <motion.div
                    key={node.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className={`game-panel p-3 transition-all ${done ? 'border-accent/40 bg-accent/5' : !unlocked ? 'opacity-35 grayscale' : ''}`}
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-2xl drop-shadow-sm">{node.icon}</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <h4 className="font-bold text-sm text-foreground">{node.name}</h4>
                          {done && <span className="bg-accent/20 text-accent rounded-full p-0.5"><Check className="w-3 h-3" /></span>}
                          {!unlocked && <Lock className="w-3.5 h-3.5 text-muted-foreground" />}
                        </div>
                        <p className="text-[11px] text-muted-foreground mt-0.5">{node.description}</p>
                        {!done && (
                          <div className="flex items-center gap-2 mt-1.5 text-[10px] font-bold text-muted-foreground">
                            <span className="bg-secondary rounded px-1 py-0.5">{node.cost.gold}💰</span>
                            {node.cost.wax && <span className="bg-secondary rounded px-1 py-0.5">{node.cost.wax}🕯️</span>}
                            {node.cost.royalJelly && <span className="bg-secondary rounded px-1 py-0.5">{node.cost.royalJelly}👑</span>}
                          </div>
                        )}
                      </div>
                      {!done && unlocked && (
                        <button
                          onClick={() => doResearch(node.id)}
                          disabled={!affordable}
                          className="honey-gradient game-btn px-3 py-1.5 text-primary-foreground text-xs disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
                        >
                          연구
                        </button>
                      )}
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        ))}
      </main>

      <BottomNav />
    </div>
  );
}
