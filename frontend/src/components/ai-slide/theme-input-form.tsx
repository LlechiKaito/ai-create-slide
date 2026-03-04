import { useState } from "react";

import { ColorConfigPanel } from "@/components/ai-slide/color-config-panel";
import { ERROR_MESSAGES } from "@/constants/errors";
import {
  DEFAULT_CATEGORY,
  DEFAULT_NUM_SLIDES,
  MAX_SLIDES_PER_DECK,
  MIN_NUM_SLIDES,
  SLIDE_CATEGORIES,
} from "@/constants/slide";
import type { ColorConfig } from "@/types/slide";

interface ThemeInputFormProps {
  onGenerate: (
    theme: string,
    numSlides: number,
    category: string,
  ) => Promise<void>;
  loading: boolean;
  colorConfig: ColorConfig;
  onColorChange: (config: ColorConfig) => void;
}

export function ThemeInputForm({
  onGenerate,
  loading,
  colorConfig,
  onColorChange,
}: ThemeInputFormProps) {
  const [theme, setTheme] = useState("");
  const [numSlides, setNumSlides] = useState(DEFAULT_NUM_SLIDES);
  const [category, setCategory] = useState(DEFAULT_CATEGORY);
  const [validationError, setValidationError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError("");

    if (!theme.trim()) {
      setValidationError(ERROR_MESSAGES.EMPTY_THEME);
      return;
    }

    await onGenerate(theme, numSlides, category);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-6"
      data-testid="theme-input-form"
    >
      <div className="rounded-lg border border-orange-200 bg-orange-50 p-6">
        <h2 className="mb-4 text-xl font-bold text-gray-800">
          AIでスライドを自動生成
        </h2>
        <p className="mb-6 text-sm text-gray-500">
          カテゴリとテーマを入力するだけで、AIがスライドの内容を自動生成します
        </p>

        <div className="space-y-4">
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-600">
              カテゴリ
            </label>
            <div
              className="flex gap-2"
              data-testid="category-tabs"
            >
              {SLIDE_CATEGORIES.map(({ key, label }) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => setCategory(key)}
                  className={`rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                    category === key
                      ? "bg-orange-500 text-white"
                      : "bg-white text-gray-600 border border-gray-300 hover:bg-orange-50"
                  }`}
                  data-testid={`category-${key}`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-600">
              テーマ *
            </label>
            <textarea
              value={theme}
              onChange={(e) => setTheme(e.target.value)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-orange-400 focus:outline-none focus:ring-1 focus:ring-orange-400"
              rows={3}
              placeholder="例: AIの未来と社会への影響について"
              data-testid="theme-input"
            />
          </div>

          <div className="flex items-end gap-6">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-600">
                スライド枚数
              </label>
              <input
                type="number"
                value={numSlides}
                onChange={(e) => setNumSlides(Number(e.target.value))}
                min={MIN_NUM_SLIDES}
                max={MAX_SLIDES_PER_DECK}
                className="w-32 rounded-md border border-gray-300 px-3 py-2 focus:border-orange-400 focus:outline-none focus:ring-1 focus:ring-orange-400"
                data-testid="num-slides-input"
              />
            </div>
          </div>

          <ColorConfigPanel
            colorConfig={colorConfig}
            onChange={onColorChange}
          />
        </div>
      </div>

      {validationError && (
        <div
          className="rounded-md bg-red-50 p-3 text-sm text-red-600"
          data-testid="validation-error"
        >
          {validationError}
        </div>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-md bg-orange-500 px-6 py-3 text-lg font-bold text-white hover:bg-orange-600 disabled:cursor-not-allowed disabled:bg-gray-400"
        data-testid="ai-generate-button"
      >
        {loading ? "AIが生成中..." : "AIでスライドを生成"}
      </button>
    </form>
  );
}
