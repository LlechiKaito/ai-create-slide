import type { ColorConfig } from "@/types/slide";
import { FONT_FAMILIES } from "@/constants/slide";

interface ColorConfigPanelProps {
  colorConfig: ColorConfig;
  onChange: (config: ColorConfig) => void;
}

const COLOR_FIELDS = [
  { key: "accent" as const, label: "アクセント" },
  { key: "text" as const, label: "文字色" },
  { key: "background" as const, label: "背景色" },
];

export function ColorConfigPanel({
  colorConfig,
  onChange,
}: ColorConfigPanelProps) {
  const handleChange = (key: keyof ColorConfig, value: string) => {
    onChange({ ...colorConfig, [key]: value });
  };

  return (
    <div
      className="space-y-3"
      data-testid="color-config-panel"
    >
      <div className="flex items-center gap-6">
        <span className="text-sm font-medium text-gray-600">カラー:</span>
        {COLOR_FIELDS.map(({ key, label }) => (
          <label key={key} className="flex items-center gap-2 text-sm text-gray-600">
            {label}
            <input
              type="color"
              value={colorConfig[key]}
              onChange={(e) => handleChange(key, e.target.value)}
              className="h-8 w-8 cursor-pointer rounded border border-gray-300"
              data-testid={`color-${key}`}
            />
          </label>
        ))}
      </div>
      <div className="flex flex-wrap items-center gap-4">
        <label className="flex items-center gap-2 text-sm text-gray-600">
          フォント
          <select
            value={colorConfig.font_family}
            onChange={(e) => handleChange("font_family", e.target.value)}
            className="rounded-md border border-gray-300 px-2 py-1 text-sm focus:border-orange-400 focus:outline-none focus:ring-1 focus:ring-orange-400"
            data-testid="font-family-select"
          >
            {FONT_FAMILIES.map(({ key, label }) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>
        </label>
      </div>
    </div>
  );
}
