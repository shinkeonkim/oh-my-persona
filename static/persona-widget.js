(() => {
  const STORAGE_KEY = "oh-my-persona-widget-session-v1";
  const DEFAULT_ENDPOINT = "https://persona.shinkeonkim.com";

  const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[char]);

  const renderText = (value) => escapeHtml(value)
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br>");

  class PersonaWidgetElement extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: "open" });
      this.endpoint = (this.getAttribute("endpoint") || DEFAULT_ENDPOINT).replace(/\/$/, "");
      this.session = null;
      this.messages = [];
      this.draft = "";
      this.open = false;
      this.pending = false;
      this.poller = null;
    }

    connectedCallback() {
      this.render();
      this.shadowRoot.addEventListener("click", (event) => this.onClick(event));
      this.shadowRoot.addEventListener("submit", (event) => this.onSubmit(event));
      this.shadowRoot.addEventListener("input", (event) => {
        if (event.target.name === "message") this.draft = event.target.value;
      });
      this.shadowRoot.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey && event.target.name === "message") {
          event.preventDefault();
          event.target.form.requestSubmit();
        }
      });
    }

    disconnectedCallback() { clearInterval(this.poller); }

    async onClick(event) {
      if (event.target.closest("[data-launcher]")) {
        this.open = !this.open;
        this.render();
        if (this.open) await this.loadSession();
      }
      if (event.target.closest("[data-close]")) {
        this.open = false;
        clearInterval(this.poller);
        this.render();
      }
    }

    async loadSession() {
      try { this.session = JSON.parse(localStorage.getItem(STORAGE_KEY)); } catch { this.session = null; }
      if (!this.session?.conversation_id || !this.session?.token) await this.createSession();
      if (!(await this.refresh())) {
        await this.createSession();
        await this.refresh();
      }
      clearInterval(this.poller);
      this.poller = setInterval(() => this.open && this.refresh(), 5000);
    }

    async createSession() {
      const response = await fetch(`${this.endpoint}/api/widget/sessions`, { method: "POST" });
      if (!response.ok) throw new Error("대화 세션을 열 수 없습니다.");
      this.session = await response.json();
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.session));
    }

    async refresh() {
      if (this.pending) return true;
      const response = await fetch(
        `${this.endpoint}/api/widget/conversations/${this.session.conversation_id}`,
        { headers: { "X-Persona-Session-Token": this.session.token } },
      );
      if (response.status === 401 || response.status === 404) return false;
      if (!response.ok) throw new Error("대화를 불러오지 못했습니다.");
      const messages = (await response.json()).messages;
      if (JSON.stringify(messages) !== JSON.stringify(this.messages)) {
        this.messages = messages;
        this.render();
      }
      return true;
    }

    async onSubmit(event) {
      const form = event.target.closest("form");
      if (!form) return;
      event.preventDefault();
      const input = form.elements.message;
      const message = (this.draft || input.value).trim();
      if (!message || this.pending) return;
      this.pending = true;
      this.draft = "";
      input.value = "";
      this.messages.push({ role: "user", content: message });
      this.render();
      try {
        const response = await fetch(`${this.endpoint}/api/widget/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ...this.session, message }),
        });
        const body = await response.json();
        if (!response.ok) throw new Error(body.detail || "답변을 받지 못했습니다.");
        this.messages.push({ role: "assistant", content: body.answer, sources: body.sources });
      } catch (error) {
        this.messages.push({ role: "error", content: error.message });
      }
      this.pending = false;
      this.render();
    }

    messageMarkup() {
      if (!this.messages.length) return `<div class="welcome"><b>안녕하세요, 김신건입니다.</b><br>프로젝트와 경험에 관해 편하게 물어보세요. 제가 직접 확인하면 이곳으로 답장도 드립니다.</div>`;
      return this.messages.map((item) => {
        const mine = item.role === "user";
        const label = item.role === "owner" ? "김신건 · 직접 답변" : item.role === "assistant" ? "김신건 AI" : "";
        return `<div class="row ${mine ? "mine" : ""}">${label ? `<span class="label">${label}</span>` : ""}<div class="bubble ${item.role}">${renderText(item.content)}</div></div>`;
      }).join("");
    }

    render() {
      this.shadowRoot.innerHTML = `<style>
        :host{all:initial;position:fixed;z-index:2147483000;right:20px;bottom:20px;font-family:Pretendard,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#17202a}
        *{box-sizing:border-box}.launcher{width:58px;height:58px;border:0;border-radius:22px;background:#17202a;color:white;box-shadow:0 12px 35px #10182042;cursor:pointer;font-size:25px;display:grid;place-items:center;margin-left:auto}
        .panel{position:absolute;right:0;bottom:70px;width:min(390px,calc(100vw - 32px));height:min(650px,calc(100vh - 110px));background:#b9c9d5;border:1px solid #ffffff80;border-radius:24px;box-shadow:0 24px 70px #0c172a52;overflow:hidden;display:flex;flex-direction:column}
        header{height:72px;flex:none;background:#fff;padding:14px 16px;display:flex;align-items:center;gap:12px;border-bottom:1px solid #e8edf1}.avatar{width:42px;height:42px;border-radius:15px;background:#17202a;color:#fff;display:grid;place-items:center;font-weight:800}.title{font-size:15px;font-weight:800}.status{font-size:12px;color:#63717e;margin-top:3px}.close{margin-left:auto;border:0;background:transparent;font-size:24px;cursor:pointer;color:#55616c}
        .messages{flex:1;overflow:auto;padding:18px 14px;display:flex;flex-direction:column;gap:12px}.welcome{background:#ffffffd9;border-radius:16px;padding:15px;font-size:13px;line-height:1.65;box-shadow:0 2px 10px #50627317}.row{display:flex;flex-direction:column;align-items:flex-start;max-width:84%}.row.mine{align-self:flex-end;align-items:flex-end}.label{font-size:11px;color:#53636f;margin:0 4px 4px}.bubble{background:#fff;border-radius:5px 16px 16px 16px;padding:10px 12px;font-size:14px;line-height:1.55;box-shadow:0 2px 8px #52657314;word-break:break-word}.mine .bubble{background:#fee500;border-radius:16px 5px 16px 16px}.bubble.owner{outline:2px solid #17202a18}.bubble.error{background:#fff0f0;color:#a12a2a}
        form{background:#fff;padding:12px;display:flex;gap:8px;border-top:1px solid #e7ebee}textarea{font:inherit;resize:none;flex:1;min-height:42px;max-height:88px;border:1px solid #dce2e6;border-radius:14px;padding:10px 12px;outline:none}textarea:focus{border-color:#8797a4}button[type=submit]{border:0;border-radius:13px;background:#fee500;color:#17202a;font-weight:800;padding:0 15px;cursor:pointer}
        @media(max-width:520px){:host{right:12px;bottom:12px}.panel{position:fixed;inset:0;width:100vw;height:100dvh;max-height:none;border-radius:0}.launcher{width:54px;height:54px;border-radius:20px}}
        @media print{:host{display:none!important}}
        @media(prefers-reduced-motion:no-preference){.panel{animation:up .18s ease-out}@keyframes up{from{opacity:0;transform:translateY(8px)}}}
      </style>
      ${this.open ? `<section class="panel" role="dialog" aria-label="김신건에게 질문하기"><header><div class="avatar">K</div><div><div class="title">김신건에게 질문하기</div><div class="status">AI가 먼저 답하고, 제가 직접 이어서 답할 수 있습니다</div></div><button class="close" data-close aria-label="닫기">×</button></header><main class="messages">${this.messageMarkup()}</main><form><textarea name="message" maxlength="4000" aria-label="메시지" placeholder="${this.pending ? "답변을 작성하고 있습니다" : "메시지를 입력하세요"}" ${this.pending ? "disabled" : ""}>${escapeHtml(this.draft)}</textarea><button type="submit" ${this.pending ? "disabled" : ""}>${this.pending ? "···" : "전송"}</button></form></section>` : ""}
      <button class="launcher" data-launcher aria-label="${this.open ? "채팅 닫기" : "김신건에게 질문하기"}">${this.open ? "×" : "✦"}</button>`;
      if (this.open) requestAnimationFrame(() => {
        const messages = this.shadowRoot.querySelector(".messages");
        if (messages) messages.scrollTop = messages.scrollHeight;
      });
    }
  }

  if (!customElements.get("persona-chat-widget")) customElements.define("persona-chat-widget", PersonaWidgetElement);
  window.PersonaWidget = { init(options = {}) {
    if (document.querySelector("persona-chat-widget")) return;
    const widget = document.createElement("persona-chat-widget");
    widget.setAttribute("endpoint", options.endpoint || DEFAULT_ENDPOINT);
    document.body.appendChild(widget);
  }};
  const script = document.currentScript;
  if (script?.dataset.autoInit !== "false") {
    const start = () => window.PersonaWidget.init({ endpoint: script.dataset.endpoint });
    document.readyState === "loading" ? document.addEventListener("DOMContentLoaded", start) : start();
  }
})();
