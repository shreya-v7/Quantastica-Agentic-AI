import type { ReactNode } from "react";
import { useLocation } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { ToggleTheme } from "../components/ToggleTheme";
import { useRehydrateTheme } from "../hooks/useRehydrateTheme";

type AppLayoutProps = {
  children: ReactNode;
};

export function AppLayout({ children }: AppLayoutProps) {
  useRehydrateTheme();
  const location = useLocation();
  const hideChrome = location.pathname === "/" || location.pathname === "/auth";

  if (hideChrome) {
    return <>{children}</>;
  }

  return (
    <div className="flex min-h-screen bg-background text-foreground">
      <Sidebar />
      <div className="flex min-h-screen flex-1 flex-col md:pl-0">
        <header className="sticky top-0 z-30 flex items-center justify-end gap-3 border-b border-border/60 bg-background/80 px-4 py-3 backdrop-blur-md md:px-8">
          <ToggleTheme />
        </header>
        <main className="flex-1 overflow-auto px-4 py-6 md:px-8 md:py-8">{children}</main>
      </div>
    </div>
  );
}
