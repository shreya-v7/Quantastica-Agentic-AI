import { Navigate } from "react-router-dom";
import { DEV_DUMMY_USER_ID } from "../config/devDummyUser";

/**
 * Dev-only: sets a dummy `userId` and sends you to the dashboard.
 * In production builds (`import.meta.env.PROD`), always redirects home — no bypass.
 */
export default function DevSessionEntry() {
  if (!import.meta.env.DEV) {
    return <Navigate to="/" replace />;
  }

  localStorage.setItem("userId", DEV_DUMMY_USER_ID);
  return <Navigate to="/dashboard" replace />;
}
