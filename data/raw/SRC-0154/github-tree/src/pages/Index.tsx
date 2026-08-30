import { useState } from "react";
import { CertificateForm } from "@/components/CertificateForm";
import { Certificate } from "@/components/Certificate";

export interface CertificateData {
  name: string;
  os: string;
  nodeVersion: string;
  date: string;
  description: string;
}

const Index = () => {
  const [certData, setCertData] = useState<CertificateData | null>(null);
  const [showStamp, setShowStamp] = useState(false);

  const handleGenerate = (data: CertificateData) => {
    setCertData(data);
    setShowStamp(false);
    setTimeout(() => setShowStamp(true), 400);
  };

  const handleReset = () => {
    setCertData(null);
    setShowStamp(false);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border py-6 text-center">
        <h1 className="font-display text-4xl font-bold tracking-tight text-foreground md:text-5xl">
          WorksOnMine
        </h1>
        <p className="mt-2 text-lg text-muted-foreground">
          "제 컴퓨터에선 되는데요"를 공식 증명서로 발급합니다
        </p>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-10">
        {!certData ? (
          <CertificateForm onGenerate={handleGenerate} />
        ) : (
          <Certificate
            data={certData}
            showStamp={showStamp}
            onReset={handleReset}
          />
        )}
      </main>

      <footer className="border-t border-border py-6 text-center text-sm text-muted-foreground">
        <p>본 증명서는 법적 효력이 없으며, 순전히 개발자의 자존심을 위한 것입니다.</p>
      </footer>
    </div>
  );
};

export default Index;
