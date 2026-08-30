import { Layers } from 'lucide-react';
import { motion } from 'framer-motion';
import { getEraLabel } from '@/lib/stackexchange';

interface StratumDividerProps {
  year: number;
  count: number;
  index: number;
}

const colorMap: Record<number, string> = {
  2012: 'border-stratum-surface bg-stratum-surface/10',
  2011: 'border-stratum-shallow bg-stratum-shallow/10',
  2010: 'border-stratum-mid bg-stratum-mid/10',
  2009: 'border-stratum-deep bg-stratum-deep/10',
  2008: 'border-stratum-ancient bg-stratum-ancient/10',
};

const dotColor: Record<number, string> = {
  2012: 'bg-stratum-surface',
  2011: 'bg-stratum-shallow',
  2010: 'bg-stratum-mid',
  2009: 'bg-stratum-deep',
  2008: 'bg-stratum-ancient',
};

const StratumDivider = ({ year, count, index }: StratumDividerProps) => {
  const era = getEraLabel(Math.floor(new Date(year, 6, 1).getTime() / 1000));
  const depth = Math.min(100, Math.max(0, ((2012 - year) / 4) * 100));
  const colors = colorMap[year] || colorMap[2012];
  const dot = dotColor[year] || dotColor[2012];

  return (
    <motion.div
      initial={{ opacity: 0, scaleX: 0 }}
      animate={{ opacity: 1, scaleX: 1 }}
      transition={{ delay: index * 0.15, duration: 0.5 }}
      className={`relative border-t-2 ${colors} rounded-lg px-4 py-3 mb-4`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${dot}`} />
          <Layers className="w-4 h-4 text-muted-foreground" />
          <span className="font-display text-lg font-bold text-foreground">
            {year}년 지층
          </span>
          <span className="text-xs text-muted-foreground font-mono-code ml-2">
            — {era}
          </span>
        </div>
        <div className="flex items-center gap-3 text-xs font-mono-code text-muted-foreground">
          <span>{count}개 유물</span>
          <span className="text-amber">깊이 {depth.toFixed(0)}m</span>
        </div>
      </div>

      {/* Decorative soil line */}
      <svg className="absolute bottom-0 left-0 w-full h-1 overflow-visible" preserveAspectRatio="none">
        <line x1="0" y1="0" x2="100%" y2="0" stroke="currentColor" strokeWidth="1" 
              strokeDasharray="4 3" className="text-border" />
      </svg>
    </motion.div>
  );
};

export default StratumDivider;
