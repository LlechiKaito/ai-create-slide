export interface GenerateSlidesRequest {
  deck_title: string;
  author: string;
  slides: {
    title: string;
    subtitle: string;
    content: string;
    bullet_points: string[];
  }[];
}

export interface AiGenerateRequest {
  theme: string;
  num_slides: number;
}

export interface AiSlideContent {
  title: string;
  subtitle: string;
  content: string;
  bullet_points: string[];
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
}