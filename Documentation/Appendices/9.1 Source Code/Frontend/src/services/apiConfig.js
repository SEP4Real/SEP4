const configuredApiUrl = import.meta.env.VITE_API_URL?.trim();

const shouldUseDefaultApiUrl =
  !configuredApiUrl ||
  configuredApiUrl === "/" ||
  configuredApiUrl === "." ||
  configuredApiUrl === window.location.origin ||
  configuredApiUrl === `${window.location.origin}/`;

export const API_URL = shouldUseDefaultApiUrl
  ? "/api"
  : configuredApiUrl.replace(/\/$/, "");
