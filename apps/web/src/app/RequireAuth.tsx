import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";

/**
 * In production, app routes require a logged-in user (`userId` in localStorage, set by `/auth`).
 * In development, this wrapper is a no-op so you can iterate without signing in, or use `/dev/session`.
 */
export function RequireAuth({ children }: { children: ReactNode }) {
  const location = useLocation();

  if (!import.meta.env.PROD) {
    return <>{children}</>;
  }

  const uid = localStorage.getItem("userId");
  if (!uid) {
    return <Navigate to="/auth" replace state={{ from: location.pathname }} />;
  }

  return <>{children}</>;
}
