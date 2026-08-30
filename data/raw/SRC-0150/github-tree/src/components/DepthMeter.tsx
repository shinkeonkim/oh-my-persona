import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';

interface DepthMeterProps {
  sectionRefs: React.RefObject<(HTMLDivElement | null)[]>;
  years: number[];
}

const layers = [
  { label: '표층 (2012)', depth: 0,  color: 'bg-stratum-surface',  year: 2012 },
  { label: '상층 (2011)', depth: 20, color: 'bg-stratum-shallow', year: 2011 },
  { label: '중층 (2010)', depth: 40, color: 'bg-stratum-mid',     year: 2010 },
  { label: '하층 (2009)', depth: 60, color: 'bg-stratum-deep',    year: 2009 },
  { label: '심층 (2008)', depth: 80, color: 'bg-stratum-ancient', year: 2008 },
];

const DepthMeter = ({ sectionRefs, years }: DepthMeterProps) => {
  const [scrollDepth, setScrollDepth] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      const refs = sectionRefs.current;
      if (!refs || refs.length === 0) return;

      const viewportCenter = window.innerHeight / 2;
      let closestIdx = 0;
      let closestDist = Infinity;

      refs.forEach((ref, i) => {
        if (!ref) return;
        const rect = ref.getBoundingClientRect();
        const center = rect.top + rect.height / 2;
        const dist = Math.abs(center - viewportCenter);
        if (dist < closestDist) {
          closestDist = dist;
          closestIdx = i;
        }
      });

      // Map year to depth percentage
      const year = years[closestIdx];
      if (year !== undefined) {
        const depth = Math.min(100, Math.max(0, ((2012 - year) / 4) * 100));
        setScrollDepth(depth);
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener('scroll', handleScroll);
  }, [sectionRefs, years]);

  return (
    <div className="fixed right-6 top-1/2 -translate-y-1/2 z-40 hidden lg:flex flex-col items-center">
      <span className="text-[10px] font-mono-code text-muted-foreground mb-2 tracking-wider">DEPTH</span>
      <div className="relative w-3 h-64 rounded-full overflow-hidden border border-border bg-card">
        {layers.map((layer, i) => (
          <div
            key={i}
            className={`absolute w-full ${layer.color}`}
            style={{
              top: `${layer.depth}%`,
              height: `${(layers[i + 1]?.depth ?? 100) - layer.depth}%`,
            }}
          />
        ))}
        <motion.div
          className="absolute w-full h-1.5 bg-amber rounded-full shadow-lg shadow-amber/60"
          animate={{ top: `${scrollDepth}%` }}
          transition={{ type: 'spring', stiffness: 120, damping: 20 }}
        />
      </div>
      {layers.map((layer, i) => (
        <span
          key={i}
          className="absolute text-[9px] font-mono-code text-muted-foreground whitespace-nowrap"
          style={{
            top: `calc(50% - 128px + ${layer.depth * 2.56}px)`,
            right: '24px',
          }}
        >
          {layer.label}
        </span>
      ))}
      <span className="text-[10px] font-mono-code text-amber mt-2">{scrollDepth.toFixed(0)}m</span>
    </div>
  );
};

export default DepthMeter;
