export let API_BASE_URL = import.meta.env.VITE_API_URL ?? "";

export function setApiBaseUrl(url: string): void {
  API_BASE_URL = url;
}
