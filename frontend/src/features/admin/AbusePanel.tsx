import { useEffect, useState } from "react";
import { ShieldCheck } from "lucide-react";
import { requestJson } from "@/api/client";
import type { AbuseBlock } from "@/api/types";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function AbusePanel({ token }: { token: string }) {
  const [blocks, setBlocks] = useState<AbuseBlock[]>([]);
  const [error, setError] = useState("");

  async function load() {
    try {
      const data = await requestJson<{ blocks: AbuseBlock[] }>("/api/admin/abuse/blocks", {}, token);
      setBlocks(data.blocks); setError("");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "목록을 불러오지 못했습니다."); }
  }
  useEffect(() => { void load(); }, []);

  async function revoke(id: string) {
    await requestJson(`/api/admin/abuse/blocks/${id}`, { method: "DELETE" }, token);
    await load();
  }

  return <section className="grid gap-4">
    <Alert><ShieldCheck /><AlertTitle>개인정보 보호형 이용 제한</AlertTitle><AlertDescription>원 IP는 저장하지 않습니다. salted hash의 앞 12자리 fingerprint와 관리자 사유·메모만 감사 기록으로 보존합니다. 대규모 공격은 Cloudflare WAF에서 별도로 차단하세요.</AlertDescription></Alert>
    <Card><CardHeader className="flex-row items-center justify-between"><CardTitle>이용 제한 기록</CardTitle><Button variant="outline" onClick={load}>새로고침</Button></CardHeader><CardContent className="grid gap-3">
      {error && <p className="text-destructive text-sm">{error}</p>}
      {blocks.length === 0 ? <p className="text-muted-foreground text-sm">차단 기록이 없습니다.</p> : blocks.map((block) => <article className="rounded-lg border p-4" key={block.id}>
        <div className="flex flex-wrap items-center justify-between gap-2"><strong>{block.reason}</strong><Badge variant={block.active ? "destructive" : "secondary"}>{block.active ? "적용 중" : "해제/만료"}</Badge></div>
        <p className="text-muted-foreground mt-2 text-sm">fingerprint {block.identity_fingerprint ?? "대화 전용"} · {block.blocked_until ?? "영구"}</p>
        {block.note && <p className="mt-2 text-sm">{block.note}</p>}
        {block.active && <Button className="mt-3" size="sm" variant="outline" onClick={() => revoke(block.id)}>차단 해제</Button>}
      </article>)}
    </CardContent></Card>
  </section>;
}
