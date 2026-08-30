import { type InspectionCard } from '@/game/types';
import { useGame } from '@/game/GameContext';
import { motion } from 'framer-motion';
import { X } from 'lucide-react';

interface Props {
  hiveId: string;
  cards: InspectionCard[];
  onClose: () => void;
}

const effectStyles = {
  positive: 'border-safe/40 bg-safe/8',
  negative: 'border-danger/40 bg-danger/8',
  neutral: 'border-border/60 bg-secondary/40',
  choice: 'border-warning/40 bg-warning/8',
};

export default function InspectionModal({ hiveId, cards, onClose }: Props) {
  const { doApplyCard } = useGame();

  const handleAction = (card: InspectionCard, actionId?: string) => {
    doApplyCard(hiveId, card.type, actionId);
  };

  return (
    <motion.div
      initial={{ opacity: 0 }} animate={{ opacity: 1 }}
      className="fixed inset-0 z-[60] flex items-center justify-center bg-foreground/40 backdrop-blur-sm p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, y: 20 }} animate={{ scale: 1, y: 0 }}
        transition={{ type: 'spring', damping: 25, stiffness: 350 }}
        onClick={e => e.stopPropagation()}
        className="game-panel w-full max-w-sm max-h-[80vh] overflow-y-auto p-0"
      >
        {/* Header */}
        <div className="px-5 pt-4 pb-3 border-b-2 border-border/60 flex items-center justify-between">
          <h2 className="font-serif text-lg font-bold text-foreground flex items-center gap-2">
            <span className="text-xl">🔍</span> 벌통 점검 결과
          </h2>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-secondary transition-colors border border-border/60">
            <X className="w-4 h-4 text-muted-foreground" />
          </button>
        </div>

        {/* Cards */}
        <div className="p-4 space-y-2.5">
          {cards.map((card, i) => (
            <motion.div
              key={`${card.type}-${i}`}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.12 }}
              className={`border-2 rounded-xl p-3.5 ${effectStyles[card.effect]}`}
            >
              <div className="flex items-start gap-2.5">
                <span className="text-2xl">{card.icon}</span>
                <div className="flex-1">
                  <h3 className="font-bold text-sm text-foreground">{card.title}</h3>
                  <p className="text-[11px] text-muted-foreground mt-0.5 leading-relaxed">{card.description}</p>
                  {card.actions ? (
                    <div className="flex gap-2 mt-2.5">
                      {card.actions.map(action => (
                        <button key={action.actionId}
                          onClick={() => handleAction(card, action.actionId)}
                          className="game-btn px-3 py-1.5 text-[11px] honey-gradient text-primary-foreground"
                        >
                          {action.label}
                        </button>
                      ))}
                    </div>
                  ) : (
                    <button
                      onClick={() => handleAction(card)}
                      className="mt-2 px-3 py-1 text-[10px] font-bold rounded-lg bg-secondary border border-border/60 text-secondary-foreground hover:bg-secondary/80 transition-colors"
                    >
                      확인
                    </button>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Footer */}
        <div className="px-4 pb-4">
          <button onClick={onClose}
            className="game-btn w-full py-3 honey-gradient text-primary-foreground text-sm">
            ✅ 점검 완료
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}
