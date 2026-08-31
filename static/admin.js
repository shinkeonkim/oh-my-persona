const login = document.querySelector("#login"),
  dashboard = document.querySelector("#dashboard");
let token = sessionStorage.getItem("personaAdminToken") || "";
const headers = () => ({
  authorization: `Bearer ${token}`,
  "content-type": "application/json",
});
async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { ...headers(), ...(options.headers || {}) },
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || `HTTP ${response.status}`);
  }
  return response.status === 204 ? null : response.json();
}
async function enter() {
  try {
    await api("/api/admin/knowledge?limit=1");
    login.hidden = true;
    dashboard.hidden = false;
    sessionStorage.setItem("personaAdminToken", token);
    await Promise.all([
      loadKnowledge(),
      loadChunks(),
      loadKnowledgeGaps(),
      loadConversations(),
    ]);
  } catch (error) {
    document.querySelector("#login-error").textContent = error.message;
  }
}
document.querySelector("#login-form").addEventListener("submit", (event) => {
  event.preventDefault();
  token = document.querySelector("#token").value;
  enter();
});
document.querySelector("#logout").onclick = () => {
  sessionStorage.removeItem("personaAdminToken");
  location.reload();
};
document.querySelectorAll("nav button").forEach(
  (button) =>
    (button.onclick = () => {
      document
        .querySelectorAll("nav button")
        .forEach((item) => item.classList.toggle("active", item === button));
      document
        .querySelectorAll(".tab")
        .forEach((tab) => (tab.hidden = tab.id !== button.dataset.tab));
    }),
);
const form = document.querySelector("#knowledge-form");
function resetForm() {
  form.reset();
  document.querySelector("#knowledge-id").value = "";
}
document.querySelector("#reset").onclick = resetForm;
async function loadKnowledge() {
  const data = await api("/api/admin/knowledge?limit=100&packaged_limit=1");
  document.querySelector("#knowledge-summary").textContent =
    `관리 지식 ${data.managed.length}개 · 전체 검색 청크 ${data.packaged_unfiltered_total.toLocaleString()}개`;
  const list = document.querySelector("#knowledge-list");
  list.replaceChildren(
    ...data.managed.map((item) => knowledgeNode(item, true)),
  );
}
function knowledgeNode(item, managed) {
  const node = document.createElement("article");
  node.className = "item";
  node.innerHTML = `<h3></h3><p></p><p></p>`;
  node.querySelector("h3").textContent = item.title;
  node.querySelectorAll("p")[0].textContent = item.content;
  node.querySelectorAll("p")[1].textContent =
    `${item.status} · ${item.observed_at || "날짜 미상"}`;
  if (managed) {
    const actions = document.createElement("div");
    actions.className = "item-actions";
    const edit = document.createElement("button");
    edit.textContent = "수정";
    edit.onclick = () => {
      document.querySelector("#knowledge-id").value = item.id;
      document.querySelector("#title").value = item.title;
      document.querySelector("#source-url").value = item.source_url;
      document.querySelector("#observed-at").value = item.observed_at || "";
      document.querySelector("#status").value = item.status;
      document.querySelector("#content").value = item.content;
    };
    const remove = document.createElement("button");
    remove.className = "danger";
    remove.textContent = "삭제";
    remove.onclick = async () => {
      if (confirm("이 관리 지식을 삭제할까요?")) {
        await api(`/api/admin/knowledge/${item.id}`, { method: "DELETE" });
        loadKnowledge();
      }
    };
    actions.append(edit, remove);
    node.append(actions);
  }
  return node;
}
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const id = document.querySelector("#knowledge-id").value,
    payload = {
      title: document.querySelector("#title").value,
      source_url: document.querySelector("#source-url").value,
      observed_at: document.querySelector("#observed-at").value || null,
      status: document.querySelector("#status").value,
      content: document.querySelector("#content").value,
    };
  await api(id ? `/api/admin/knowledge/${id}` : "/api/admin/knowledge", {
    method: id ? "PUT" : "POST",
    body: JSON.stringify(payload),
  });
  resetForm();
  loadKnowledge();
});
document.querySelector("#reload-knowledge").onclick = loadKnowledge;
const chunkState = { offset: 0, limit: 25, total: 0 };
async function loadChunks(reset = false) {
  if (reset) chunkState.offset = 0;
  const params = new URLSearchParams({
      limit: "1",
      packaged_limit: String(chunkState.limit),
      packaged_offset: String(chunkState.offset),
    }),
    query = document.querySelector("#chunk-query").value.trim(),
    source = document.querySelector("#chunk-source").value;
  if (query) params.set("q", query);
  if (source) params.set("source_id", source);
  const data = await api(`/api/admin/knowledge?${params}`);
  chunkState.total = data.packaged_total;
  const sourceSelect = document.querySelector("#chunk-source");
  if (sourceSelect.options.length === 1) {
    sourceSelect.append(
      ...data.source_facets.map((item) => {
        const option = document.createElement("option");
        option.value = item.source_id;
        option.textContent = `${item.source_id} · ${item.title || "제목 없음"}`;
        return option;
      }),
    );
  }
  document.querySelector("#chunk-summary").textContent =
    `검색 결과 ${data.packaged_total.toLocaleString()}개 / 전체 ${data.packaged_unfiltered_total.toLocaleString()}개`;
  document.querySelector("#packaged-list").replaceChildren(
    ...data.packaged.map((item) => {
      const node = knowledgeNode(item, false);
      node.querySelectorAll("p")[1].textContent =
        `${item.source_id || "출처 없음"} · ${item.document_id || "문서 없음"} · ${item.observed_at || "날짜 미상"}`;
      node.onclick = () => showChunkDetail(item.id);
      return node;
    }),
  );
  const first = chunkState.total ? chunkState.offset + 1 : 0,
    last = Math.min(chunkState.offset + chunkState.limit, chunkState.total);
  document.querySelector("#chunk-page").textContent =
    `${first}–${last} / ${chunkState.total}`;
  document.querySelector("#chunk-prev").disabled = chunkState.offset === 0;
  document.querySelector("#chunk-next").disabled = last >= chunkState.total;
}
async function showChunkDetail(chunkId) {
  const item = await api(`/api/admin/chunks/${encodeURIComponent(chunkId)}`),
    detail = document.querySelector("#chunk-detail");
  detail.replaceChildren();
  const metadata = document.createElement("dl");
  for (const [label, value] of [
    ["청크 ID", item.chunk_id],
    ["문서 ID", item.document_id],
    ["출처 ID", item.source_id],
    ["원본 경로", item.source_path],
    ["순번", item.ordinal],
    ["관측일", item.observed_at],
    ["게시일", item.published_at],
    ["SHA-256", item.content_sha256],
  ]) {
    const term = document.createElement("dt"),
      description = document.createElement("dd");
    term.textContent = label;
    description.textContent = value ?? "없음";
    metadata.append(term, description);
  }
  const content = document.createElement("pre");
  content.textContent = item.content;
  detail.append(metadata, content);
  if (item.source_url) {
    const link = document.createElement("a");
    link.href = item.source_url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = "원본 출처 열기";
    detail.prepend(link);
  }
}
document.querySelector("#reload-chunks").onclick = () => loadChunks(true);
document.querySelector("#chunk-query").addEventListener("keydown", (event) => {
  if (event.key === "Enter") loadChunks(true);
});
document.querySelector("#chunk-source").onchange = () => loadChunks(true);
document.querySelector("#chunk-prev").onclick = () => {
  chunkState.offset = Math.max(0, chunkState.offset - chunkState.limit);
  loadChunks();
};
document.querySelector("#chunk-next").onclick = () => {
  chunkState.offset += chunkState.limit;
  loadChunks();
};
let gapQuestions = [];
async function loadKnowledgeGaps() {
  const data = await api("/api/admin/knowledge-gaps");
  gapQuestions = data.questions;
  document.querySelector("#gap-summary").textContent = Object.entries(
    data.summary,
  )
    .map(([status, count]) => `${status} ${count}`)
    .join(" · ");
  document.querySelector("#gap-list").replaceChildren(
    ...gapQuestions.map((item) => {
      const node = document.createElement("article");
      node.className = `item gap-item ${item.status}`;
      node.innerHTML = '<h3></h3><p></p><span class="badge"></span>';
      node.querySelector("h3").textContent = item.question;
      node.querySelector("p").textContent =
        `${item.category} · 근거 출처 ${item.unique_source_count}개`;
      node.querySelector(".badge").textContent = item.status;
      node.onclick = () => selectKnowledgeGap(item);
      return node;
    }),
  );
}
function selectKnowledgeGap(item) {
  const form = document.querySelector("#gap-answer-form"),
    managed = item.managed_answer;
  form.hidden = false;
  document.querySelector("#gap-question-id").value = item.question_id;
  document.querySelector("#gap-category").textContent =
    `${item.question_id} · ${item.category}`;
  document.querySelector("#gap-question").textContent = item.question;
  document.querySelector("#gap-hint").textContent = item.answer_hint;
  document.querySelector("#gap-answered-at").value =
    managed?.observed_at || new Date().toISOString().slice(0, 10);
  document.querySelector("#gap-visibility").value =
    managed?.status === "active" ? "public" : "private";
  document.querySelector("#gap-answer").value = managed
    ? extractGapAnswer(managed.content)
    : "";
  document.querySelector("#gap-evidence-urls").value =
    item.evidence_urls.join("\n");
  const remove = document.querySelector("#delete-gap-question");
  remove.hidden = !item.custom;
  remove.dataset.questionId = item.custom ? item.question_id : "";
  const evidence = document.querySelector("#gap-evidence");
  evidence.replaceChildren(
    ...item.evidence_urls.map((url) => {
      const link = document.createElement("a");
      link.href = url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = url;
      return link;
    }),
  );
}
function extractGapAnswer(content) {
  return content.match(/답변: ([\s\S]*?)\n\n참고 URL:/)?.[1] || content;
}
document
  .querySelector("#gap-answer-form")
  .addEventListener("submit", async (event) => {
    event.preventDefault();
    const questionId = document.querySelector("#gap-question-id").value,
      status = document.querySelector("#gap-save-status"),
      evidenceUrls = document
        .querySelector("#gap-evidence-urls")
        .value.split("\n")
        .map((url) => url.trim())
        .filter(Boolean);
    status.textContent = "저장 중…";
    try {
      await api(`/api/admin/knowledge-gaps/${questionId}/answer`, {
        method: "POST",
        body: JSON.stringify({
          answer: document.querySelector("#gap-answer").value,
          answered_at: document.querySelector("#gap-answered-at").value,
          visibility: document.querySelector("#gap-visibility").value,
          evidence_urls: evidenceUrls,
        }),
      });
      status.textContent = "저장했습니다.";
      await Promise.all([loadKnowledgeGaps(), loadKnowledge()]);
    } catch (error) {
      status.textContent = error.message;
    }
  });
