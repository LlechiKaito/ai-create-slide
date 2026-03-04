import type { AxiosResponse } from "axios";

import { API_PATHS } from "@/constants/api";
import { apiClient } from "@/services/api-client";
import type {
  AiGenerateRequest,
  AiGenerateResponse,
  AiReviseRequest,
  AiReviseSlideRequest,
  AiReviseSlideResponse,
  GenerateSlidesRequest,
  PreviewImagesRequest,
  PreviewImagesResponse,
} from "@/types/slide";

export const slideService = {
  generate: (
    data: GenerateSlidesRequest,
  ): Promise<AxiosResponse<Blob>> =>
    apiClient.post(API_PATHS.SLIDES_GENERATE, data, {
      responseType: "blob",
    }),

  aiGenerate: (
    data: AiGenerateRequest,
  ): Promise<AxiosResponse<AiGenerateResponse>> =>
    apiClient.post(API_PATHS.AI_GENERATE, data),

  aiRevise: (
    data: AiReviseRequest,
  ): Promise<AxiosResponse<AiGenerateResponse>> =>
    apiClient.post(API_PATHS.AI_REVISE, data),

  aiReviseSlide: (
    data: AiReviseSlideRequest,
  ): Promise<AxiosResponse<AiReviseSlideResponse>> =>
    apiClient.post(API_PATHS.AI_REVISE_SLIDE, data),

  previewImages: (
    data: PreviewImagesRequest,
  ): Promise<AxiosResponse<PreviewImagesResponse>> =>
    apiClient.post(API_PATHS.PREVIEW_IMAGES, data),
};
