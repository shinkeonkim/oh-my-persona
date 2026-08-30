export function StampSeal({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 200 200"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Outer circle */}
      <circle cx="100" cy="100" r="90" fill="none" stroke="hsl(0 75% 45%)" strokeWidth="6" opacity="0.85" />
      {/* Inner circle */}
      <circle cx="100" cy="100" r="78" fill="none" stroke="hsl(0 75% 45%)" strokeWidth="2" opacity="0.7" />

      {/* Center text - CERTIFIED */}
      <text
        x="100"
        y="105"
        textAnchor="middle"
        dominantBaseline="middle"
        fontFamily="'Playfair Display', serif"
        fontWeight="900"
        fontSize="30"
        fill="hsl(0 75% 45%)"
        opacity="0.9"
      >
        CERTIFIED
      </text>

      {/* Bottom curved text - WORKS ON MINE */}
      <defs>
        <path id="bottomArc" d="M 30,100 a 70,70 0 0,0 140,0" fill="none" />
      </defs>
      <text
        fontFamily="'Playfair Display', serif"
        fontWeight="700"
        fontSize="14"
        fill="hsl(0 75% 45%)"
        opacity="0.85"
        letterSpacing="3"
      >
        <textPath href="#bottomArc" startOffset="50%" textAnchor="middle">
          WORKS ON MINE
        </textPath>
      </text>

      {/* Top curved text - decorative stars */}
      <defs>
        <path id="topArc" d="M 30,100 a 70,70 0 0,1 140,0" fill="none" />
      </defs>
      <text
        fontFamily="'Playfair Display', serif"
        fontWeight="700"
        fontSize="13"
        fill="hsl(0 75% 45%)"
        opacity="0.85"
        letterSpacing="4"
      >
        <textPath href="#topArc" startOffset="50%" textAnchor="middle">
          ★ DEVELOPER ★
        </textPath>
      </text>

      {/* Distressed overlay effect using small random shapes */}
      <g opacity="0.08">
        <rect x="40" y="60" width="8" height="3" fill="hsl(0 75% 45%)" transform="rotate(15 44 61)" />
        <rect x="150" y="80" width="6" height="4" fill="hsl(0 75% 45%)" transform="rotate(-20 153 82)" />
        <rect x="70" y="140" width="10" height="2" fill="hsl(0 75% 45%)" transform="rotate(30 75 141)" />
        <rect x="120" y="50" width="5" height="5" fill="hsl(0 75% 45%)" transform="rotate(-10 122 52)" />
      </g>
    </svg>
  );
}
