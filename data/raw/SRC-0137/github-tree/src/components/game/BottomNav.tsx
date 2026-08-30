import { useGame } from '@/game/GameContext';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';

export default function BottomNav() {
  const { state } = useGame();
  const navigate = useNavigate();
  const location = useLocation();
  if (!state) return null;

  const activeEvents = state.events.filter(e => !e.resolved).length;

  const items = [
    { path: '/', icon: '🏠', label: '양봉장', badge: activeEvents > 0 ? activeEvents : undefined },
    { path: '/shop', icon: '🏪', label: '상점' },
    { path: '/research', icon: '🔬', label: '연구' },
    { path: '/prestige', icon: '🌟', label: '명성' },
    { path: '/settings', icon: '⚙️', label: '설정' },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t-2 border-honey-dark/40 bg-card/95 backdrop-blur-md px-1 py-1.5 flex justify-around">
      {items.map(item => {
        const isActive = location.pathname === item.path;
        return (
          <motion.button
            key={item.path}
            whileTap={{ scale: 0.9 }}
            onClick={() => navigate(item.path)}
            className={`relative flex flex-col items-center gap-0.5 p-1.5 rounded-xl transition-all min-w-[48px] ${
              isActive
                ? 'bg-primary/15 text-foreground nav-active-glow'
                : 'text-muted-foreground hover:bg-secondary/60'
            }`}
          >
            <span className={`text-lg transition-transform ${isActive ? 'scale-110' : ''}`}>{item.icon}</span>
            <span className={`text-[9px] font-bold tracking-wide ${isActive ? 'text-primary' : ''}`}>{item.label}</span>
            {item.badge && (
              <span className="absolute -top-1 -right-1 bg-danger text-primary-foreground text-[9px] font-bold w-4.5 h-4.5 rounded-full flex items-center justify-center animate-pulse ring-2 ring-card">
                {item.badge}
              </span>
            )}
            {isActive && (
              <motion.div
                layoutId="nav-indicator"
                className="absolute -top-0.5 left-1/2 -translate-x-1/2 w-6 h-0.5 rounded-full honey-gradient"
              />
            )}
          </motion.button>
        );
      })}
    </nav>
  );
}
