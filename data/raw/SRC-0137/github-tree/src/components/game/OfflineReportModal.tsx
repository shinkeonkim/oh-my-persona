import { type OfflineReport } from '@/game/types';
import { motion } from 'framer-motion';

interface OfflineReportModalProps {
  report: OfflineReport;
  onDismiss: () => void;
}

export default function OfflineReportModal({ report, onDismiss }: OfflineReportModalProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-foreground/40 p-4"
      onClick={onDismiss}
    >
      <motion.div
        initial={{ scale: 0.85, y: 30 }}
        animate={{ scale: 1, y: 0 }}
        onClick={(e) => e.stopPropagation()}
        className="game-panel w-full max-w-sm p-6 text-center"
      >
        <div className="text-4xl mb-3">🐝</div>
        <h2 className="font-serif text-lg font-bold text-foreground mb-1">어서 오세요!</h2>
        <p className="text-sm text-muted-foreground mb-4">{report.duration} 동안 부재하셨습니다</p>

        <div className="space-y-3 text-left text-sm mb-5">
          {report.honeyProduced > 0 && (
            <div className="bg-secondary/60 rounded-lg p-3">
              <span className="text-foreground">🍯 벌들이 <strong>{report.honeyProduced.toFixed(1)}kg</strong>의 꿀을 모았습니다!</span>
            </div>
          )}

          {report.varroaChanges.map(v => (
            <div key={v.hiveId} className="bg-secondary/60 rounded-lg p-3">
              <span className={v.newLevel > 40 ? 'text-danger' : 'text-foreground'}>
                🦠 {v.hiveName}: 바로아 {v.oldLevel}% → {v.newLevel}%
              </span>
            </div>
          ))}

          {report.beeChanges.map(b => (
            <div key={b.hiveId} className="bg-secondary/60 rounded-lg p-3">
              <span className={b.change < 0 ? 'text-danger' : 'text-safe'}>
                🐝 {b.hiveName}: 봉군 {b.change > 0 ? '+' : ''}{b.change}
              </span>
            </div>
          ))}

          {report.seasonChanges.length > 0 && (
            <div className="bg-secondary/60 rounded-lg p-3">
              <span className="text-foreground">📅 계절이 바뀌었습니다</span>
            </div>
          )}

          {report.alerts.map((alert, i) => (
            <div key={i} className="bg-destructive/10 border border-destructive/20 rounded-lg p-3">
              <span className="text-destructive text-sm">{alert}</span>
            </div>
          ))}
        </div>

        <button
          onClick={onDismiss}
          className="w-full py-3 rounded-lg honey-gradient text-primary-foreground font-bold text-sm hover:opacity-90 transition-opacity"
        >
          양봉장으로 가기 🌻
        </button>
      </motion.div>
    </motion.div>
  );
}
