import { createBrowserRouter, Navigate } from "react-router-dom";
import { Layout } from "./components/Layout";
import { DashboardPage } from "./pages/DashboardPage";
import { PortfoliosPage } from "./pages/PortfoliosPage";
import { PortfolioDetailPage } from "./pages/PortfolioDetailPage";
import { AgentsPage } from "./pages/AgentsPage";
import { InsightsPage } from "./pages/InsightsPage";
import { PlatformPage } from "./pages/PlatformPage";
import { ChatPage } from "./pages/ChatPage";
import { MarketsPage } from "./pages/MarketsPage";
import { GoalsPage } from "./pages/GoalsPage";
import { MatchPage } from "./pages/MatchPage";
import { TradesPage } from "./pages/TradesPage";
import { AutomationPage } from "./pages/AutomationPage";
import { AlertsPage } from "./pages/AlertsPage";
import { ProfilePage } from "./pages/ProfilePage";
import { SignInPage } from "./pages/SignInPage";
import { LandingPage } from "./pages/LandingPage";
import { DemoPage } from "./pages/DemoPage";
import { MetricsPage } from "./pages/MetricsPage";

export const router = createBrowserRouter([
  { path: "/", element: <LandingPage /> },
  { path: "/signin", element: <SignInPage /> },
  {
    element: <Layout />,
    children: [
      { path: "desk", element: <DashboardPage /> },
      { path: "ask", element: <ChatPage /> },
      { path: "chat", element: <Navigate to="/ask" replace /> },
      { path: "markets", element: <MarketsPage /> },
      { path: "profile", element: <ProfilePage /> },
      { path: "portfolios", element: <PortfoliosPage /> },
      { path: "portfolios/:id", element: <PortfolioDetailPage /> },
      { path: "agents", element: <AgentsPage /> },
      { path: "insights", element: <InsightsPage /> },
      { path: "planning", element: <GoalsPage /> },
      { path: "match", element: <MatchPage /> },
      { path: "trades", element: <TradesPage /> },
      { path: "automation", element: <AutomationPage /> },
      { path: "alerts", element: <AlertsPage /> },
      { path: "operators", element: <PlatformPage /> },
      { path: "metrics", element: <MetricsPage /> },
      { path: "demo", element: <DemoPage /> },
      { path: "platform", element: <Navigate to="/operators" replace /> },
    ],
  },
]);
