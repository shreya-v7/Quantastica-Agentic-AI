import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";
import { applyTheme, readTheme, toggleTheme, type Theme } from "../lib/theme";

export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>("dark");

  useEffect(() => {
    const current = readTheme();
    applyTheme(current);
    setTheme(current);
  }, []);

  const toLight = theme === "dark";

  return (
    <button
      type="button"
      onClick={() => setTheme(toggleTheme())}
      className="p-1.5 text-ink-400 hover:text-ink-900"
      aria-label={toLight ? "Switch to light mode" : "Switch to dark mode"}
    >
      {toLight ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
    </button>
  );
}
