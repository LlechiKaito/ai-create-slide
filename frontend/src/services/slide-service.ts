import type { AxiosResponse } from "axios";

import { API_PATHS } from "@/constants/api";
import { apiClient } from "@/services/api-client";
import type { GenerateSlidesRequest } from "@/types/slide";

export const slideService = {
  generate: (
    data: GenerateSlidesRequest,
  ): Promise<AxiosResponse<Blob>> =>
    apiClient.post(API_PATHS.SLIDES_GENERATE, data, {
      responseType: "blob",
    }),
};
