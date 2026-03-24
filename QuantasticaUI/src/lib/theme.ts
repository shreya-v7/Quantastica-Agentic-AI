export const theme = {
  light: {
    bg: "#ffffff",
    text: "#0f172a",
    primary: "#2563eb",
    gradient: "linear-gradient(135deg, #3b82f6, #1e3a8a)",
  },
  dark: {
    bg: "#020617",
    text: "#e2e8f0",
    primary: "#3b82f6",
    gradient: "linear-gradient(135deg, #1e3a8a, #020617)",
  },
} as const;

export type ThemeMode = keyof typeof theme;
