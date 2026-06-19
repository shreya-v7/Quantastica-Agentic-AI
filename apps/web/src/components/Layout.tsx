import { NavLink, Outlet } from "react-router-dom";
import {
  Activity,
  Bell,
  Bot,
  CandlestickChart,
  LayoutDashboard,
  Lightbulb,
  LogIn,
  MessageSquare,
  Server,
  ShieldCheck,
  Target,
  TrendingUp,
  UserCircle,
  Wallet,
} from "lucide-react";
import type { ComponentType } from "react";

const NAV: { to: string; label: string; icon: ComponentType<{ className?: string }> }[] = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/chat", label: "Ask", icon: MessageSquare },
  { to: "/markets", label: "Markets", icon: CandlestickChart },
  { to: "/profile", label: "Profile", icon: UserCircle },
  { to: "/portfolios", label: "Portfolios", icon: Wallet },
  { to: "/agents", label: "Agents", icon: Activity },
  { to: "/insights", label: "Insights", icon: Lightbulb },
  { to: "/planning", label: "Planning", icon: Target },
  { to: "/match", label: "Match", icon: ShieldCheck },
  { to: "/trades", label: "Trades", icon: TrendingUp },
  { to: "/automation", label: "Automation", icon: Bot },
  { to: "/alerts", label: "Alerts", icon: Bell },
  { to: "/platform", label: "Platform", icon: Server },
  { to: "/signin", label: "Sign in", icon: LogIn },
];

export function Layout() {
  return (
    <div className="flex min-h-screen bg-ink-50 text-ink-900">
      <aside className="hidden w-60 shrink-0 border-r border-ink-200 bg-white p-4 md:block">
        <div className="mb-8 px-2">
          <p className="text-lg font-semibold">Quantastica</p>
          <p className="text-xs text-ink-400">Agentic financial intelligence</p>
        </div>
        <nav className="space-y-1">
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
                  isActive ? "bg-brand-50 text-brand-700" : "text-ink-500 hover:bg-ink-100"
                }`
              }
            >
              <Icon className="h-4 w-4" />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="flex-1 px-6 py-8 md:px-10">
        <div className="mx-auto max-w-6xl">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
