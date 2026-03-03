import { useState } from "react";

import { SlideFormItem } from "@/components/slide/slide-form-item";
import { ERROR_MESSAGES } from "@/constants/errors";
import { MAX_SLIDES_PER_DECK } from "@/constants/slide";
import type { SlideInput } from "@/types/slide";

const EMPTY_SLIDE: SlideInput = {
  title: "",
  subtitle: "",
  content: "",
  bulletPoints: [],
};

interface SlideFormProps {
  onGenerate: (
    deckTitle: string,
    author: string,
    slides: SlideInput[],
  ) => Promise<void>;
  loading: boolean;
}

export function SlideForm({ onGenerate, loading }: SlideFormProps) {
  const [deckTitle, setDeckTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [slides, setSlides] = useState<SlideInput[]>([{ ...EMPTY_SLIDE }]);
  const [validationError, setValidationError] = useState("");

  const addSlide = () => {
    if (slides.length >= MAX_SLIDES_PER_DECK) return;
    setSlides([...slides, { ...EMPTY_SLIDE }]);
  };

  const removeSlide = (index: number) => {
    setSlides(slides.filter((_, i) => i !== index));
  };

  const updateSlide = (index: number, updated: SlideInput) => {
    const newSlides = [...slides];
    newSlides[index] = updated;
    setSlides(newSlides);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError("");

    if (!deckTitle.trim()) {
      setValidationError(ERROR_MESSAGES.EMPTY_DECK_TITLE);
      return;
    }

    const hasEmptyTitle = slides.some((s) => !s.title.trim());
    if (hasEmptyTitle) {
      setValidationError(ERROR_MESSAGES.EMPTY_SLIDE_TITLE);
      return;
    }

    await onGenerate(deckTitle, author, slides);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6" data-testid="slide-form">
      <div className="rounded-lg border border-orange-200 bg-orange-50 p-6">
        <h2 className="mb-4 text-xl font-bold text-gray-800">
          プレゼンテーション情報
        </h2>
        <div className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-600">
              タイトル *
            </label>
            <input
              type="text"
              value={deckTitle}
              onChange={(e) => setDeckTitle(e.target.value)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-orange-400 focus:outline-none focus:ring-1 focus:ring-orange-400"
              placeholder="プレゼンテーションのタイトル"
              data-testid="deck-title"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-600">
              作成者
            </label>
            <input
              type="text"
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-orange-400 focus:outline-none focus:ring-1 focus:ring-orange-400"
              placeholder="作成者名（任意）"
              data-testid="deck-author"
            />
          </div>
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

      <div className="space-y-4">
        <h2 className="text-xl font-bold text-gray-800">スライド</h2>
        {slides.map((slide, index) => (
          <SlideFormItem
            key={index}
            index={index}
            slide={slide}
            onUpdate={updateSlide}
            onRemove={removeSlide}
            canRemove={slides.length > 1}
          />
        ))}
      </div>

      <div className="flex items-center gap-4">
        {slides.length < MAX_SLIDES_PER_DECK && (
          <button
            type="button"
            onClick={addSlide}
            className="rounded-md border-2 border-dashed border-gray-300 px-4 py-2 text-gray-500 hover:border-orange-400 hover:text-orange-500"
            data-testid="add-slide-button"
          >
            + スライドを追加
          </button>
        )}
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-md bg-orange-500 px-6 py-3 text-lg font-bold text-white hover:bg-orange-600 disabled:cursor-not-allowed disabled:bg-gray-400"
        data-testid="generate-button"
      >
        {loading ? "生成中..." : "スライドを生成してダウンロード"}
      </button>
    </form>
  );
}
