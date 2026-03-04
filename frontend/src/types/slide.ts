export interface ColorConfig {
  accent: string;
  text: string;
  background: string;
}

export interface GenerateSlidesRequest {
  deck_title: string;
  author: string;
  slides: {
    title: string;
    subtitle: string;
    content: string;
    bullet_points: string[];
    image_data: string;
  }[];
  color_config: ColorConfig;
}

export interface AiGenerateRequest {
  theme: string;
  num_slides: number;
  category: string;
  color_config: ColorConfig;
}

export interface AiSlideContent {
  title: string;
  subtitle: string;
  content: string;
  bullet_points: string[];
  image_prompt: string;
  image_data: string;
}

export interface AiGenerateResponse {
  is_success: boolean;
  deck_title: string;
  author: string;
  slides: AiSlideContent[];
}

export interface AiReviseRequest {
  current_content: {
    is_success: boolean;
    deck_title: string;
    author: string;
    slides: AiSlideContent[];
  };
  revision_instruction: string;
  color_config: ColorConfig;
}

export interface AiReviseSlideRequest {
  slide_index: number;
  current_slide: AiSlideContent;
  revision_instruction: string;
}

export interface AiReviseSlideResponse {
  is_success: boolean;
  slide: AiSlideContent;
}

export interface PreviewImagesRequest {
  deck_title: string;
  author: string;
  slides: AiSlideContent[];
  color_config: ColorConfig;
}

export interface PreviewImagesResponse {
  images: string[];
}
