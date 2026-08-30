import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { CertificateData } from "@/pages/Index";

interface Props {
  onGenerate: (data: CertificateData) => void;
}

export function CertificateForm({ onGenerate }: Props) {
  const [name, setName] = useState("");
  const [os, setOs] = useState("");
  const [nodeVersion, setNodeVersion] = useState("");
  const [date, setDate] = useState(new Date().toISOString().split("T")[0]);
  const [description, setDescription] = useState("npm run dev 실행 후 정상 작동 확인");

  const canSubmit = name.trim() && os.trim() && nodeVersion.trim() && date;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;
    onGenerate({
      name: name.trim(),
      os: os.trim(),
      nodeVersion: nodeVersion.trim(),
      date,
      description: description.trim(),
    });
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="mx-auto max-w-lg space-y-6 rounded-lg border border-border bg-card p-8 shadow-sm"
    >
      <div className="text-center">
        <h2 className="font-display text-2xl font-bold text-foreground">증명서 발급 신청</h2>
        <p className="mt-1 text-muted-foreground">아래 정보를 입력하여 정상 작동 확인서를 발급받으세요</p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="name" className="font-body text-base">신청인 성명</Label>
        <Input
          id="name"
          placeholder="홍길동"
          value={name}
          onChange={(e) => setName(e.target.value)}
          maxLength={50}
          className="font-mono"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="os" className="font-body text-base">운영체제</Label>
        <Input
          id="os"
          placeholder="예: macOS Tahoe 26, Windows 11, Ubuntu 24.04"
          value={os}
          onChange={(e) => setOs(e.target.value)}
          maxLength={60}
          className="font-mono"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="node" className="font-body text-base">Node.js 버전</Label>
        <Input
          id="node"
          placeholder="v20.11.0"
          value={nodeVersion}
          onChange={(e) => setNodeVersion(e.target.value)}
          maxLength={30}
          className="font-mono"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="date" className="font-body text-base">재현 날짜</Label>
        <Input
          id="date"
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="font-mono"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="desc" className="font-body text-base">확인 사항</Label>
        <Input
          id="desc"
          placeholder="npm run dev 실행 후 정상 작동 확인"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          maxLength={100}
          className="font-mono"
        />
      </div>

      <Button
        type="submit"
        disabled={!canSubmit}
        className="w-full font-display text-lg font-bold tracking-wide"
        size="lg"
      >
        🔏 증명서 발급
      </Button>
    </form>
  );
}

