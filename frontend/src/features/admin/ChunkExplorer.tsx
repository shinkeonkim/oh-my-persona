import { useEffect, useState } from "react";
import { requestJson } from "../../api/client";
import type { ChunkDetail } from "../../api/types";

interface ChunkPage { packaged: ChunkDetail[]; packaged_total: number; packaged_unfiltered_total: number; source_facets: { source_id: string; title?: string }[] }

export function ChunkExplorer({ token }: { token: string }) {
  const [items, setItems] = useState<ChunkDetail[]>([]), [detail, setDetail] = useState<ChunkDetail>();
  const [query, setQuery] = useState(""), [source, setSource] = useState(""), [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0), [all, setAll] = useState(0), [facets, setFacets] = useState<ChunkPage["source_facets"]>([]);
  const limit = 25;
  useEffect(() => { void load(); }, [offset, source]);
  async function load(reset = false) {
    const nextOffset = reset ? 0 : offset;
    if (reset) setOffset(0);
    const params = new URLSearchParams({ limit: "1", packaged_limit: String(limit), packaged_offset: String(nextOffset) });
    if (query.trim()) params.set("q", query.trim());
    if (source) params.set("source_id", source);
    const data = await requestJson<ChunkPage>(`/api/admin/knowledge?${params}`, {}, token);
    setItems(data.packaged); setTotal(data.packaged_total); setAll(data.packaged_unfiltered_total); setFacets(data.source_facets);
  }
  async function inspect(id: string) { setDetail(await requestJson<ChunkDetail>(`/api/admin/chunks/${encodeURIComponent(id)}`, {}, token)); }
  return <section className="admin-card chunk-explorer"><div className="title-row"><div><h2>검색 청크 탐색기</h2><p>검색 결과 {total.toLocaleString()}개 / 전체 {all.toLocaleString()}개</p></div><button className="secondary" onClick={() => load(true)}>검색</button></div>
    <div className="chunk-filters"><input type="search" value={query} onChange={(event) => setQuery(event.target.value)} onKeyDown={(event) => event.key === "Enter" && load(true)} placeholder="내용, 문서 ID, 경로 검색" /><select value={source} onChange={(event) => { setSource(event.target.value); setOffset(0); }}><option value="">모든 출처</option>{facets.map((item) => <option key={item.source_id} value={item.source_id}>{item.source_id} · {item.title ?? "제목 없음"}</option>)}</select></div>
    <div className="chunk-layout"><div><div className="admin-list chunk-list">{items.map((item) => <button className="admin-item chunk-button" key={item.id} onClick={() => inspect(item.id)}><h3>{item.title}</h3><p>{item.content}</p><small>{item.source_id} · {item.document_id}</small></button>)}</div><div className="pager"><button className="secondary" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - limit))}>이전</button><span>{total ? offset + 1 : 0}–{Math.min(offset + limit, total)} / {total}</span><button className="secondary" disabled={offset + limit >= total} onClick={() => setOffset(offset + limit)}>다음</button></div></div><ChunkDetailView item={detail} /></div>
  </section>;
}

function ChunkDetailView({ item }: { item?: ChunkDetail }) {
  if (!item) return <div className="chunk-detail">청크를 선택하면 전체 내용과 출처 계보를 표시합니다.</div>;
  const fields = [["청크 ID", item.chunk_id], ["문서 ID", item.document_id], ["출처 ID", item.source_id], ["원본 경로", item.source_path], ["관측일", item.observed_at], ["SHA-256", item.content_sha256]];
  return <div className="chunk-detail">{item.source_url && <a href={item.source_url} target="_blank" rel="noreferrer">원본 출처 열기</a>}<dl>{fields.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value ?? "없음"}</dd></div>)}</dl><pre>{item.content}</pre></div>;
}
