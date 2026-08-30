import { useMemo, useState, useCallback, useRef, forwardRef } from "react";
import { CityBlock } from "@/lib/github";

interface CitySkylineProps {
  blocks: CityBlock[];
  id?: string;
}

const BLOCK_WIDTH = 14;
const MAX_BUILDING_HEIGHT = 180;
const GROUND_Y = 260;
const SVG_HEIGHT = 320;

interface TooltipState {
  x: number;
  y: number;
  text: string;
  subtext: string;
  visible: boolean;
}

function BuildingBlock({ block, x, index, onHover, onLeave }: { block: CityBlock; x: number; index: number; onHover: (x: number, y: number, block: CityBlock) => void; onLeave: () => void }) {
  const height = Math.max(block.height * MAX_BUILDING_HEIGHT, 20);
  const y = GROUND_Y - height;
  const width = BLOCK_WIDTH - 2;
  const windowRows = Math.floor(height / 16);
  const windowCols = width > 8 ? 2 : 1;

  // Deterministic windows based on index
  const windows = useMemo(() => {
    const seed = index * 7 + 13;
    return Array.from({ length: windowRows * windowCols }).map((_, i) => {
      const hash = ((seed + i * 31) % 100) / 100;
      return {
        lit: hash > 0.35,
        flicker: hash > 0.75,
        dur: 3 + (hash * 4),
      };
    });
  }, [index, windowRows, windowCols]);

  return (
    <g
      style={{ animationDelay: `${index * 8}ms` }}
      className="origin-bottom animate-building-rise cursor-pointer"
      onMouseEnter={() => onHover(x + width / 2, y - 8, block)}
      onMouseLeave={onLeave}
    >
      <rect x={x} y={y} width={width} height={height} rx={1}
        fill="hsl(var(--building))" stroke="hsl(var(--border))" strokeWidth={0.5} />
      
      {block.height > 0.6 && (
        <polygon points={`${x + width / 2},${y - 6} ${x + 1},${y} ${x + width - 1},${y}`}
          fill="hsl(var(--building))" stroke="hsl(var(--border))" strokeWidth={0.3} />
      )}
      
      {block.height > 0.85 && (
        <>
          <line x1={x + width / 2} y1={y - 6} x2={x + width / 2} y2={y - 18}
            stroke="hsl(var(--muted-foreground))" strokeWidth={0.8} />
          <circle cx={x + width / 2} cy={y - 18} r={1.5} fill="hsl(var(--primary))" opacity={0.9}>
            <animate attributeName="opacity" values="0.4;1;0.4" dur="2s" repeatCount="indefinite" />
          </circle>
        </>
      )}

      {windows.map((w, i) => {
        const row = Math.floor(i / windowCols);
        const col = i % windowCols;
        const wx = x + 2 + col * (width / windowCols);
        const wy = y + 4 + row * 16;
        return (
          <rect key={i} x={wx} y={wy} width={3} height={4} rx={0.3}
            fill={w.lit ? "hsl(var(--window-glow))" : "hsl(var(--building))"}
            opacity={w.lit ? 0.9 : 0.3}
          >
            {w.flicker && (
              <animate attributeName="opacity" values="0.9;0.3;0.9" dur={`${w.dur}s`} repeatCount="indefinite" />
            )}
          </rect>
        );
      })}

      {/* Invisible hover target */}
      <rect x={x - 1} y={y - 20} width={width + 2} height={height + 20} fill="transparent" />
    </g>
  );
}

function ParkBlock({ block, x, index, onHover, onLeave }: { block: CityBlock; x: number; index: number; onHover: (x: number, y: number, block: CityBlock) => void; onLeave: () => void }) {
  const treeX = x + (BLOCK_WIDTH - 2) / 2;
  return (
    <g style={{ animationDelay: `${index * 8}ms` }} className="origin-bottom animate-building-rise cursor-pointer"
      onMouseEnter={() => onHover(treeX, GROUND_Y - 28, block)} onMouseLeave={onLeave}>
      <rect x={x} y={GROUND_Y - 3} width={BLOCK_WIDTH - 2} height={3} rx={1} fill="hsl(var(--park))" opacity={0.6} />
      <rect x={treeX - 1} y={GROUND_Y - 14} width={2} height={11} fill="hsl(30 40% 30%)" />
      <circle cx={treeX} cy={GROUND_Y - 18} r={5} fill="hsl(var(--accent))" opacity={0.8} />
      <rect x={x - 1} y={GROUND_Y - 25} width={BLOCK_WIDTH} height={28} fill="transparent" />
    </g>
  );
}

function BridgeBlock({ block, x, index, onHover, onLeave }: { block: CityBlock; x: number; index: number; onHover: (x: number, y: number, block: CityBlock) => void; onLeave: () => void }) {
  return (
    <g style={{ animationDelay: `${index * 8}ms` }} className="origin-bottom animate-building-rise cursor-pointer"
      onMouseEnter={() => onHover(x + BLOCK_WIDTH / 2, GROUND_Y - 28, block)} onMouseLeave={onLeave}>
      <rect x={x - 2} y={GROUND_Y - 10} width={BLOCK_WIDTH + 2} height={3} rx={1} fill="hsl(var(--bridge))" />
      <rect x={x} y={GROUND_Y - 16} width={1.5} height={6} fill="hsl(var(--bridge))" opacity={0.7} />
      <rect x={x + BLOCK_WIDTH - 4} y={GROUND_Y - 16} width={1.5} height={6} fill="hsl(var(--bridge))" opacity={0.7} />
      <path d={`M${x},${GROUND_Y - 16} Q${x + (BLOCK_WIDTH - 2) / 2},${GROUND_Y - 22} ${x + BLOCK_WIDTH - 4},${GROUND_Y - 16}`}
        fill="none" stroke="hsl(var(--bridge))" strokeWidth={0.6} opacity={0.5} />
      <rect x={x - 2} y={GROUND_Y - 25} width={BLOCK_WIDTH + 4} height={28} fill="transparent" />
    </g>
  );
}

