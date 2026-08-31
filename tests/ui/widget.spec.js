const { test, expect } = require('@playwright/test');

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => localStorage.clear());
  await page.goto('/');
  await page.addScriptTag({ url: '/sdk/persona-widget.js' });
});

test('embedded widget opens without covering the desktop host page', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'desktop');
  const widget = page.locator('persona-chat-widget');
  await expect(widget.locator('[data-launcher]')).toBeVisible();
  await widget.locator('[data-launcher]').click();
  await expect(widget.locator('[role=dialog]')).toBeVisible();
  const panel = await widget.locator('.panel').boundingBox();
  expect(panel.width).toBeLessThanOrEqual(390);
  expect(panel.x + panel.width).toBeLessThanOrEqual(1440);
  await expect(page).toHaveScreenshot('widget-desktop-open.png', { animations: 'disabled' });
});

test('embedded widget becomes a full-screen mobile messenger', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'mobile');
  const widget = page.locator('persona-chat-widget');
  await widget.locator('[data-launcher]').click();
  await page.waitForTimeout(250);
  const panel = await widget.locator('.panel').boundingBox();
  expect(panel.x).toBe(0);
  expect(panel.y).toBe(0);
  expect(panel.width).toBe(page.viewportSize().width);
  expect(panel.height).toBe(page.viewportSize().height);
  await expect(page).toHaveScreenshot('widget-mobile-open.png', { animations: 'disabled' });
});

test('a background refresh does not erase an optimistic pending message', async ({ page }) => {
  await page.route('**/api/widget/sessions', (route) => route.fulfill({
    status: 201,
    contentType: 'application/json',
    body: JSON.stringify({ conversation_id: '00000000-0000-4000-8000-000000000001', token: 'test-token-that-is-long-enough' }),
  }));
  await page.route('**/api/widget/conversations/**', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ messages: [] }),
  }));
  await page.route('**/api/widget/chat', async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 250));
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ answer: '답변입니다.', sources: [] }),
    });
  });
  await page.evaluate(() => localStorage.clear());
  const widget = page.locator('persona-chat-widget');
  await widget.locator('[data-launcher]').click();
  await widget.locator('textarea').fill('질문입니다.');
  await widget.locator('form').evaluate((form) => form.requestSubmit());
  await widget.evaluate((element) => element.refresh());
  await expect(widget.locator('.bubble.user')).toHaveText('질문입니다.');
  await expect(widget.locator('.bubble.assistant')).toHaveText('답변입니다.');
});

test('an unchanged refresh preserves the focused composer and draft', async ({ page }) => {
  await page.route('**/api/widget/sessions', (route) => route.fulfill({
    status: 201,
    contentType: 'application/json',
    body: JSON.stringify({ conversation_id: '00000000-0000-4000-8000-000000000002', token: 'test-token-that-is-long-enough' }),
  }));
  await page.route('**/api/widget/conversations/**', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ messages: [] }),
  }));
  await page.evaluate(() => localStorage.clear());
  const widget = page.locator('persona-chat-widget');
  await widget.locator('[data-launcher]').click();
  const composer = widget.locator('textarea');
  await composer.fill('입력 중인 메시지입니다.');
  await widget.evaluate((element) => element.refresh());
  await expect(composer).toHaveValue('입력 중인 메시지입니다.');
  await expect(composer).toBeFocused();
});

test('SSE owner messages arrive without losing the current draft', async ({ page }) => {
  const widget = page.locator('persona-chat-widget');
  await widget.locator('[data-launcher]').click();
  const composer = widget.locator('textarea');
  await composer.fill('작성 중인 초안');
  await widget.evaluate((element) => element.consumeStreamBlock(
    'event: messages\ndata: {"messages":[{"role":"owner","content":"관리자 직접 답변"}]}',
  ));
  await expect(widget.locator('.bubble.owner')).toHaveText('관리자 직접 답변');
  await expect(widget.locator('textarea')).toHaveValue('작성 중인 초안');
});
