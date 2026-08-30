const StratumBackground = () => {
  return (
    <svg
      className="absolute inset-0 w-full h-full pointer-events-none"
      preserveAspectRatio="none"
      viewBox="0 0 100 100"
    >
      <defs>
        <pattern id="soil-dots" x="0" y="0" width="4" height="4" patternUnits="userSpaceOnUse">
          <circle cx="1" cy="1" r="0.3" fill="hsl(25 30% 12% / 0.08)" />
          <circle cx="3" cy="3" r="0.2" fill="hsl(25 30% 12% / 0.05)" />
        </pattern>
        <pattern id="rock-lines" x="0" y="0" width="20" height="2" patternUnits="userSpaceOnUse">
          <line x1="0" y1="1" x2="20" y2="1" stroke="hsl(25 30% 12% / 0.06)" strokeWidth="0.5" />
        </pattern>
      </defs>

      {/* Surface grass layer */}
      <rect x="0" y="0" width="100" height="8" fill="hsl(80 25% 55%)" />
      <path d="M0,7 Q10,5 20,7 T40,6 T60,7.5 T80,6 T100,7 L100,8 L0,8 Z" fill="hsl(35 35% 55%)" />

      {/* Top soil */}
      <rect x="0" y="8" width="100" height="20" fill="hsl(35 35% 55%)" />
      <rect x="0" y="8" width="100" height="20" fill="url(#soil-dots)" />

      {/* Transition wavy line */}
      <path d="M0,28 Q15,26 30,28 T60,27 T100,28" fill="none" stroke="hsl(25 40% 35%)" strokeWidth="0.3" />

      {/* Mid layer */}
      <rect x="0" y="28" width="100" height="25" fill="hsl(25 40% 40%)" />
      <rect x="0" y="28" width="100" height="25" fill="url(#rock-lines)" />

      {/* Embedded rocks */}
      <ellipse cx="15" cy="38" rx="3" ry="1.5" fill="hsl(25 30% 35%)" opacity="0.5" />
      <ellipse cx="70" cy="42" rx="4" ry="2" fill="hsl(20 35% 32%)" opacity="0.4" />
      <ellipse cx="45" cy="48" rx="2" ry="1" fill="hsl(25 28% 38%)" opacity="0.3" />

      {/* Deep layer */}
      <path d="M0,53 Q25,51 50,53 T100,52 L100,78 L0,78 Z" fill="hsl(18 45% 28%)" />
      <rect x="0" y="53" width="100" height="25" fill="url(#rock-lines)" opacity="0.5" />

      {/* Ancient layer */}
      <path d="M0,78 Q20,76 40,78 T80,77 T100,78 L100,100 L0,100 Z" fill="hsl(15 50% 18%)" />

      {/* Fossil hints */}
      <circle cx="30" cy="85" r="1.5" fill="none" stroke="hsl(38 40% 40%)" strokeWidth="0.2" opacity="0.4" />
      <circle cx="75" cy="90" r="1" fill="none" stroke="hsl(38 40% 40%)" strokeWidth="0.2" opacity="0.3" />
    </svg>
  );
};

export default StratumBackground;