function SvgTooltip({ tooltip }: { tooltip: TooltipState }) {
  if (!tooltip.visible) return null;
  const padding = 6;
  const textLen = Math.max(tooltip.text.length, tooltip.subtext.length) * 4.5 + padding * 2;
  const boxH = 32;
  const boxX = tooltip.x - textLen / 2;
  const boxY = tooltip.y - boxH - 6;

  return (
    <g pointerEvents="none">
      <rect x={boxX} y={boxY} width={textLen} height={boxH} rx={4}
        fill="hsl(var(--popover))" stroke="hsl(var(--border))" strokeWidth={0.5} opacity={0.95} />
      <polygon points={`${tooltip.x - 4},${boxY + boxH} ${tooltip.x},${boxY + boxH + 5} ${tooltip.x + 4},${boxY + boxH}`}
        fill="hsl(var(--popover))" />
      <text x={tooltip.x} y={boxY + 13} textAnchor="middle" fill="hsl(var(--foreground))" fontSize={8} fontWeight={600} fontFamily="Space Grotesk, sans-serif">
        {tooltip.text}
      </text>
      <text x={tooltip.x} y={boxY + 24} textAnchor="middle" fill="hsl(var(--muted-foreground))" fontSize={6.5} fontFamily="JetBrains Mono, monospace">
        {tooltip.subtext}
      </text>
    </g>
  );
}

const CitySkyline = forwardRef<SVGSVGElement, CitySkylineProps>(({ blocks, id }, ref) => {
  const svgWidth = blocks.length * BLOCK_WIDTH + 40;
  const [tooltip, setTooltip] = useState<TooltipState>({ x: 0, y: 0, text: "", subtext: "", visible: false });

  const handleHover = useCallback((x: number, y: number, block: CityBlock) => {
    const typeLabels = { building: `🏢 ${block.count} commits`, park: "🌳 Park day", bridge: "🌉 Bridge" };
    setTooltip({ x, y, text: block.date, subtext: typeLabels[block.type], visible: true });
  }, []);

  const handleLeave = useCallback(() => {
    setTooltip(t => ({ ...t, visible: false }));
  }, []);

  const stars = useMemo(() =>
    Array.from({ length: 60 }).map((_, i) => {
      const hash = ((i * 7919 + 104729) % 100000) / 100000;
      const hash2 = ((i * 6271 + 52711) % 100000) / 100000;
      return {
        cx: hash * svgWidth,
        cy: hash2 * (GROUND_Y - 80),
        r: (hash * 1.2) + 0.3,
        delay: hash2 * 5,
      };
    }), [svgWidth]
  );

  const gradientId = id ? `sky-${id}` : "skyGradient";
  const groundId = id ? `ground-${id}` : "groundGradient";

  return (
    <div className="w-full overflow-x-auto pb-4">
      <svg ref={ref} id={id} viewBox={`0 0 ${svgWidth} ${SVG_HEIGHT}`} width={svgWidth} height={SVG_HEIGHT}
        className="min-w-full" style={{ minWidth: svgWidth }}>
        <defs>
          <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="hsl(var(--sky-top))" />
            <stop offset="70%" stopColor="hsl(222 35% 15%)" />
            <stop offset="100%" stopColor="hsl(var(--sky-bottom))" />
          </linearGradient>
          <linearGradient id={groundId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="hsl(222 25% 10%)" />
            <stop offset="100%" stopColor="hsl(222 30% 6%)" />
          </linearGradient>
        </defs>
        
        <rect width={svgWidth} height={SVG_HEIGHT} fill={`url(#${gradientId})`} />
        
        {stars.map((star, i) => (
          <circle key={i} cx={star.cx} cy={star.cy} r={star.r} fill="hsl(var(--foreground))" opacity={0.5}>
            <animate attributeName="opacity" values="0.2;0.8;0.2" dur={`${2 + star.delay}s`} repeatCount="indefinite" />
          </circle>
        ))}
        
        <circle cx={svgWidth - 60} cy={50} r={18} fill="hsl(45 60% 85%)" opacity={0.9} />
        <circle cx={svgWidth - 54} cy={46} r={16} fill={`url(#${gradientId})`} />
        
        <rect x={0} y={GROUND_Y} width={svgWidth} height={SVG_HEIGHT - GROUND_Y} fill={`url(#${groundId})`} />
        
        {blocks.map((block, i) => {
          const x = 20 + i * BLOCK_WIDTH;
          const common = { x, index: i, onHover: handleHover, onLeave: handleLeave, block };
          if (block.type === 'building') return <BuildingBlock key={i} {...common} />;
          if (block.type === 'park') return <ParkBlock key={i} {...common} />;
          return <BridgeBlock key={i} {...common} />;
        })}

        <SvgTooltip tooltip={tooltip} />
      </svg>
    </div>
  );
});

CitySkyline.displayName = "CitySkyline";
export default CitySkyline;
