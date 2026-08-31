import { FormEvent, useEffect, useRef, useState } from "react";
import { streamChat } from "../api/client";
import type { ConversationMessage, SourceReference } from "../api/types";
import "../styles/chat.css";

const prompts = [
  "최근에 가장 집중하고 있는 일은 무엇인가요?",
  "대표 프로젝트와 맡은 역할을 소개해 주세요.",
  "어떤 개발자로 성장하고 싶으신가요?",
];

export function ChatPage() {
  const [conversationId, setConversationId] = useState<string>();
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [pending, setPending] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const bottom = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, pending]);

  async function send(event: FormEvent) {
    event.preventDefault();
    const message = draft.trim();
    if (!message || pending) return;
    setDraft("");
    setPending(true);
    setMessages((current) => [...current, { role: "user", content: message, sources: [] }]);
    try {
      let sources: SourceReference[] = [];
      setMessages((current) => [...current, { role: "assistant", content: "", sources: [] }]);
      await streamChat({ message, conversation_id: conversationId }, (eventName, raw) => {
        if (eventName === "conversation") setConversationId((raw as { conversation_id: string }).conversation_id);
        if (eventName === "sources") sources = raw as SourceReference[];
        if (eventName === "token") setMessages((current) => current.map((item, index) => index === current.length - 1 ? { ...item, content: item.content + (raw as { text: string }).text, sources } : item));
        if (eventName === "error") throw new Error((raw as { message: string }).message);
      });
    } catch (error) {
      setMessages((current) => current.map((item, index) => index === current.length - 1 && item.role === "assistant" && !item.content ? { ...item, content: error instanceof Error ? error.message : "답변에 실패했습니다." } : item));
    } finally {
      setPending(false);
    }
  }

  function reset() {
    setConversationId(undefined);
    setMessages([]);
    setMenuOpen(false);
  }

  return (
    <div className="messenger-shell">
      <aside className={menuOpen ? "sidebar open" : "sidebar"}>
        <div className="brand"><strong>Oh My Persona</strong><button onClick={() => setMenuOpen(false)}>×</button></div>
        <button className="new-chat" onClick={reset}>＋ 새 대화 시작</button>
        <div className="contact"><span className="avatar">김</span><div><strong>김신건</strong><small>백엔드 개발자 · 온라인</small></div></div>
        <p className="side-label">추천 질문</p>
        {prompts.map((prompt) => <button className="side-prompt" key={prompt} onClick={() => { setDraft(prompt); setMenuOpen(false); }}>{prompt}</button>)}
        <a className="admin-link" href="/admin">관리 콘솔</a>
      </aside>
      {menuOpen && <button className="backdrop" aria-label="메뉴 닫기" onClick={() => setMenuOpen(false)} />}
      <main className="chat-main">
        <header className="chat-header"><button className="menu-button" onClick={() => setMenuOpen(true)}>☰</button><span className="avatar">김</span><div><strong>김신건</strong><small>궁금한 내용을 편하게 물어보세요</small></div></header>
        <section className="message-list">
          <article className="message assistant"><span className="avatar small">김</span><div><strong>김신건</strong><div className="bubble">안녕하세요. 백엔드 개발자 김신건입니다. 제가 해온 일과 기술적 판단이 궁금하시다면 편하게 물어봐 주세요.</div></div></article>
          {messages.map((message, index) => <Message key={`${index}-${message.created_at ?? "now"}`} message={message} />)}
          {pending && <div className="typing">김신건이 답변하고 있습니다…</div>}
          <div ref={bottom} />
        </section>
        <form className="composer" onSubmit={send}><textarea value={draft} onChange={(event) => setDraft(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }} placeholder="메시지를 입력하세요" /><button disabled={pending}>전송</button></form>
      </main>
    </div>
  );
}

function Message({ message }: { message: ConversationMessage }) {
  const mine = message.role === "user";
  return <article className={`message ${mine ? "user" : "assistant"}`}>
    {!mine && <span className="avatar small">김</span>}
    <div><strong>{mine ? "나" : message.role === "owner" ? "김신건 · 직접 답변" : "김신건"}</strong><div className="bubble">{message.content}</div>
      {message.sources.length > 0 && <details><summary>답변 근거 {message.sources.length}개</summary>{message.sources.map((source, index) => source.url ? <a key={`${source.url}-${index}`} href={source.url} target="_blank" rel="noreferrer">{source.title ?? source.source_id ?? `출처 ${index + 1}`}</a> : null)}</details>}
    </div>
  </article>;
}