document.querySelector("#reload-gaps").onclick = loadKnowledgeGaps;
document
  .querySelector("#gap-question-form")
  .addEventListener("submit", async (event) => {
    event.preventDefault();
    const status = document.querySelector("#gap-question-status");
    status.textContent = "생성 중…";
    try {
      await api("/api/admin/knowledge-gaps/questions", {
        method: "POST",
        body: JSON.stringify({
          question: document.querySelector("#new-gap-question").value,
          category: document.querySelector("#new-gap-category").value,
          time_scope: document.querySelector("#new-gap-time-scope").value,
        }),
      });
      event.currentTarget.reset();
      status.textContent = "질문을 생성했습니다.";
      await loadKnowledgeGaps();
    } catch (error) {
      status.textContent = error.message;
    }
  });
document.querySelector("#delete-gap-question").onclick = async (event) => {
  const questionId = event.currentTarget.dataset.questionId;
  if (
    !questionId ||
    !confirm("이 질문을 삭제할까요? 작성한 답변은 관리 지식에 남습니다.")
  )
    return;
  await api(
    `/api/admin/knowledge-gaps/questions/${encodeURIComponent(questionId)}`,
    { method: "DELETE" },
  );
  document.querySelector("#gap-answer-form").hidden = true;
  await loadKnowledgeGaps();
};
async function loadConversations() {
  const data = await api("/api/admin/conversations?limit=100");
  const list = document.querySelector("#conversation-list");
  list.replaceChildren(
    ...data.conversations.map((item) => {
      const node = document.createElement("article");
      node.className = "item";
      node.innerHTML = "<h3></h3><p></p>";
      node.querySelector("h3").textContent = item.preview || "(메시지 없음)";
      node.querySelector("p").textContent =
        `${item.message_count}개 메시지 · ${item.updated_at || ""}`;
      node.onclick = () => showConversation(item.id);
      return node;
    }),
  );
}
async function showConversation(id) {
  const data = await api(`/api/admin/conversations/${id}`),
    detail = document.querySelector("#conversation-detail");
  detail.replaceChildren(
    ...data.messages.map((item) => {
      const node = document.createElement("article");
      node.className = item.role;
      const label =
        item.role === "user"
          ? "사용자"
          : item.role === "owner"
            ? "김신건 · 직접 답변"
            : "김신건 AI";
      node.textContent = `${label}: ${item.content}`;
      return node;
    }),
  );
  document.querySelector("#conversation-id").value = id;
  document.querySelector("#conversation-reply-form").hidden = false;
  document.querySelector("#conversation-reply-status").textContent = "";
}
document
  .querySelector("#conversation-reply-form")
  .addEventListener("submit", async (event) => {
    event.preventDefault();
    const id = document.querySelector("#conversation-id").value,
      reply = document.querySelector("#conversation-reply"),
      status = document.querySelector("#conversation-reply-status");
    status.textContent = "전송 중…";
    try {
      await api(`/api/admin/conversations/${id}/messages`, {
        method: "POST",
        body: JSON.stringify({ content: reply.value }),
      });
      reply.value = "";
      status.textContent = "전달했습니다.";
      await Promise.all([showConversation(id), loadConversations()]);
    } catch (error) {
      status.textContent = error.message;
    }
  });
document.querySelector("#reload-conversations").onclick = loadConversations;
if (token) enter();
