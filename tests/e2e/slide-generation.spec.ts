import { test, expect } from "@playwright/test";

test.describe("Slide Generation Flow", () => {
  test("should display the slide generator page", async ({ page }) => {
    await page.goto("/");
    await expect(
      page.locator("text=AI Slide Generator"),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="slide-form"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="deck-title"]'),
    ).toBeVisible();
  });

  test("should show validation error when deck title is empty", async ({
    page,
  }) => {
    await page.goto("/");
    await page.click('[data-testid="generate-button"]');
    await expect(
      page.locator('[data-testid="validation-error"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="validation-error"]'),
    ).toContainText("タイトルを入力");
  });

  test("should show validation error when slide title is empty", async ({
    page,
  }) => {
    await page.goto("/");
    await page.fill('[data-testid="deck-title"]', "Test Presentation");
    await page.click('[data-testid="generate-button"]');
    await expect(
      page.locator('[data-testid="validation-error"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="validation-error"]'),
    ).toContainText("スライドのタイトル");
  });

  test("should add and remove slides", async ({ page }) => {
    await page.goto("/");
    await expect(
      page.locator('[data-testid="slide-item-0"]'),
    ).toBeVisible();

    await page.click('[data-testid="add-slide-button"]');
    await expect(
      page.locator('[data-testid="slide-item-1"]'),
    ).toBeVisible();

    await page.click('[data-testid="remove-slide-1"]');
    await expect(
      page.locator('[data-testid="slide-item-1"]'),
    ).not.toBeVisible();
  });

  test("should add and remove bullet points", async ({ page }) => {
    await page.goto("/");

    await page.click('[data-testid="add-bullet-0"]');
    await expect(
      page.locator('[data-testid="bullet-point-0-0"]'),
    ).toBeVisible();

    await page.fill('[data-testid="bullet-point-0-0"]', "Test bullet");

    await page.click('[data-testid="remove-bullet-0-0"]');
    await expect(
      page.locator('[data-testid="bullet-point-0-0"]'),
    ).not.toBeVisible();
  });

  test("should fill form and submit for download", async ({ page }) => {
    await page.goto("/");

    await page.fill('[data-testid="deck-title"]', "Test Presentation");
    await page.fill('[data-testid="deck-author"]', "Test Author");

    await page.fill('[data-testid="slide-title-0"]', "First Slide");
    await page.fill(
      '[data-testid="slide-subtitle-0"]',
      "Subtitle",
    );
    await page.fill(
      '[data-testid="slide-content-0"]',
      "Content of the first slide",
    );

    const downloadPromise = page.waitForEvent("download");
    await page.click('[data-testid="generate-button"]');
    const download = await downloadPromise;

    expect(download.suggestedFilename()).toBe("generated_slides.pptx");
  });

  test("should navigate to 404 page for unknown routes", async ({
    page,
  }) => {
    await page.goto("/unknown-route");
    await expect(page.locator("text=404")).toBeVisible();
    await expect(
      page.locator("text=ページが見つかりません"),
    ).toBeVisible();
  });
});
