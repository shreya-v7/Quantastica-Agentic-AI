import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  BarChart3,
  LayoutDashboard,
  Menu,
  MessageSquare,
  Play,
  Server,
  Target,
  UserCircle,
  X,
} from "lucide-react";
import { useState } from "react";
import type { ComponentType } from "react";
import { BrandMark, Disclaimer } from "./Disclaimer";
import { IstClock, LiveDot } from "./ui";
import { ThemeToggle } from "./ThemeToggle";
import { getAccessToken, setAccessToken } from "../lib/api";

const PRIMARY: { to: string; label: string; icon: ComponentType<{ className?: string }> }[] = [
  { to: "/desk", label: "Desk", icon: LayoutDashboard },
  { to: "/ask", label: "Ask", icon: MessageSquare },
  { to: "/planning", label: "Planning", icon: Target },
  { to: "/profile", label: "Profile", icon: UserCircle },
];

function linkClass(active: boolean) {
  return `flex items-center gap-3 border-l-2 px-3 py-2 text-[13px] transition ${
    active
      ? "border-pine-500 bg-ink-100 text-ink-900"
      : "border-transparent text-ink-500 hover:border-ink-200 hover:bg-ink-50 hover:text-ink-900"
  }`;
}

function NavList({
  items,
  onNavigate,
}: {
  items: typeof PRIMARY;
  onNavigate?: () => void;
}) {
  return (
    <nav className="space-y-1">
      {items.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          onClick={onNavigate}
          className={({ isActive }) => linkClass(isActive)}
        >
          <Icon className="h-4 w-4" />
          {label}
        </NavLink>
      ))}
    </nav>
  );
}

function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  const signedIn = Boolean(getAccessToken());
  const navigate = useNavigate();

  return (
    <div className="flex h-full flex-col">
      <div className="mb-8 px-2">
        <NavLink to="/" onClick={onNavigate}>
          <BrandMark />
        </NavLink>
        <p className="mt-2 flex items-center gap-2 px-1 font-mono text-[10px] uppercase tracking-label text-pine-500">
          <LiveDot /> desk
        </p>
      </div>
      <NavList items={PRIMARY} onNavigate={onNavigate} />
      <div className="mt-auto space-y-3 pt-8">
        <NavLink
          to="/demo"
          onClick={onNavigate}
          className={({ isActive }) => `${linkClass(isActive)} text-xs`}
        >
          <Play className="h-4 w-4" />
          Demo
        </NavLink>
        <NavLink
          to="/metrics"
          onClick={onNavigate}
          className={({ isActive }) => `${linkClass(isActive)} text-xs`}
        >
          <BarChart3 className="h-4 w-4" />
          Metrics
        </NavLink>
        <NavLink
          to="/operators"
          onClick={onNavigate}
          className={({ isActive }) => `${linkClass(isActive)} text-xs`}
        >
          <Server className="h-4 w-4" />
          Operators
        </NavLink>
        {signedIn ? (
          <button
            className="w-full px-3 py-2 text-left text-[13px] text-ink-500 hover:bg-ink-50 hover:text-ink-900"
            onClick={() => {
              setAccessToken(null);
              onNavigate?.();
              navigate("/");
            }}
          >
            Sign out
          </button>
        ) : (
          <NavLink to="/signin" onClick={onNavigate} className={linkClass(false)}>
            Sign in
          </NavLink>
        )}
        <div className="flex items-center justify-between px-2">
          <IstClock />
          <ThemeToggle />
        </div>
        <Disclaimer className="px-2 text-[10px] text-ink-400" />
      </div>
    </div>
  );
}

export function Layout() {
  const [open, setOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-paper-100 text-ink-900">
      <aside className="hidden w-60 shrink-0 border-r border-ink-200 bg-paper-100 p-5 md:block">
        <Sidebar />
      </aside>
      <div className="flex min-w-0 flex-1 flex-col bg-paper-50/40">
        <header className="flex items-center justify-between border-b border-ink-200 px-4 py-3 md:hidden">
          <BrandMark />
          <div className="flex items-center gap-3">
            <ThemeToggle />
            <button
              type="button"
              aria-label={open ? "Close menu" : "Open menu"}
              onClick={() => setOpen((v) => !v)}
              className="p-2 text-ink-700"
            >
              {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </header>
        {open && (
          <div className="border-b border-ink-200 bg-paper-100 p-5 md:hidden">
            <Sidebar onNavigate={() => setOpen(false)} />
          </div>
        )}
        <main className="flex-1 px-4 py-8 md:px-10">
          <div className="mx-auto max-w-6xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
