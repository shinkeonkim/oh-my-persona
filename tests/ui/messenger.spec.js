const { test, expect } = require('@playwright/test');

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => localStorage.clear());
  await page.goto('/');
  await expect(page.locator('#model option').first()).toBeAttached();
});

test('desktop renders a complete two-pane messenger', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'desktop');
  await expect(page.locator('.sidebar')).toBeVisible();
  await expect(page.locator('.chat-panel')).toBeVisible();
  await expect(page.locator('#model')).not.toHaveValue('');
  const shell = await page.locator('.messenger').boundingBox();
  const composer = await page.locator('.chat-form').boundingBox();
  expect(shell.width).toBeGreaterThan(1000);
  expect(composer.y + composer.height).toBeLessThanOrEqual(shell.y + shell.height + 1);
  await expect(page).toHaveScreenshot('messenger-desktop.png', { animations: 'disabled' });
});

test('mobile uses the full viewport without horizontal overflow', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'mobile');
  await expect(page.locator('.sidebar')).toBeHidden();
  await expect(page.locator('.chat-header')).toBeVisible();
  const dimensions = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
    height: document.querySelector('.messenger').getBoundingClientRect().height,
  }));
  expect(dimensions.scrollWidth).toBe(dimensions.clientWidth);
  expect(dimensions.height).toBe(page.viewportSize().height);
  await expect(page).toHaveScreenshot('messenger-mobile.png', { animations: 'disabled' });
});

test('suggested question fills the composer', async ({ page }) => {
  await page.locator('.quick-prompts button').first().click();
  await expect(page.locator('#message')).toHaveValue('최근에 가장 집중하고 있는 일은 무엇인가요?');
  await expect(page.locator('#message')).toBeFocused();
});
