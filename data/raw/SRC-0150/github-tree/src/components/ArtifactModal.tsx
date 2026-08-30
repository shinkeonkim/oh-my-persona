import { Dialog, DialogContent, DialogTitle } from '@/components/ui/dialog';
import { Calendar, ThumbsUp, User, ExternalLink } from 'lucide-react';
import { StackAnswer, getArchaeologicalComment, getEraLabel } from '@/lib/stackexchange';
import { useEffect, useRef } from 'react';

interface ArtifactModalProps {
  artifact: StackAnswer | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const ArtifactModal = ({ artifact, open, onOpenChange }: ArtifactModalProps) => {
  const bodyRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open || !bodyRef.current) return;
    // Style code blocks after render
    const codeBlocks = bodyRef.current.querySelectorAll('pre code, pre');
    codeBlocks.forEach((block) => {
      (block as HTMLElement).classList.add('artifact-code-block');
    });
  }, [open, artifact]);

  if (!artifact) return null;

  const date = new Date(artifact.creation_date * 1000);
  const year = date.getFullYear();
  const comment = getArchaeologicalComment(artifact.tags || [], year);
  const era = getEraLabel(artifact.creation_date);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[85vh] overflow-y-auto bg-card border-border">
        <DialogTitle className="sr-only">유물 상세</DialogTitle>
        
        {/* Era badge */}
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xs font-mono-code text-amber tracking-wide uppercase">
            {era}
          </span>
          <span className="text-xs text-muted-foreground">·</span>
          <span className="text-xs font-mono-code text-muted-foreground">
            {date.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' })}
          </span>
        </div>

        {/* Title */}
        <h2
          className="font-display text-2xl font-bold text-foreground mb-3 leading-tight"
          dangerouslySetInnerHTML={{ __html: artifact.title || 'Untitled Artifact' }}
        />

        {/* Tags */}
        {artifact.tags && (
          <div className="flex flex-wrap gap-1.5 mb-4">
            {artifact.tags.map((tag) => (
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

        {/* Archaeological comment */}
        <div className="bg-amber/10 border border-amber/20 rounded p-3 mb-5">
          <p className="text-sm text-foreground/80 italic font-display">
            🏺 "{comment}"
          </p>
        </div>

        {/* Full body with code highlighting */}
        <div
          ref={bodyRef}
          className="artifact-body prose prose-sm max-w-none"
          dangerouslySetInnerHTML={{ __html: artifact.body }}
        />

        {/* Footer meta */}
        <div className="flex items-center justify-between text-xs text-muted-foreground mt-6 pt-4 border-t border-border">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5" />
              {date.toLocaleDateString('ko-KR')}
            </span>
            <span className="flex items-center gap-1">
              <ThumbsUp className="w-3.5 h-3.5" />
              {artifact.score}점
            </span>
            <span className="flex items-center gap-1">
              <User className="w-3.5 h-3.5" />
              {artifact.owner.display_name}
              {artifact.owner.reputation && (
                <span className="text-amber ml-1">({artifact.owner.reputation.toLocaleString()} rep)</span>
              )}
            </span>
          </div>
          {artifact.link && (
            <a
              href={artifact.link}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-primary hover:text-accent transition-colors"
            >
              Stack Overflow에서 보기 <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ArtifactModal;
