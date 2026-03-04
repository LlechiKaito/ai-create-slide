import axios from "axios";

import { setApiBaseUrl } from "@/constants/config";
import { apiClient } from "@/services/api-client";

interface RuntimeConfig {
  apiUrl: string;
}

export async function loadRuntimeConfig(): Promise<void> {
  if (import.meta.env.DEV) {
    return;
  }

  const response = await axios.get<RuntimeConfig>("/runtime-config.json");
  const { apiUrl } = response.data;

  setApiBaseUrl(apiUrl);
  apiClient.defaults.baseURL = apiUrl;
}
