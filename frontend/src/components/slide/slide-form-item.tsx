import { MAX_BULLET_POINTS_PER_SLIDE } from "@/constants/slide";
import type { SlideInput } from "@/types/slide";

interface SlideFormItemProps {
  index: number;
  slide: SlideInput;
  onUpdate: (index: number, slide: SlideInput) => void;
  onRemove: (index: number) => void;
  canRemove: boolean;
}

export function SlideFormItem({
  index,
  slide,
  onUpdate,
  onRemove,
  canRemove,
}: SlideFormItemProps) {
  const updateField = (field: keyof SlideInput, value: string) => {
    onUpdate(index, { ...slide, [field]: value });
  };

  const updateBulletPoint = (bpIndex: number, value: string) => {
    const newBulletPoints = [...slide.bulletPoints];
    newBulletPoints[bpIndex] = value;
    onUpdate(index, { ...slide, bulletPoints: newBulletPoints });
  };

  const addBulletPoint = () => {
    if (slide.bulletPoints.length >= MAX_BULLET_POINTS_PER_SLIDE) return;
    onUpdate(index, {
      ...slide,
      bulletPoints: [...slide.bulletPoints, ""],
    });
  };

  const removeBulletPoint = (bpIndex: number) => {
    const newBulletPoints = slide.bulletPoints.filter(
      (_, i) => i !== bpIndex,
    );
    onUpdate(index, { ...slide, bulletPoints: newBulletPoints });
  };

  return (
    <div
      className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm"
      data-testid={`slide-item-${index}`}
    >
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-700">
          スライド {index + 1}
        </h3>
        {canRemove && (
          <button
            type="button"
            onClick={() => onRemove(index)}
            className="rounded-md px-3 py-1 text-sm text-red-500 hover:bg-red-50"
            data-testid={`remove-slide-${index}`}
          >
            削除
          </button>
        )}
      </div>

      <div className="space-y-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-600">
            タイトル *
          </label>
          <input
            type="text"
            value={slide.title}
            onChange={(e) => updateField("title", e.target.value)}
            className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-orange-400 focus:outline-none focus:ring-1 focus:ring-orange-400"
            placeholder="スライドのタイトル"
            data-testid={`slide-title-${index}`}
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-600">
            サブタイトル
          </label>
          <input
            type="text"
            value={slide.subtitle}
            onChange={(e) => updateField("subtitle", e.target.value)}
            className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-orange-400 focus:outline-none focus:ring-1 focus:ring-orange-400"
            placeholder="サブタイトル（任意）"
            data-testid={`slide-subtitle-${index}`}
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-600">
            本文
          </label>
          <textarea
            value={slide.content}
            onChange={(e) => updateField("content", e.target.value)}
            className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-orange-400 focus:outline-none focus:ring-1 focus:ring-orange-400"
            rows={3}
            placeholder="本文テキスト（任意）"
            data-testid={`slide-content-${index}`}
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-gray-600">
            箇条書き
          </label>
          {slide.bulletPoints.map((bp, bpIndex) => (
            <div key={bpIndex} className="mb-2 flex items-center gap-2">
              <span className="text-gray-400">-</span>
              <input
                type="text"
                value={bp}
                onChange={(e) =>
                  updateBulletPoint(bpIndex, e.target.value)
                }
                className="flex-1 rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-orange-400 focus:outline-none focus:ring-1 focus:ring-orange-400"
                placeholder="箇条書き項目"
                data-testid={`bullet-point-${index}-${bpIndex}`}
              />
              <button
                type="button"
                onClick={() => removeBulletPoint(bpIndex)}
                className="text-sm text-gray-400 hover:text-red-500"
                data-testid={`remove-bullet-${index}-${bpIndex}`}
              >
                x
              </button>
            </div>
          ))}
          {slide.bulletPoints.length < MAX_BULLET_POINTS_PER_SLIDE && (
            <button
              type="button"
              onClick={addBulletPoint}
              className="text-sm text-orange-500 hover:text-orange-600"
              data-testid={`add-bullet-${index}`}
            >
              + 箇条書きを追加
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
