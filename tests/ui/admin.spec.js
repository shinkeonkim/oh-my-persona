const { test, expect } = require('@playwright/test');

test('admin can send a direct reply into a selected conversation', async ({ page }) => {
  let submitted = null;
  await page.addInitScript(() => sessionStorage.setItem('personaAdminToken', 'test-token'));
  await page.route('**/api/admin/**', async (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname;
    let body;
    if (path === '/api/admin/knowledge') body = { managed: [], packaged: [], packaged_total: 0 };
    else if (path === '/api/admin/conversations') body = { conversations: [{ id: 'conversation-1', preview: '문의합니다', message_count: 1, updated_at: '2026-08-31' }] };
    else if (path.endsWith('/messages')) {
      submitted = request.postDataJSON();
      body = { role: 'owner', content: submitted.content };
    } else body = { conversation_id: 'conversation-1', messages: [{ role: 'user', content: '문의합니다' }] };
    await route.fulfill({ status: path.endsWith('/messages') ? 201 : 200, contentType: 'application/json', body: JSON.stringify(body) });
  });
  await page.goto('/admin');
  await page.locator('[data-tab=conversations]').click();
  await page.locator('#conversation-list .item').click();
  await expect(page.locator('#conversation-reply-form')).toBeVisible();
  await page.locator('#conversation-reply').fill('제가 직접 답변드립니다.');
  await page.locator('#conversation-reply-form button').click();
  await expect.poll(() => submitted).toEqual({ content: '제가 직접 답변드립니다.' });
});
