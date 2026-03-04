import type { ColorConfig } from "@/types/slide";

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
      className="flex items-center gap-6"
      data-testid="color-config-panel"
    >
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
  );
}
