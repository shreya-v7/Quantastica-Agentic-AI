import { createBrowserRouter } from "react-router-dom";
import { Layout } from "./components/Layout";
import { DashboardPage } from "./pages/DashboardPage";
import { PortfoliosPage } from "./pages/PortfoliosPage";
import { PortfolioDetailPage } from "./pages/PortfolioDetailPage";
import { AgentsPage } from "./pages/AgentsPage";
import { InsightsPage } from "./pages/InsightsPage";
import { PlatformPage } from "./pages/PlatformPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: "portfolios", element: <PortfoliosPage /> },
      { path: "portfolios/:id", element: <PortfolioDetailPage /> },
      { path: "agents", element: <AgentsPage /> },
      { path: "insights", element: <InsightsPage /> },
      { path: "platform", element: <PlatformPage /> },
    ],
  },
]);
