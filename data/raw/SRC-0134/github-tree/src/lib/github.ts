export interface ContributionDay {
  date: string;
  count: number;
}

export interface ContributionWeek {
  days: ContributionDay[];
}

export async function fetchContributions(username: string, year?: number | string): Promise<ContributionDay[]> {
  const y = year || 'last';
  const response = await fetch(`https://github-contributions-api.jogruber.de/v4/${username}?y=${y}`);
  
  if (!response.ok) {
    throw new Error(`Could not fetch contributions for ${username}`);
  }
  
  const data = await response.json();
  
  return (data.contributions as Array<{ date: string; count: number }>).map(c => ({
    date: c.date,
    count: c.count,
  }));
}

export interface CityBlock {
  type: 'building' | 'park' | 'bridge';
  height: number; // 0-1 normalized
  count: number;
  date: string;
  streak: boolean; // part of a consecutive streak
}

export function contributionsToCity(contributions: ContributionDay[]): CityBlock[] {
  if (!contributions.length) return [];
  
  const maxCount = Math.max(...contributions.map(c => c.count), 1);
  
  return contributions.map((day, i) => {
    const prev = contributions[i - 1];
    const next = contributions[i + 1];
    const streak = (prev?.count > 0 && day.count > 0) || (next?.count > 0 && day.count > 0);
    
    if (day.count === 0) {
      // Check if it's between two active days → bridge, otherwise park
      const isBridge = prev?.count > 0 && next?.count > 0;
      return {
        type: isBridge ? 'bridge' : 'park',
        height: 0,
        count: 0,
        date: day.date,
        streak: false,
      };
    }
    
    return {
      type: 'building' as const,
      height: day.count / maxCount,
      count: day.count,
      date: day.date,
      streak,
    };
  });
}
