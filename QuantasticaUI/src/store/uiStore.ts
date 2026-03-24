import { create } from "zustand";
import { persist } from "zustand/middleware";

export type ThemePreference = "light" | "dark";

function applyClass(isDark: boolean) {
  document.documentElement.classList.toggle("dark", isDark);
}

export const useUiStore = create(
  persist<{
    theme: ThemePreference;
    toggleTheme: () => void;
    setTheme: (t: ThemePreference) => void;
  }>(
    (set, get) => ({
      theme: "light",
      toggleTheme: () => {
        const next: ThemePreference = get().theme === "light" ? "dark" : "light";
        applyClass(next === "dark");
        set({ theme: next });
      },
      setTheme: (t) => {
        applyClass(t === "dark");
        set({ theme: t });
      },
    }),
    {
      name: "quantastica-ui-theme",
      onRehydrateStorage: () => (state) => {
        if (state?.theme === "dark") applyClass(true);
        else applyClass(false);
      },
    },
  ),
);
