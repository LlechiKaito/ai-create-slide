import { useState } from "react";

import { ERROR_MESSAGES } from "@/constants/errors";
import type { AiGenerateResponse } from "@/types/slide";

interface SlidePreviewProps {
  content: AiGenerateResponse;
  previewImages: string[];
  onReviseSlide: (slideIndex: number, instruction: string) => Promise<void>;
  loading: boolean;
}

export function SlidePreview({
  content,
  previewImages,
  onReviseSlide,
  loading,
}: SlidePreviewProps) {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [slideInstruction, setSlideInstruction] = useState("");
  const [validationError, setValidationError] = useState("");

  const handleReviseSlide = async (index: number) => {
    setValidationError("");
    if (!slideInstruction.trim()) {
      setValidationError(ERROR_MESSAGES.EMPTY_REVISION);
      return;
    }
    await onReviseSlide(index, slideInstruction);
    setEditingIndex(null);
    setSlideInstruction("");
  };

  return (
    <div className="space-y-4" data-testid="slide-preview">
      <div className="rounded-lg border border-orange-200 bg-orange-50 p-4">
        <h2
          className="text-xl font-bold text-gray-800"
          data-testid="preview-deck-title"
        >
          {content.deck_title}
        </h2>
        {content.author && (
          <p className="text-sm text-gray-500">
            作成者: {content.author}
          </p>
        )}
      </div>

      {previewImages.length > 0 ? (
        previewImages.map((image, index) => (
          <div
            key={index}
            className="overflow-hidden rounded-lg border border-gray-200 shadow-sm"
            data-testid={`preview-slide-${index}`}
          >
            <img
              src={`data:image/png;base64,${image}`}
              alt={`スライド ${index + 1}`}
              className="w-full"
            />
            {index > 0 && (
              <div className="border-t border-gray-100 bg-gray-50 px-4 py-2">
                {editingIndex === index - 1 ? (
                  <div className="space-y-2">
                    <textarea
                      value={slideInstruction}
                      onChange={(e) => setSlideInstruction(e.target.value)}
                      className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-orange-400 focus:outline-none focus:ring-1 focus:ring-orange-400"
                      rows={2}
                      placeholder="このスライドへの修正内容を入力"
                      data-testid={`slide-revision-input-${index - 1}`}
                    />
                    {validationError && (
                      <p className="text-xs text-red-500">{validationError}</p>
                    )}
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => handleReviseSlide(index - 1)}
                        disabled={loading}
                        className="rounded-md bg-orange-500 px-3 py-1 text-sm font-medium text-white hover:bg-orange-600 disabled:bg-gray-400"
                        data-testid={`slide-revision-submit-${index - 1}`}
                      >
                        {loading ? "修正中..." : "修正"}
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setEditingIndex(null);
                          setSlideInstruction("");
                          setValidationError("");
                        }}
                        className="rounded-md border border-gray-300 px-3 py-1 text-sm text-gray-600 hover:bg-gray-100"
                      >
                        キャンセル
                      </button>
                    </div>
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={() => {
                      setEditingIndex(index - 1);
                      setSlideInstruction("");
                      setValidationError("");
                    }}
                    disabled={loading}
                    className="text-sm font-medium text-orange-500 hover:text-orange-600 disabled:text-gray-400"
                    data-testid={`slide-edit-btn-${index - 1}`}
                  >
                    このスライドを修正
                  </button>
                )}
              </div>
            )}
          </div>
        ))
      ) : (
        content.slides.map((slide, index) => (
          <div
            key={index}
            className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm"
            data-testid={`preview-slide-${index}`}
          >
            <div className="mb-2 text-xs font-medium text-orange-400">
              スライド {index + 1}
            </div>
            <h3 className="mb-1 text-lg font-bold text-gray-800">
              {slide.title}
            </h3>
            {slide.subtitle && (
              <p className="mb-2 text-sm text-gray-500">{slide.subtitle}</p>
            )}
            {slide.content && (
              <p className="mb-3 text-sm text-gray-700">{slide.content}</p>
            )}
            {slide.bullet_points.length > 0 && (
              <ul className="list-inside list-disc space-y-1 text-sm text-gray-600">
                {slide.bullet_points.map((bp, bpIndex) => (
                  <li key={bpIndex}>{bp}</li>
                ))}
              </ul>
            )}
          </div>
        ))
      )}
    </div>
  );
}
