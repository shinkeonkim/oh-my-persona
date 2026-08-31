import { FormEvent, useEffect, useState } from "react";
import { requestJson } from "../../api/client";
import type { GapQuestion } from "../../api/types";

export function GapsPanel({ token }: { token: string }) {
  const [questions, setQuestions] = useState<GapQuestion[]>([]);
  const [selected, setSelected] = useState<GapQuestion>();
  const [filter, setFilter] = useState("all");

  useEffect(() => { void load(); }, []);
  async function load() {
    const data = await requestJson<{ questions: GapQuestion[] }>("/api/admin/knowledge-gaps", {}, token);
    setQuestions(data.questions);
  }
  async function create(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget, data = new FormData(form);
    await requestJson("/api/admin/knowledge-gaps/questions", { method: "POST", body: JSON.stringify({
      question: data.get("question"), category: data.get("category"), time_scope: data.get("time_scope"),
    }) }, token);
    form.reset(); await load();
  }
  async function answer(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!selected) return;
    const form = event.currentTarget, data = new FormData(form);
    await requestJson(`/api/admin/knowledge-gaps/${selected.question_id}/answer`, { method: "POST", body: JSON.stringify({
      answer: data.get("answer"), answered_at: data.get("answered_at"), visibility: data.get("visibility"),
      evidence_urls: String(data.get("evidence_urls") ?? "").split(/\s+/).filter(Boolean),
    }) }, token);
    setSelected(undefined); await load();
  }
  async function remove(question: GapQuestion) {
    if (!question.custom || !confirm("이 질문을 삭제할까요?")) return;
    await requestJson(`/api/admin/knowledge-gaps/questions/${question.question_id}`, { method: "DELETE" }, token);
    await load();
  }
  const visible = questions.filter((item) => filter === "all" || item.status === filter);
  return <section className="admin-grid gaps-grid">
    <div className="admin-card"><h2>빈 지식 질문 생성</h2><p>자료에 없는 경험과 판단을 질문으로 만들고 직접 답변해 지식으로 전환합니다.</p><form onSubmit={create}>
      <label>질문<textarea name="question" required minLength={3} rows={3} /></label><label>분류<input name="category" required placeholder="예: 프로젝트" /></label><label>시점<input name="time_scope" required placeholder="예: 2024년" /></label><button>질문 생성</button>
    </form></div>
    <div className="admin-card"><div className="title-row"><h2>지식 공백 {visible.length}개</h2><select value={filter} onChange={(e) => setFilter(e.target.value)}><option value="all">전체</option><option value="empty">미답변</option><option value="direct_answer">공개 답변</option><option value="draft_answer">비공개 답변</option></select></div><div className="admin-list">
      {visible.map((item) => <article className="admin-item" key={item.question_id}><small>{item.category} · {item.time_scope} · {item.status}</small><h3>{item.question}</h3><p>{item.answer_hint}</p><div className="actions"><button onClick={() => setSelected(item)}>답변하기</button>{item.custom && <button className="danger" onClick={() => remove(item)}>삭제</button>}</div></article>)}
    </div></div>
    {selected && <form className="admin-card gap-answer" onSubmit={answer}><div className="title-row"><h2>답변 작성</h2><button type="button" className="secondary" onClick={() => setSelected(undefined)}>닫기</button></div><h3>{selected.question}</h3><label>답변<textarea name="answer" required rows={10} /></label><label>답변일<input name="answered_at" type="date" required defaultValue={new Date().toISOString().slice(0, 10)} /></label><label>공개 범위<select name="visibility"><option value="public">챗봇에 공개</option><option value="private">비공개 초안</option></select></label><label>근거 URL (공백 구분)<textarea name="evidence_urls" rows={3} /></label><button>지식으로 저장</button></form>}
  </section>;
}
