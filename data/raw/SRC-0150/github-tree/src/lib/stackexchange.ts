export interface StackAnswer {
  answer_id: number;
  question_id: number;
  score: number;
  creation_date: number;
  body: string;
  owner: {
    display_name: string;
    reputation?: number;
  };
  title?: string;
  tags?: string[];
  link?: string;
}

export interface SearchResult {
  items: StackAnswer[];
  has_more: boolean;
}

export async function searchOldAnswers(query: string): Promise<SearchResult> {
  // Year ranges from 2008 to 2012
  const yearRanges = [
    { from: 1199145600, to: 1230768000 }, // 2008-2009
    { from: 1230768000, to: 1262304000 }, // 2009-2010
    { from: 1262304000, to: 1293840000 }, // 2010-2011
    { from: 1293840000, to: 1325376000 }, // 2011-2012
    { from: 1325376000, to: 1356998400 }, // 2012-2013
  ];

  const fetchRange = async (range: { from: number; to: number }) => {
    const randomPage = Math.floor(Math.random() * 3) + 1;
    const params = new URLSearchParams({
      order: 'desc',
      sort: 'votes',
      intitle: query,
      site: 'stackoverflow',
      filter: '!nNPvSNdWme',
      pagesize: '4',
      page: String(randomPage),
      fromdate: String(range.from),
      todate: String(range.to),
    });

    try {
      const res = await fetch(`https://api.stackexchange.com/2.3/search?${params}`);
      if (!res.ok) return [];
      const data = await res.json();
      return data.items || [];
    } catch {
      return [];
    }
  };

  const allResults = await Promise.all(yearRanges.map(fetchRange));
  const combined = allResults.flat();

  return {
    items: combined.map((q: any) => ({
      answer_id: q.question_id,
      question_id: q.question_id,
      score: q.score,
      creation_date: q.creation_date,
      body: q.body || '',
      owner: {
        display_name: q.owner?.display_name || 'Unknown',
        reputation: q.owner?.reputation,
      },
      title: q.title,
      tags: q.tags,
      link: q.link,
    })),
    has_more: false,
  };
}

export function getEraLabel(timestamp: number): string {
  const year = new Date(timestamp * 1000).getFullYear();
  if (year <= 2008) return '선캄브리아기 — Stack Overflow 태초';
  if (year <= 2009) return '고생대 — jQuery 전성시대';
  if (year <= 2010) return '중생대 — MVC 프레임워크의 부상';
  if (year <= 2011) return '신생대 — Node.js 혁명기';
  return '현생대 — 모던 웹의 여명';
}

export function getArchaeologicalComment(tags: string[], year: number): string {
  const age = new Date().getFullYear() - year;

  if (tags?.some(t => ['jquery', 'jquery-ui'].includes(t))) {
    return `이 jQuery 유물은 약 ${age}년 전 문명의 것으로 추정됩니다. 당시 모든 웹 개발자의 필수 도구였습니다.`;
  }
  if (tags?.some(t => ['php', 'mysql'].includes(t))) {
    return `PHP-MySQL 복합 유물입니다. ${age}년 전 LAMP 스택 문명의 대표적 산물입니다.`;
  }
  if (tags?.some(t => ['java', 'spring'].includes(t))) {
    return `Java 계층의 유물입니다. ${age}년의 세월에도 여전히 엔터프라이즈 지층에서 발견됩니다.`;
  }
  if (tags?.some(t => ['html', 'css', 'html5', 'css3'].includes(t))) {
    return `HTML/CSS 원시 유물입니다. ${age}년 전 웹 표준 전쟁의 흔적이 남아있습니다.`;
  }
  if (tags?.some(t => ['javascript', 'prototype'].includes(t))) {
    return `순수 JavaScript 유물입니다. Framework 이전 시대, ${age}년 전의 것으로 보입니다.`;
  }
  if (tags?.some(t => ['c#', '.net', 'asp.net'].includes(t))) {
    return `Microsoft 문명의 유물입니다. ${age}년 전 .NET 제국의 전성기를 보여줍니다.`;
  }
  if (tags?.some(t => ['python', 'django'].includes(t))) {
    return `Python 초기 유물입니다. ${age}년 전, 이 언어가 아직 주류가 되기 전의 것입니다.`;
  }
  if (tags?.some(t => ['perl', 'cgi'].includes(t))) {
    return `Perl/CGI 화석입니다! ${age}년 전 웹 서버의 최전선에서 사용된 고대 기술입니다.`;
  }
  if (tags?.some(t => ['flash', 'actionscript', 'flex'].includes(t))) {
    return `Flash 문명의 멸종된 유물입니다. ${age}년 전 웹의 절반을 지배했던 제국의 유산입니다.`;
  }
  if (tags?.some(t => ['xml', 'xslt', 'soap'].includes(t))) {
    return `XML/SOAP 유물입니다. ${age}년 전 "Enterprise" 문명의 정수가 담겨있습니다.`;
  }
  return `이 디지털 유물은 약 ${age}년 전의 것으로 추정됩니다. 당시 개발자들의 고민이 고스란히 담겨있습니다.`;
}

export function getStratumDepth(year: number): number {
  // 2008 = deepest (100), 2012 = shallowest (0)
  return Math.min(100, Math.max(0, ((2012 - year) / 4) * 100));
}

export function getStratumColor(year: number): string {
  if (year <= 2008) return 'stratum-ancient';
  if (year <= 2009) return 'stratum-deep';
  if (year <= 2010) return 'stratum-mid';
  if (year <= 2011) return 'stratum-shallow';
  return 'stratum-surface';
}
