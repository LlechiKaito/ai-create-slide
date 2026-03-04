import type { ColorConfig } from "@/types/slide";

export const MAX_SLIDES_PER_DECK = 20;
export const GENERATED_FILENAME = "generated_slides.pptx";
export const DEFAULT_NUM_SLIDES = 5;
export const MIN_NUM_SLIDES = 1;

export const SLIDE_CATEGORIES = [
  { key: "sales_proposal", label: "営業提案書" },
  { key: "business_plan", label: "事業企画書" },
  { key: "training", label: "研修資料" },
  { key: "report", label: "報告書" },
  { key: "other", label: "その他" },
] as const;

export const DEFAULT_CATEGORY = "sales_proposal";

export const FONT_FAMILIES = [
  { key: "gothic", label: "ゴシック" },
  { key: "mincho", label: "明朝" },
] as const;

export const IMAGE_SIZES = [
  { key: "small", label: "小" },
  { key: "medium", label: "中" },
  { key: "large", label: "大" },
] as const;

export const CONTENT_GAPS = [
  { key: "narrow", label: "狭い" },
  { key: "medium", label: "標準" },
  { key: "wide", label: "広い" },
] as const;

export const DEFAULT_COLOR_CONFIG: ColorConfig = {
  accent: "#F08228",
  text: "#323232",
  background: "#FFFFFF",
  font_family: "gothic",
  image_size: "medium",
  content_gap: "medium",
};
