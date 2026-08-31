import { FormEvent, useEffect, useState } from "react";
import { requestJson } from "../../api/client";
import type { ConversationMessage, ConversationSummary } from "../../api/types";

export function ConversationsPanel({ token }: { token: string }) {
  const [items, setItems] = useState<ConversationSummary[]>([]), [selected, setSelected] = useState<string>();
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  useEffect(() => { void load(); }, []);
  async function load() { const data = await requestJson<{ conversations: ConversationSummary[] }>("/api/admin/conversations", {}, token); setItems(data.conversations.filter((x) => x.message_count > 0)); }
  async function open(id: string) { const data = await requestJson<{ messages: ConversationMessage[] }>(`/api/admin/conversations/${id}`, {}, token); setSelected(id); setMessages(data.messages); }
  async function reply(event: FormEvent<HTMLFormElement>) { event.preventDefault(); if (!selected) return; const form = event.currentTarget, data = new FormData(form); await requestJson(`/api/admin/conversations/${selected}/messages`, { method: "POST", body: JSON.stringify({ content: data.get("content") }) }, token); form.reset(); await open(selected); }
  return <section className="admin-card"><div className="title-row"><h2>대화 기록</h2><button className="secondary" onClick={load}>새로고침</button></div>{items.length === 0 ? <p className="empty">메시지가 있는 대화가 없습니다.</p> : <div className="conversation-layout"><div className="admin-list conversation-list">{items.map((item) => <button className="admin-item" key={item.id} onClick={() => open(item.id)}><strong>{item.preview || "대화"}</strong><small>{item.message_count}개 메시지 · {item.updated_at}</small></button>)}</div><div className="transcript">{selected ? <>{messages.map((message, index) => <article className={`transcript-message ${message.role}`} key={index}><strong>{message.role === "user" ? "방문자" : "김신건"}</strong><p>{message.content}</p></article>)}<form onSubmit={reply}><textarea name="content" required rows={3} placeholder="김신건으로 직접 답변" /><button>대화에 개입</button></form></> : <p>대화를 선택하세요.</p>}</div></div>}</section>;
}
