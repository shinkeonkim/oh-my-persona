import { FormEvent, useEffect, useState } from "react";
import { requestJson } from "../../api/client";
import type { KnowledgeItem } from "../../api/types";

export function KnowledgePanel({ token }: { token: string }) {
  const [items, setItems] = useState<KnowledgeItem[]>([]);
  const [editing, setEditing] = useState<KnowledgeItem>();
  useEffect(() => { void load(); }, []);

  async function load() {
    const data = await requestJson<{ managed: KnowledgeItem[] }>(
      "/api/admin/knowledge?limit=100&packaged_limit=1", {}, token,
    );
    setItems(data.managed);
  }

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget), payload = {
      title: String(data.get("title")), content: String(data.get("content")),
      source_url: String(data.get("source_url")),
      observed_at: String(data.get("observed_at")) || null,
      status: String(data.get("status")),
    };
    await requestJson(
      editing ? `/api/admin/knowledge/${editing.id}` : "/api/admin/knowledge",
      { method: editing ? "PUT" : "POST", body: JSON.stringify(payload) }, token,
    );
    setEditing(undefined);
    event.currentTarget.reset();
    await load();
  }

  async function remove(id: string) {
    if (!confirm("이 관리 지식을 삭제할까요?")) return;
    await requestJson(`/api/admin/knowledge/${id}`, { method: "DELETE" }, token);
    await load();
  }

  return <section className="admin-grid">
    <form className="admin-card" onSubmit={save} key={editing?.id ?? "new"}><h2>관리 지식</h2>
      <label>제목<input name="title" required maxLength={200} defaultValue={editing?.title} /></label>
      <label>근거 URL<input name="source_url" type="url" required defaultValue={editing?.source_url} /></label>
      <label>관측일<input name="observed_at" type="date" defaultValue={editing?.observed_at} /></label>
      <label>상태<select name="status" defaultValue={editing?.status ?? "active"}><option value="active">활성</option><option value="draft">초안</option></select></label>
      <label>내용<textarea name="content" required rows={10} defaultValue={editing?.content} /></label>
      <div className="actions"><button>저장</button><button type="button" className="secondary" onClick={() => setEditing(undefined)}>새로 작성</button></div>
    </form>
    <div className="admin-card"><div className="title-row"><h2>관리 지식 {items.length}개</h2><button className="secondary" onClick={load}>새로고침</button></div><div className="admin-list">{items.map((item) => <article className="admin-item" key={item.id}><h3>{item.title}</h3><p>{item.content}</p><small>{item.status} · {item.observed_at ?? "날짜 미상"}</small><div className="actions"><button onClick={() => setEditing(item)}>수정</button><button className="danger" onClick={() => remove(item.id)}>삭제</button></div></article>)}</div></div>
  </section>;
}
