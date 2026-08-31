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
  const data = await api("/api/admin/knowledge?limit=100");
  document.querySelector("#knowledge-summary").textContent =
    `관리 지식 ${data.managed.length}개 · 패키지 청크 ${data.packaged_total.toLocaleString()}개`;
  const list = document.querySelector("#knowledge-list");
  list.replaceChildren(
    ...data.managed.map((item) => knowledgeNode(item, true)),
  );
  const packaged = document.querySelector("#packaged-list");
  packaged.replaceChildren(
    ...data.packaged.map((item) => knowledgeNode(item, false)),
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
