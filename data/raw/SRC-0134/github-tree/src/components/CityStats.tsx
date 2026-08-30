import { CityBlock } from "@/lib/github";
import { Building2, TreePine, Waypoints, Flame } from "lucide-react";

interface CityStatsProps {
  blocks: CityBlock[];
  username: string;
}

export default function CityStats({ blocks, username }: CityStatsProps) {
  const buildings = blocks.filter(b => b.type === 'building');
  const parks = blocks.filter(b => b.type === 'park');
  const bridges = blocks.filter(b => b.type === 'bridge');
  const totalCommits = blocks.reduce((sum, b) => sum + b.count, 0);
  const maxStreak = getMaxStreak(blocks);

  const stats = [
    { icon: Building2, label: "Buildings", value: buildings.length, color: "text-primary" },
    { icon: TreePine, label: "Parks", value: parks.length, color: "text-accent" },
    { icon: Waypoints, label: "Bridges", value: bridges.length, color: "text-bridge" },
    { icon: Flame, label: "Max Streak", value: `${maxStreak}d`, color: "text-primary" },
  ];

  return (
    <div className="mt-8 space-y-4">
      <h2 className="font-mono text-sm text-muted-foreground">
        {username}'s city — {totalCommits.toLocaleString()} total commits
      </h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {stats.map(({ icon: Icon, label, value, color }) => (
          <div key={label} className="bg-secondary/50 border border-border rounded-lg p-3 text-center">
            <Icon className={`w-5 h-5 mx-auto mb-1 ${color}`} />
            <div className="text-lg font-bold text-foreground">{value}</div>
            <div className="text-xs text-muted-foreground">{label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function getMaxStreak(blocks: CityBlock[]): number {
  let max = 0, current = 0;
  for (const b of blocks) {
    if (b.count > 0) { current++; max = Math.max(max, current); }
    else current = 0;
  }
  return max;
}
