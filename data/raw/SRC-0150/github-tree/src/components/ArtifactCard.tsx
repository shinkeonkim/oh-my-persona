import { motion } from 'framer-motion';
import { ExternalLink, ThumbsUp, Calendar, User } from 'lucide-react';
import { StackAnswer, getArchaeologicalComment, getEraLabel, getStratumDepth } from '@/lib/stackexchange';

interface ArtifactCardProps {
  artifact: StackAnswer;
  index: number;
  onClick?: () => void;
}

const ArtifactCard = ({ artifact, index, onClick }: ArtifactCardProps) => {
  const date = new Date(artifact.creation_date * 1000);
  const year = date.getFullYear();
  const depth = getStratumDepth(year);
  const comment = getArchaeologicalComment(artifact.tags || [], year);
  const era = getEraLabel(artifact.creation_date);

  // Determine card styling based on depth
  const getBgClass = () => {
    if (depth >= 80) return 'bg-stratum-ancient/20 border-stratum-ancient/40';
    if (depth >= 60) return 'bg-stratum-deep/20 border-stratum-deep/40';
    if (depth >= 40) return 'bg-stratum-mid/20 border-stratum-mid/40';
    if (depth >= 20) return 'bg-stratum-shallow/20 border-stratum-shallow/40';
    return 'bg-stratum-surface/20 border-stratum-surface/40';
  };

  const getDepthLabel = () => {
    if (depth >= 80) return '깊이 ████████░░ 심층';
    if (depth >= 60) return '깊이 ██████░░░░ 하층';
    if (depth >= 40) return '깊이 ████░░░░░░ 중층';
    if (depth >= 20) return '깊이 ██░░░░░░░░ 상층';
    return '깊이 █░░░░░░░░░ 표층';
  };

  // Strip HTML tags for preview
  const plainBody = artifact.body
    .replace(/<[^>]+>/g, '')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .slice(0, 300);

  return (
    <motion.div
      initial={{ opacity: 0, x: -30, y: 20 }}
      animate={{ opacity: 1, x: 0, y: 0 }}
      transition={{ delay: index * 0.12, duration: 0.5, ease: 'easeOut' }}
      onClick={onClick}
      className={`relative border-2 rounded-lg p-5 ${getBgClass()} backdrop-blur-sm 
                  hover:artifact-glow transition-all duration-300 group cursor-pointer`}
    >
      {/* Depth indicator */}
      <div className="absolute -left-3 top-4 px-2 py-0.5 rounded text-[10px] font-mono-code 
                      bg-foreground/80 text-background tracking-wider">
        {depth.toFixed(0)}m
      </div>

      {/* Era badge */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-mono-code text-amber tracking-wide uppercase">
          {era}
        </span>
        <span className="text-[10px] font-mono-code text-muted-foreground">
          {getDepthLabel()}
        </span>
      </div>

      {/* Title */}
      <h3 className="font-display text-lg font-bold text-foreground mb-2 leading-tight"
          dangerouslySetInnerHTML={{ __html: artifact.title || 'Untitled Artifact' }} />

      {/* Tags */}
      {artifact.tags && (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {artifact.tags.slice(0, 5).map((tag) => (
            <span
              key={tag}
              className="px-2 py-0.5 text-[11px] rounded bg-sienna/20 text-sienna 
                         border border-sienna/30 font-mono-code"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Body preview */}
      <p className="text-sm text-muted-foreground leading-relaxed mb-3 font-mono-code">
        {plainBody}...
      </p>

      {/* Archaeological comment */}
      <div className="bg-amber/10 border border-amber/20 rounded p-3 mb-3">
        <p className="text-sm text-foreground/80 italic font-display">
          🏺 "{comment}"
        </p>
      </div>

      {/* Meta footer */}
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1">
            <Calendar className="w-3 h-3" />
            {date.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' })}
          </span>
          <span className="flex items-center gap-1">
            <ThumbsUp className="w-3 h-3" />
            {artifact.score}
          </span>
          <span className="flex items-center gap-1">
            <User className="w-3 h-3" />
            {artifact.owner.display_name}
          </span>
        </div>
        {artifact.link && (
          <a
            href={artifact.link}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-primary hover:text-accent transition-colors"
          >
            원문 보기 <ExternalLink className="w-3 h-3" />
          </a>
        )}
      </div>
    </motion.div>
  );
};

export default ArtifactCard;
