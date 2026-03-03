import { test, expect } from "@playwright/test";

const MOCK_SLIDES_RESPONSE = {
  is_success: true,
  deck_title: "AIの未来と社会への影響",
  author: "",
  slides: [
    {
      title: "はじめに",
      subtitle: "概要",
      content: "AIの基本的な説明",
      bullet_points: ["ポイント1", "ポイント2"],
      image_prompt: "A robot thinking about AI",
      image_data: "",
    },
    {
      title: "まとめ",
      subtitle: "",
      content: "結論",
      bullet_points: [],
      image_prompt: "A summary chart",
      image_data: "",
    },
  ],
};

const MOCK_SIMPLE_RESPONSE = {
  is_success: true,
  deck_title: "テスト",
  author: "",
  slides: [
    { title: "S1", subtitle: "", content: "C1", bullet_points: [], image_prompt: "", image_data: "" },
  ],
};

const MOCK_PREVIEW_IMAGES = {
  images: ["iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="],
};

function mockPreviewImages(page: import("@playwright/test").Page) {
  return page.route("**/api/slides/preview-images", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(MOCK_PREVIEW_IMAGES),
    });
  });
}

test.describe("AI Slide Generation Flow", () => {
  test("should display the AI slide generator page", async ({ page }) => {
    await page.goto("/");
    await expect(
      page.locator("text=AI Slide Generator"),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="theme-input-form"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="theme-input"]'),
    ).toBeVisible();
  });

  test("should show validation error when theme is empty", async ({
    page,
  }) => {
    await page.goto("/");
    await page.click('[data-testid="ai-generate-button"]');
    await expect(
      page.locator('[data-testid="validation-error"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="validation-error"]'),
    ).toContainText("テーマを入力");
  });

  test("should have default slide count of 5", async ({ page }) => {
    await page.goto("/");
    const numSlidesInput = page.locator('[data-testid="num-slides-input"]');
    await expect(numSlidesInput).toHaveValue("5");
  });

  test("should allow changing slide count", async ({ page }) => {
    await page.goto("/");
    const numSlidesInput = page.locator('[data-testid="num-slides-input"]');
    await numSlidesInput.fill("10");
    await expect(numSlidesInput).toHaveValue("10");
  });

  test("should show generating state when submitting", async ({ page }) => {
    await page.goto("/");
    await page.fill('[data-testid="theme-input"]', "AIの未来");

    await page.route("**/api/slides/ai-generate", async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 2000));
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_SIMPLE_RESPONSE),
      });
    });
    await mockPreviewImages(page);

    await page.click('[data-testid="ai-generate-button"]');
    await expect(
      page.locator('[data-testid="ai-generate-button"]'),
    ).toContainText("AIが生成中");
  });

  test("should show preview with images after AI generation", async ({ page }) => {
    await page.goto("/");
    await page.fill('[data-testid="theme-input"]', "AIの未来");

    await page.route("**/api/slides/ai-generate", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_SLIDES_RESPONSE),
      });
    });
    await mockPreviewImages(page);

    await page.click('[data-testid="ai-generate-button"]');

    await expect(
      page.locator('[data-testid="slide-preview"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="preview-deck-title"]'),
    ).toContainText("AIの未来と社会への影響");
    await expect(
      page.locator('[data-testid="preview-slide-0"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="preview-slide-0"] img'),
    ).toBeVisible();

    await expect(
      page.locator('[data-testid="revision-form"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="download-button"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="reset-button"]'),
    ).toBeVisible();
  });

  test("should show revision validation error when instruction is empty", async ({
    page,
  }) => {
    await page.goto("/");
    await page.fill('[data-testid="theme-input"]', "テスト");

    await page.route("**/api/slides/ai-generate", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_SIMPLE_RESPONSE),
      });
    });
    await mockPreviewImages(page);

    await page.click('[data-testid="ai-generate-button"]');
    await expect(
      page.locator('[data-testid="slide-preview"]'),
    ).toBeVisible();

    await page.click('[data-testid="revise-button"]');
    await expect(
      page.locator('[data-testid="revision-validation-error"]'),
    ).toContainText("修正内容を入力");
  });

  test("should reset to input form when clicking reset button", async ({
    page,
  }) => {
    await page.goto("/");
    await page.fill('[data-testid="theme-input"]', "テスト");

    await page.route("**/api/slides/ai-generate", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_SIMPLE_RESPONSE),
      });
    });
    await mockPreviewImages(page);

    await page.click('[data-testid="ai-generate-button"]');
    await expect(
      page.locator('[data-testid="slide-preview"]'),
    ).toBeVisible();

    await page.click('[data-testid="reset-button"]');
    await expect(
      page.locator('[data-testid="theme-input-form"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="slide-preview"]'),
    ).not.toBeVisible();
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
