import type { ReactNode } from "react";
import { useLocation } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { ToggleTheme } from "../components/ToggleTheme";
import { ChatDock } from "../components/ChatDock";
import { useRehydrateTheme } from "../hooks/useRehydrateTheme";

type AppLayoutProps = {
  children: ReactNode;
};

export function AppLayout({ children }: AppLayoutProps) {
  useRehydrateTheme();
  const location = useLocation();

  const hideChrome =
    location.pathname === "/" ||
    location.pathname === "/auth" ||
    location.pathname === "/dev/session";

  if (hideChrome) {
    return <>{children}</>;
  }

  return (
    <div className="flex h-[100dvh] max-h-[100dvh] overflow-hidden bg-background text-foreground">
      <Sidebar />
      <div className="relative flex min-h-0 min-w-0 flex-1 flex-col bg-gradient-to-b from-background via-background to-surface/35 dark:to-surface/20">
        <header className="z-30 flex shrink-0 items-center justify-end gap-3 border-b border-border/50 bg-background/85 px-4 py-3.5 backdrop-blur-xl supports-[backdrop-filter]:bg-background/70 md:px-8">
          <ToggleTheme />
        </header>
        <main className="relative min-h-0 flex-1 overflow-y-auto overflow-x-hidden px-4 py-6 md:px-10 md:py-10">
          {children}
        </main>
        {location.pathname !== "/chat" && <ChatDock />}
      </div>
    </div>
  );
}
