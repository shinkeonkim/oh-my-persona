import { useState, useMemo, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Pickaxe, Layers, Skull } from 'lucide-react';
import SearchBar from '@/components/SearchBar';
import ArtifactCard from '@/components/ArtifactCard';
import ArtifactModal from '@/components/ArtifactModal';
import DepthMeter from '@/components/DepthMeter';
import StratumBackground from '@/components/StratumBackground';
import StratumDivider from '@/components/StratumDivider';
import { searchOldAnswers, StackAnswer } from '@/lib/stackexchange';

const Index = () => {
  const [results, setResults] = useState<StackAnswer[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const sectionRefs = useRef<(HTMLDivElement | null)[]>([]);
  const [selectedArtifact, setSelectedArtifact] = useState<StackAnswer | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  const handleSearch = async (query: string) => {
    setIsLoading(true);
    setError(null);
    setHasSearched(true);
    try {
      const data = await searchOldAnswers(query);
      // Sort newest first (descending) — shallow on top, deep below
      const sorted = data.items.sort((a, b) => b.creation_date - a.creation_date);
      setResults(sorted);
    } catch (err) {
      setError('발굴 작업 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Group by year, newest first
  const groupedByYear = useMemo(() => {
    const groups: Record<number, StackAnswer[]> = {};
    results.forEach((r) => {
      const year = new Date(r.creation_date * 1000).getFullYear();
      if (!groups[year]) groups[year] = [];
      groups[year].push(r);
    });
    // Sort years descending (newest/shallowest first)
    return Object.entries(groups)
      .sort(([a], [b]) => Number(b) - Number(a))
      .map(([year, items]) => ({ year: Number(year), items }));
  }, [results]);

  const years = useMemo(() => groupedByYear.map((g) => g.year), [groupedByYear]);

  return (
    <div className="min-h-screen relative overflow-hidden">
      <div className="fixed inset-0 opacity-15 pointer-events-none">
        <StratumBackground />
      </div>

      {results.length > 0 && (
        <DepthMeter sectionRefs={sectionRefs} years={years} />
      )}

      <div className="relative z-10 max-w-3xl mx-auto px-6 py-12">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-12"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <Pickaxe className="w-8 h-8 text-amber" />
            <h1 className="font-display text-5xl font-900 text-foreground tracking-tight">
              StackDigger
            </h1>
            <Layers className="w-8 h-8 text-sienna" />
          </div>
          <p className="text-muted-foreground text-lg max-w-lg mx-auto leading-relaxed">
            Stack Overflow의 가장 오래된 답변을 유물처럼 발굴합니다.
            <br />
            <span className="text-sm">2008~2012년, 웹 개발 고대 문명의 지층을 탐험하세요.</span>
          </p>
          <div className="flex h-2 rounded-full overflow-hidden mt-6 max-w-xs mx-auto">
            <div className="flex-1 bg-stratum-surface" />
            <div className="flex-1 bg-stratum-shallow" />
            <div className="flex-1 bg-stratum-mid" />
            <div className="flex-1 bg-stratum-deep" />
            <div className="flex-1 bg-stratum-ancient" />
          </div>
        </motion.header>

        <SearchBar onSearch={handleSearch} isLoading={isLoading} />

        <div className="mt-10">
          <AnimatePresence mode="wait">
            {error && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-center p-6 bg-destructive/10 border border-destructive/20 rounded-lg"
              >
                <p className="text-destructive">{error}</p>
              </motion.div>
            )}

            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-center py-16"
              >
                <motion.div
                  animate={{ rotate: [0, 10, -10, 0], y: [0, -5, 0] }}
                  transition={{ repeat: Infinity, duration: 1.5 }}
                >
                  <Pickaxe className="w-12 h-12 text-amber mx-auto mb-4" />
                </motion.div>
                <p className="text-muted-foreground font-display text-lg">발굴 중...</p>
                <p className="text-muted-foreground text-sm mt-1">지층을 파헤치고 있습니다</p>
              </motion.div>
            )}

            {!isLoading && hasSearched && results.length === 0 && !error && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-16"
              >
                <Skull className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground font-display text-lg">
                  이 지층에서는 유물이 발견되지 않았습니다.
                </p>
                <p className="text-muted-foreground text-sm mt-1">
                  다른 키워드로 발굴을 시도해보세요.
                </p>
              </motion.div>
            )}

            {!isLoading && results.length > 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <div className="text-center mb-8">
                  <p className="text-sm font-mono-code text-muted-foreground">
                    ▼ 발굴 보고서: <span className="text-amber">{results.length}개</span>의 유물 발견 · 
                    {groupedByYear.length}개 지층 ▼
                  </p>
                </div>

                {/* Grouped by year */}
                <div className="space-y-2">
                  {groupedByYear.map((group, gi) => {
                    let cardIdx = 0;
                    for (let i = 0; i < gi; i++) cardIdx += groupedByYear[i].items.length;

                    return (
                      <div
                        key={group.year}
                        ref={(el) => { sectionRefs.current[gi] = el; }}
                      >
                        <StratumDivider
                          year={group.year}
                          count={group.items.length}
                          index={gi}
                        />
                        <div className="space-y-4 mb-8 pl-4 border-l-2 border-border ml-1.5">
                          {group.items.map((artifact, i) => (
                            <ArtifactCard
                              key={artifact.answer_id}
                              artifact={artifact}
                              index={cardIdx + i}
                              onClick={() => {
                                setSelectedArtifact(artifact);
                                setModalOpen(true);
                              }}
                            />
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <ArtifactModal
          artifact={selectedArtifact}
          open={modalOpen}
          onOpenChange={setModalOpen}
        />
      </div>
    </div>
  );
};

export default Index;
