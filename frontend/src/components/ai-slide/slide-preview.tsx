import type { AiGenerateResponse } from "@/types/slide";

interface SlidePreviewProps {
  content: AiGenerateResponse;
  previewImages: string[];
}

export function SlidePreview({ content, previewImages }: SlidePreviewProps) {
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
