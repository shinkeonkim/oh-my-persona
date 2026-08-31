const { test, expect } = require('@playwright/test');
test.beforeEach(async ({ page }) => { await page.goto('/'); });
test('desktop renders a complete two-pane messenger', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'desktop');
  await expect(page.locator('.sidebar')).toBeVisible(); await expect(page.locator('.chat-main')).toBeVisible();
  const shell = await page.locator('.messenger-shell').boundingBox(); expect(shell.width).toBeGreaterThan(1000); expect(shell.height).toBe(page.viewportSize().height);
  await expect(page).toHaveScreenshot('react-messenger-desktop.png', { animations: 'disabled' });
});
test('mobile has no overflow and exposes sidebar drawer', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'mobile'); await expect(page.locator('.sidebar')).not.toBeInViewport();
  const d = await page.evaluate(() => ({ scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth })); expect(d.scrollWidth).toBe(d.clientWidth);
  await page.locator('.menu-button').click(); await expect(page.locator('.sidebar')).toBeInViewport(); await expect(page.getByRole('link', { name: '관리 콘솔' })).toBeVisible();
  await expect(page).toHaveScreenshot('react-messenger-mobile-menu.png', { animations: 'disabled' }); await page.locator('.backdrop').click({ position: { x: 370, y: 300 } }); await expect(page.locator('.sidebar')).not.toBeInViewport();
});
test('suggested question fills the composer', async ({ page }, testInfo) => { if (testInfo.project.name === 'mobile') await page.locator('.menu-button').click(); await page.locator('.side-prompt').first().click(); await expect(page.getByPlaceholder('메시지를 입력하세요')).toHaveValue('최근에 가장 집중하고 있는 일은 무엇인가요?'); });
