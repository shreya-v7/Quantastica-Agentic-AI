import { createBrowserRouter } from "react-router-dom";
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

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: "chat", element: <ChatPage /> },
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
      { path: "platform", element: <PlatformPage /> },
      { path: "signin", element: <SignInPage /> },
    ],
  },
]);
