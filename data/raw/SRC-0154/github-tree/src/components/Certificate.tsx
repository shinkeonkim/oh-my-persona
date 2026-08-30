import { useRef } from "react";
import html2canvas from "html2canvas";
import { Button } from "@/components/ui/button";
import { generateSerial } from "@/lib/serial";
import { StampSeal } from "@/components/StampSeal";
import type { CertificateData } from "@/pages/Index";

interface Props {
  data: CertificateData;
  showStamp: boolean;
  onReset: () => void;
}

export function Certificate({ data, showStamp, onReset }: Props) {
  const certRef = useRef<HTMLDivElement>(null);
  const serial = generateSerial(data.name, data.os, data.date);

  const handleExport = async () => {
    if (!certRef.current) return;
    const canvas = await html2canvas(certRef.current, {
      scale: 2,
      backgroundColor: null,
      useCORS: true,
    });
    const link = document.createElement("a");
    link.download = `WorksOnMine-${serial}.png`;
    link.href = canvas.toDataURL("image/png");
    link.click();
  };

  return (
    <div className="space-y-6">
      {/* Action buttons */}
      <div className="flex justify-center gap-4">
        <Button onClick={handleExport} size="lg" className="font-display font-bold tracking-wide">
          📥 이미지로 내보내기
        </Button>
        <Button onClick={onReset} variant="outline" size="lg" className="font-display">
          🔄 새로 발급
        </Button>
      </div>

      {/* Certificate */}
      <div className="flex justify-center">
        <div
          ref={certRef}
          className="certificate-border parchment-bg relative w-full max-w-2xl p-10 md:p-14"
        >
          {/* Watermark */}
          <div className="watermark">
            <span className="watermark-text">CERTIFIED</span>
          </div>

          {/* Content */}
          <div className="relative z-10 space-y-8 text-center">
            {/* Title */}
            <div>
              <p className="font-mono text-xs tracking-widest text-certificate-gold-dark uppercase">
                Certificate of Verification
              </p>
              <h2 className="font-display text-3xl font-black tracking-tight text-ink md:text-4xl mt-2">
                정상 작동 확인서
              </h2>
              <p className="font-display text-base text-muted-foreground mt-1 italic">
                "It Works on My Machine"
              </p>
            </div>

            {/* Divider */}
            <div className="flex items-center justify-center gap-3">
              <div className="h-px flex-1 bg-certificate-gold-dark/30" />
              <span className="text-certificate-gold-dark text-lg">◆</span>
              <div className="h-px flex-1 bg-certificate-gold-dark/30" />
            </div>

            {/* Body */}
            <div className="space-y-4 font-body text-lg text-ink leading-relaxed">
              <p>
                본 확인서는 <strong className="font-bold underline decoration-certificate-gold decoration-2 underline-offset-4">{data.name}</strong> 이(가)
              </p>
              <p>
                <span className="font-mono text-base bg-secondary/50 px-2 py-1 rounded">{data.os}</span>
                {" "}환경,{" "}
                <span className="font-mono text-base bg-secondary/50 px-2 py-1 rounded">Node {data.nodeVersion}</span>
                {" "}에서
              </p>
              <p>
                <strong>{data.date}</strong> 일자에
              </p>
              <p className="font-mono text-sm bg-secondary/60 inline-block px-4 py-2 rounded-md">
                "{data.description}"
              </p>
              <p>
                위 사실을 확인하였음을 증명합니다.
              </p>
            </div>

            {/* Stamp area */}
            <div className="relative flex items-center justify-center h-40 mt-6">
              {showStamp && (
                <StampSeal className="animate-stamp-slam h-36 w-36 opacity-90 drop-shadow-md" />
              )}
            </div>

            {/* Footer info */}
            <div className="flex items-end justify-between border-t border-certificate-gold-dark/20 pt-4">
              <div className="text-left">
                <p className="font-mono text-[10px] text-muted-foreground tracking-wider">SERIAL NO.</p>
                <p className="font-mono text-xs text-ink font-semibold">{serial}</p>
              </div>
              <div className="text-center">
                <p className="font-display text-sm font-bold text-ink">WorksOnMine™</p>
                <p className="font-mono text-[10px] text-muted-foreground">Certified Developer Authority</p>
              </div>
              <div className="text-right">
                <p className="font-mono text-[10px] text-muted-foreground tracking-wider">ISSUED</p>
                <p className="font-mono text-xs text-ink font-semibold">{data.date}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
