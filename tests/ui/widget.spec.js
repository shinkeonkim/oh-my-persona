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
