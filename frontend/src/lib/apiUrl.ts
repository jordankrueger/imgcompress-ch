// CH-patch: Next.js `basePath` prefixes router links but does NOT auto-prefix:
//   - fetch() calls
//   - <Image> src in static-export mode with `images.unoptimized: true`
// At https://tools.campaign.help/image-pro/, hardcoded "/api/..." or
// "/some-asset.png" paths resolve to the landing's nginx instead of this
// fork. Wrap every such path with apiUrl() / assetUrl() to apply the prefix.
//
// If the basePath ever changes, update BASE here — it's the only place.

const BASE = "/image-pro";

export const apiUrl = (path: string): string => {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${BASE}${normalized}`;
};

// Same shape as apiUrl, named separately so callers signal intent.
export const assetUrl = (path: string): string => apiUrl(path);
