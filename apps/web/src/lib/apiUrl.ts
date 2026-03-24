/**
 * API base  - dev uses Vite `/api` proxy; prod uses `VITE_API_URL` (no `/api` prefix).
 */
export function apiUrl(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  const base = import.meta.env.VITE_API_URL?.replace(/\/$/, "") ?? "";
  const useDevProxy = import.meta.env.DEV && !import.meta.env.VITE_API_URL;
  if (useDevProxy) {
    return `/api${p}`;
  }
  return `${base}${p}`;
}
