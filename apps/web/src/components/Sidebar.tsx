import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  Home,
  Newspaper,
  Users,
  Shield,
  BarChart,
  FileText,
  Calendar,
  User,
  Menu,
  X,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  Mail,
} from "lucide-react";

const COLLAPSED_KEY = "quantastica-sidebar-collapsed";

const navItems = [
  { name: "Dashboard", icon: Home, path: "/dashboard" },
  { name: "Insights", icon: Sparkles, path: "/insights" },
  { name: "News Analysis", icon: Newspaper, path: "/news" },
  { name: "Group Investments", icon: Users, path: "/group-investments" },
  { name: "Risk Analyzer", icon: Shield, path: "/investments" },
  { name: "Finance Tracker", icon: BarChart, path: "/finance-tracker" },
  { name: "Tax Advisor", icon: FileText, path: "/tax-advisor" },
  { name: "Family Finance", icon: User, path: "/family-finance" },
  { name: "Trade Execution", icon: Calendar, path: "/trade-execution" },
];

export default function Sidebar() {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    try {
      setCollapsed(localStorage.getItem(COLLAPSED_KEY) === "1");
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem(COLLAPSED_KEY, collapsed ? "1" : "0");
    } catch {
      /* ignore */
    }
  }, [collapsed]);

  const toggleCollapsed = () => setCollapsed((c) => !c);

  return (
    <>
      <button
        type="button"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="fixed left-4 top-4 z-50 flex h-10 w-10 items-center justify-center rounded-xl border border-border bg-card text-foreground shadow-sm transition hover:bg-muted/70 md:hidden"
        aria-label="Toggle sidebar"
      >
        {sidebarOpen ? <X className="h-5 w-5" strokeWidth={1.75} /> : <Menu className="h-5 w-5" strokeWidth={1.75} />}
      </button>

      <button
        type="button"
        aria-label="Close menu"
        className={`fixed inset-0 z-30 bg-background/50 backdrop-blur-[1px] transition-opacity duration-300 md:hidden ${
          sidebarOpen ? "pointer-events-auto opacity-100" : "pointer-events-none opacity-0"
        }`}
        onClick={() => setSidebarOpen(false)}
      />

      <div
        className={`
          fixed left-0 top-0 z-40 flex h-[100dvh] max-h-[100dvh] flex-col pt-14 transition-[width] duration-300 ease-out
          md:relative md:z-0 md:translate-x-0 md:pt-0 md:transition-[width]
          ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
          ${collapsed ? "md:w-[4.5rem]" : "md:w-[15.5rem]"}
          w-[min(16rem,calc(100vw-1.25rem))]
        `}
      >
        <aside className="relative h-full w-full overflow-hidden border-r border-border/80 bg-card/40 shadow-[inset_-1px_0_0_0] shadow-border/30 dark:bg-card/25 dark:shadow-border/20">
          {/* Restrained texture: fine line grid */}
          <div
            className="pointer-events-none absolute inset-0 opacity-[0.35] dark:opacity-[0.2]"
            style={{
              backgroundImage: `linear-gradient(to right, hsl(var(--border) / 0.35) 1px, transparent 1px),
                linear-gradient(to bottom, hsl(var(--border) / 0.35) 1px, transparent 1px)`,
              backgroundSize: "24px 24px",
            }}
            aria-hidden
          />
          {/* Single vertical accent — editorial detail */}
          <div
            className="pointer-events-none absolute inset-y-0 left-0 w-px bg-gradient-to-b from-transparent via-foreground/12 to-transparent dark:via-foreground/18"
            aria-hidden
          />

          <div className="relative flex h-full min-h-0 flex-col px-3 pb-4 pt-4 md:px-3 md:pb-5 md:pt-6">
            <div className={`shrink-0 ${collapsed ? "md:flex md:justify-center" : ""}`}>
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-border/80 bg-background/80 shadow-sm dark:bg-background/50">
                  <span className="font-mono text-sm font-bold tabular-nums tracking-tighter text-foreground">Q</span>
                </div>
                <div className={`min-w-0 ${collapsed ? "md:hidden" : ""}`}>
                  <p className="text-[0.65rem] font-medium uppercase tracking-[0.18em] text-muted-foreground">Workspace</p>
                  <h1 className="mt-0.5 font-semibold leading-none tracking-tight text-foreground">Quantastica</h1>
                </div>
              </div>
            </div>

            <div className="mt-6 shrink-0">
              <div
                className={`rounded-xl border border-border/70 bg-background/60 p-3.5 dark:bg-background/40 ${
                  collapsed ? "md:hidden" : ""
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-medium text-foreground">Trial</span>
                  <span className="rounded border border-border/80 bg-muted/50 px-1.5 py-0.5 text-[0.6rem] font-medium uppercase tracking-wide text-muted-foreground">
                    Pro
                  </span>
                </div>
                <p className="mt-1.5 text-[0.7rem] text-muted-foreground">20 days remaining</p>
                <div className="mt-2.5 h-1 overflow-hidden rounded-full bg-muted">
                  <div className="h-full w-[72%] rounded-full bg-foreground/25 dark:bg-foreground/35" aria-hidden />
                </div>
              </div>
              {collapsed && (
                <div
                  className="mx-auto mt-3 hidden h-10 w-10 items-center justify-center rounded-lg border border-border/70 bg-background/60 text-[0.65rem] font-medium tabular-nums text-muted-foreground md:flex"
                  title="Trial — 20 days left"
                >
                  20d
                </div>
              )}
            </div>

            <nav
              className="mt-6 min-h-0 flex-1 overflow-x-hidden overflow-y-auto py-0.5 [scrollbar-width:thin]"
              aria-label="Main"
            >
              <p className={`mb-2 px-0.5 text-[0.6rem] font-medium uppercase tracking-[0.16em] text-muted-foreground ${collapsed ? "md:sr-only" : ""}`}>
                Menu
              </p>
              <ul className="space-y-0.5 pr-0.5">
                {navItems.map((item) => {
                  const isActive = location.pathname === item.path;
                  return (
                    <li key={item.name}>
                      <Link
                        to={item.path}
                        title={collapsed ? item.name : undefined}
                        onClick={() => setSidebarOpen(false)}
                        className={`
                          group flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-[0.8125rem] font-medium transition-colors
                          ${collapsed ? "md:justify-center md:px-2" : ""}
                          ${
                            isActive
                              ? "bg-foreground/[0.06] text-foreground dark:bg-foreground/[0.09]"
                              : "text-muted-foreground hover:bg-muted/60 hover:text-foreground"
                          }
                        `}
                      >
                        <span
                          className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-md border transition-colors ${
                            isActive
                              ? "border-border/80 bg-background/90 text-foreground dark:bg-background/60"
                              : "border-transparent bg-transparent text-muted-foreground group-hover:border-border/60 group-hover:bg-muted/50"
                          }`}
                        >
                          <item.icon className="h-[15px] w-[15px]" strokeWidth={2} />
                        </span>
                        <span className={`min-w-0 flex-1 truncate ${collapsed ? "md:sr-only" : ""}`}>{item.name}</span>
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </nav>

            <div className="mt-auto shrink-0 border-t border-border/60 pt-4 dark:border-border/50">
              <button
                type="button"
                className={`flex w-full items-center justify-center gap-2 rounded-lg border border-border/80 bg-background/70 py-2 text-[0.8125rem] font-medium text-foreground transition hover:bg-muted/60 dark:bg-background/40 ${
                  collapsed ? "md:px-0" : ""
                }`}
                title="Contact sales"
              >
                <Mail className={`h-4 w-4 shrink-0 text-muted-foreground ${collapsed ? "md:inline" : "hidden"}`} aria-hidden />
                <span className={collapsed ? "md:sr-only" : ""}>Contact sales</span>
              </button>
            </div>
          </div>
        </aside>

        {/* Hanging collapse control — straddles sidebar / main, between logo block and scrollable menu */}
        <button
          type="button"
          onClick={toggleCollapsed}
          className="absolute right-0 top-[7.25rem] z-50 hidden h-9 w-9 -translate-y-1/2 translate-x-1/2 items-center justify-center rounded-full border border-border bg-background text-muted-foreground shadow-md ring-4 ring-background transition hover:bg-muted/80 hover:text-foreground dark:bg-card dark:ring-card md:flex"
          aria-expanded={!collapsed}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronRight className="h-4 w-4" strokeWidth={2} /> : <ChevronLeft className="h-4 w-4" strokeWidth={2} />}
        </button>
      </div>
    </>
  );
}
