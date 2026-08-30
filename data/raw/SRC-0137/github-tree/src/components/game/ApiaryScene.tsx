import { type Season } from '@/game/types';
import springBg from '@/assets/season-spring.jpg';
import summerBg from '@/assets/season-summer.jpg';
import fallBg from '@/assets/season-fall.jpg';
import winterBg from '@/assets/season-winter.jpg';
import { useMemo } from 'react';
import { motion } from 'framer-motion';

const bgMap: Record<Season, string> = {
  spring: springBg, summer: summerBg, fall: fallBg, winter: winterBg,
};

const seasonAccent: Record<Season, string> = {
  spring: 'from-season-spring/20 via-transparent to-season-spring/5',
  summer: 'from-season-summer/20 via-transparent to-season-summer/5',
  fall: 'from-season-fall/20 via-transparent to-season-fall/5',
  winter: 'from-season-winter/20 via-transparent to-season-winter/5',
};

const seasonParticles: Record<Season, { emoji: string; count: number }> = {
  spring: { emoji: '🌸', count: 6 },
  summer: { emoji: '☀️', count: 4 },
  fall: { emoji: '🍂', count: 7 },
  winter: { emoji: '❄️', count: 8 },
};

interface Props {
  season: Season;
  children: React.ReactNode;
}

function FloatingBee({ delay, x, size }: { delay: number; x: number; size: number }) {
  return (
    <span
      className="absolute animate-bee pointer-events-none select-none z-10"
      style={{
        left: `${x}%`,
        top: `${10 + Math.random() * 30}%`,
        animationDelay: `${delay}s`,
        fontSize: `${size}px`,
        animationDuration: `${3 + Math.random() * 3}s`,
      }}
    >
      🐝
    </span>
  );
}

function SeasonParticle({ emoji, delay, x, duration }: { emoji: string; delay: number; x: number; duration: number }) {
  return (
    <motion.span
      className="absolute pointer-events-none select-none z-10 opacity-40"
      initial={{ y: '-10%', x: `${x}vw`, rotate: 0 }}
      animate={{ y: '110%', x: `${x + (Math.random() - 0.5) * 20}vw`, rotate: 360 }}
      transition={{ duration, delay, repeat: Infinity, ease: 'linear' }}
      style={{ fontSize: `${10 + Math.random() * 8}px`, left: 0, top: 0 }}
    >
      {emoji}
    </motion.span>
  );
}

export default function ApiaryScene({ season, children }: Props) {
  const bees = useMemo(() =>
    Array.from({ length: 8 }, (_, i) => ({
      id: i,
      delay: Math.random() * 4,
      x: 5 + Math.random() * 85,
      size: 12 + Math.random() * 10,
    })), []);

  const particles = useMemo(() => {
    const { emoji, count } = seasonParticles[season];
    return Array.from({ length: count }, (_, i) => ({
      id: i,
      emoji,
      delay: Math.random() * 8,
      x: Math.random() * 90,
      duration: 6 + Math.random() * 6,
    }));
  }, [season]);

  return (
    <div className="rounded-2xl overflow-hidden relative mb-4 border-2 border-border/40 game-shadow">
      {/* Background image */}
      <div className="absolute inset-0 z-0">
        <img
          src={bgMap[season]}
          alt={`${season} apiary`}
          className="w-full h-full object-cover opacity-25 transition-all duration-1000"
        />
        {/* Layered gradients */}
        <div className="absolute inset-0 bg-gradient-to-b from-background/20 via-background/50 to-background" />
        <div className={`absolute inset-0 bg-gradient-to-br ${seasonAccent[season]}`} />
      </div>

      {/* Vignette */}
      <div className="absolute inset-0 z-[1] pointer-events-none"
        style={{ boxShadow: 'inset 0 0 60px 20px hsl(var(--background) / 0.3)' }} />

      {/* Ground strip */}
      <div className="absolute bottom-0 left-0 right-0 h-8 z-[2] pointer-events-none">
        <div className="w-full h-full bg-gradient-to-t from-background via-background/80 to-transparent" />
      </div>

      {/* Floating bees */}
      <div className="absolute inset-0 z-10 pointer-events-none overflow-hidden">
        {bees.map(bee => (
          <FloatingBee key={bee.id} delay={bee.delay} x={bee.x} size={bee.size} />
        ))}
      </div>

      {/* Season particles */}
      <div className="absolute inset-0 z-10 pointer-events-none overflow-hidden">
        {particles.map(p => (
          <SeasonParticle key={p.id} emoji={p.emoji} delay={p.delay} x={p.x} duration={p.duration} />
        ))}
      </div>

      {/* Content */}
      <div className="relative z-20 p-4 pt-3">
        {children}
      </div>
    </div>
  );
}
