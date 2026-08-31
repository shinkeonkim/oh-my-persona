import { FormEvent, useEffect, useState } from "react";
import { requestJson } from "../api/client";
import { ChunkExplorer } from "../features/admin/ChunkExplorer";
import { ConversationsPanel } from "../features/admin/ConversationsPanel";
import { GapsPanel } from "../features/admin/GapsPanel";
import { KnowledgePanel } from "../features/admin/KnowledgePanel";
import "../styles/admin.css";

type Tab = "knowledge" | "gaps" | "conversations";

export function AdminPage() {
  const [token, setToken] = useState(() => sessionStorage.getItem("personaAdminToken") ?? "");
  const [authenticated, setAuthenticated] = useState(false);
  const [error, setError] = useState("");
  const [tab, setTab] = useState<Tab>("knowledge");

  useEffect(() => {
    if (token) authenticate(token);
  }, []);

  async function authenticate(value: string) {
    try {
      await requestJson("/api/admin/knowledge?limit=1&packaged_limit=1", {}, value);
      sessionStorage.setItem("personaAdminToken", value);
      setToken(value);
      setAuthenticated(true);
      setError("");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "인증에 실패했습니다.");
    }
  }

  function login(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    authenticate(String(data.get("token") ?? ""));
  }

  if (!authenticated) return <main className="admin-shell"><section className="admin-card login-card"><h1>Persona Admin</h1><p>관리자 토큰은 현재 탭에만 저장됩니다.</p><form onSubmit={login}><input name="token" type="password" required placeholder="관리자 토큰" defaultValue={token} /><button>접속</button></form>{error && <p className="error">{error}</p>}</section></main>;

  return <main className="admin-shell">
    <header className="admin-header"><div><small>OH MY PERSONA</small><h1>관리 콘솔</h1></div><button className="secondary" onClick={() => { sessionStorage.removeItem("personaAdminToken"); location.reload(); }}>로그아웃</button></header>
    <nav className="admin-tabs">{(["knowledge", "gaps", "conversations"] as Tab[]).map((item) => <button key={item} className={tab === item ? "active" : ""} onClick={() => setTab(item)}>{item === "knowledge" ? "지식 데이터" : item === "gaps" ? "지식 공백" : "대화 기록"}</button>)}</nav>
    {tab === "knowledge" && <><KnowledgePanel token={token} /><ChunkExplorer token={token} /></>}
    {tab === "gaps" && <GapsPanel token={token} />}
    {tab === "conversations" && <ConversationsPanel token={token} />}
  </main>;
}
