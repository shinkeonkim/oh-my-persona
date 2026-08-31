const { test, expect } = require("@playwright/test");

test("admin can send a direct reply into a selected conversation", async ({
  page,
}) => {
  let submitted = null;
  await page.addInitScript(() =>
    sessionStorage.setItem("personaAdminToken", "test-token"),
  );
  await page.route("**/api/admin/**", async (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname;
    let body;
    if (path === "/api/admin/knowledge")
      body = { managed: [], packaged: [], packaged_total: 0 };
    else if (path === "/api/admin/knowledge-gaps")
      body = {
        summary: { indirect_evidence: 1 },
        questions: [
          {
            question_id: "PQ-014",
            category: "community",
            question: "운영진 경험은 어땠나요?",
            status: "indirect_evidence",
            unique_source_count: 2,
            evidence_urls: [],
            answer_hint: "직접 답변하세요.",
            managed_answer: null,
          },
        ],
      };
    else if (path === "/api/admin/conversations")
      body = {
        conversations: [
          {
            id: "conversation-1",
            preview: "문의합니다",
            message_count: 1,
            updated_at: "2026-08-31",
          },
        ],
      };
    else if (path.endsWith("/messages")) {
      submitted = request.postDataJSON();
      body = { role: "owner", content: submitted.content };
    } else
      body = {
        conversation_id: "conversation-1",
        messages: [{ role: "user", content: "문의합니다" }],
      };
    await route.fulfill({
      status: path.endsWith("/messages") ? 201 : 200,
      contentType: "application/json",
      body: JSON.stringify(body),
    });
  });
  await page.goto("/admin");
  await page.locator("[data-tab=conversations]").click();
  await page.locator("#conversation-list .item").click();
  await expect(page.locator("#conversation-reply-form")).toBeVisible();
  await page.locator("#conversation-reply").fill("제가 직접 답변드립니다.");
  await page.locator("#conversation-reply-form button").click();
  await expect
    .poll(() => submitted)
    .toEqual({ content: "제가 직접 답변드립니다." });
});

test("admin can save a knowledge gap answer as a private draft", async ({
  page,
}) => {
  let submitted = null;
  await page.addInitScript(() =>
    sessionStorage.setItem("personaAdminToken", "test-token"),
  );
  await page.route("**/api/admin/**", async (route) => {
    const request = route.request(),
      path = new URL(request.url()).pathname;
    let body = {};
    if (path === "/api/admin/knowledge")
      body = { managed: [], packaged: [], packaged_total: 0 };
    else if (path === "/api/admin/knowledge-gaps/PQ-014/answer") {
      submitted = request.postDataJSON();
      body = { id: "answer-1", status: "draft" };
    } else if (path === "/api/admin/knowledge-gaps")
      body = {
        summary: { indirect_evidence: 1 },
        questions: [
          {
            question_id: "PQ-014",
            category: "community",
            question: "운영진 경험은 어땠나요?",
            status: "indirect_evidence",
            unique_source_count: 2,
            evidence_urls: [],
            answer_hint: "직접 답변하세요.",
            managed_answer: null,
          },
        ],
      };
    else if (path === "/api/admin/conversations") body = { conversations: [] };
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(body),
    });
  });
  await page.goto("/admin");
  await page.locator("[data-tab=gaps]").click();
  await page.locator("#gap-list .item").click();
  await page.locator("#gap-answer").fill("제가 직접 작성한 답변입니다.");
  await page.locator("#gap-answer-form button").click();
  await expect
    .poll(() => submitted)
    .toMatchObject({
      answer: "제가 직접 작성한 답변입니다.",
      visibility: "private",
      evidence_urls: [],
    });
});
