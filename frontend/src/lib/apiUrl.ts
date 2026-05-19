// CH-patch: Next.js `basePath` prefixes assets + router URLs but NOT fetch() calls.
// At https://tools.campaign.help/image-pro/, a `fetch("/api/...")` resolves to the
// landing's nginx (which returns HTML) instead of this fork's Flask backend. Wrap
// every API call with apiUrl() so the prefix is applied consistently.
//
// If the basePath ever changes, update API_BASE here — it's the only place.

const API_BASE = "/image-pro";

export const apiUrl = (path: string): string => {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${normalized}`;
};
