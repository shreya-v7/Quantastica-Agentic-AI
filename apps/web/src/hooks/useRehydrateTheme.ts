import { useEffect } from "react";
import { useUiStore } from "../store/uiStore";

/** Ensures persisted theme applies after Zustand rehydration (client-only). */
export function useRehydrateTheme() {
  const theme = useUiStore((s) => s.theme);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);
}
