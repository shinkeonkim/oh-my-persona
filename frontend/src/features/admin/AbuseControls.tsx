import { FormEvent, useState } from "react";
import { ShieldAlert } from "lucide-react";
import { requestJson } from "@/api/client";
import type { AbuseBlock, AbuseStatus } from "@/api/types";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

interface Props {
  conversationId: string;
  status: AbuseStatus;
  token: string;
  onChanged: () => Promise<void>;
}

export function AbuseControls({ conversationId, status, token, onChanged }: Props) {
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function block(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setBusy(true);
    setError("");
    try {
      await requestJson<AbuseBlock>(`/api/admin/conversations/${conversationId}/blocks`, {
        method: "POST", body: JSON.stringify(Object.fromEntries(data)),
      }, token);
      await onChanged();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "차단하지 못했습니다.");
    } finally { setBusy(false); }
  }

  async function unblock() {
    if (!status.block) return;
    setBusy(true);
    try {
      await requestJson(`/api/admin/abuse/blocks/${status.block.id}`, { method: "DELETE" }, token);
      await onChanged();
    } finally { setBusy(false); }
  }

  return <Card className={status.blocked ? "border-destructive/50" : ""}>
    <CardHeader className="flex-row items-center justify-between">
      <div><CardTitle className="text-base">사용자 보호 및 이용 제한</CardTitle><p className="text-muted-foreground mt-1 text-xs">비식별 fingerprint: {status.identity_fingerprint ?? "기록 없음"}</p></div>
      <Badge variant={status.blocked ? "destructive" : "secondary"}>{status.blocked ? "차단됨" : "정상"}</Badge>
    </CardHeader>
    <CardContent>
      {status.blocked && status.block ? <Alert variant="destructive"><ShieldAlert /><AlertTitle>{status.block.reason}</AlertTitle><AlertDescription>{status.block.blocked_until ?? "영구 차단"}{status.block.note && ` · ${status.block.note}`}<Button className="mt-3" size="sm" variant="outline" disabled={busy} onClick={unblock}>차단 해제</Button></AlertDescription></Alert> :
      <form className="grid gap-3" onSubmit={block}>
        <div className="grid grid-cols-2 gap-2"><select className="h-9 rounded-md border px-3 text-sm" name="scope" defaultValue="identity"><option value="identity">사용자 전체 차단</option><option value="conversation">현재 대화만 차단</option></select><select className="h-9 rounded-md border px-3 text-sm" name="duration" defaultValue="24h"><option value="24h">24시간</option><option value="7d">7일</option><option value="permanent">영구</option></select></div>
        <Input name="reason" required minLength={3} placeholder="차단 사유" />
        <Textarea name="note" rows={2} placeholder="감사 메모(선택)" />
        <Button variant="destructive" disabled={busy}><ShieldAlert />{busy ? "처리 중…" : "이용 제한 적용"}</Button>
      </form>}
      {error && <p className="text-destructive mt-2 text-sm">{error}</p>}
    </CardContent>
  </Card>;
}
