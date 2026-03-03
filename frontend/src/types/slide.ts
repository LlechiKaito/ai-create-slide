export interface SlideInput {
  title: string;
  subtitle: string;
  content: string;
  bulletPoints: string[];
}

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

export interface ApiErrorResponse {
  is_success: false;
  message: string;
  code: string;
}
