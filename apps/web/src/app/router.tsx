import { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";
import { AppLayout } from "./layout";
import { RequireAuth } from "./RequireAuth";
import DevSessionEntry from "./DevSessionEntry";

const LandingPage = lazy(() => import("../components/LandingPage"));
const AuthPage = lazy(() => import("../components/AuthPage"));
const DashboardPage = lazy(() => import("../features/dashboard/DashboardPage"));
const InsightsPage = lazy(() => import("../features/insights/InsightsPage"));
const ChatPage = lazy(() => import("../features/chat/ChatPage"));
const NewsAnalysisPage = lazy(() => import("../components/NewsAnalysis"));
const GroupInvestmentsPage = lazy(() => import("../components/GroupInvestments"));
const FinanceTracker = lazy(() => import("../components/FinanceTracker"));
const InvestmentsPage = lazy(() => import("../components/Investments"));
const FamilyFinancePage = lazy(() => import("../components/FamilyFinance"));
const FinanceExpense = lazy(() => import("../components/FinanceExpense"));
const TradeExecution = lazy(() => import("../components/TradeExecution"));

function PageFallback() {
  return (
    <div className="flex min-h-[50vh] items-center justify-center p-8">
      <div className="h-14 w-56 rounded-2xl fi-shimmer" aria-hidden />
    </div>
  );
}

export function AppRouter() {
  return (
    <AppLayout>
      <Suspense fallback={<PageFallback />}>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/auth" element={<AuthPage />} />
          <Route path="/dev/session" element={<DevSessionEntry />} />
          <Route
            path="/dashboard"
            element={
              <RequireAuth>
                <DashboardPage />
              </RequireAuth>
            }
          />
          <Route
            path="/insights"
            element={
              <RequireAuth>
                <InsightsPage />
              </RequireAuth>
            }
          />
          <Route
            path="/chat"
            element={
              <RequireAuth>
                <ChatPage />
              </RequireAuth>
            }
          />
          <Route
            path="/news"
            element={
              <RequireAuth>
                <NewsAnalysisPage />
              </RequireAuth>
            }
          />
          <Route
            path="/group-investments"
            element={
              <RequireAuth>
                <GroupInvestmentsPage />
              </RequireAuth>
            }
          />
          <Route
            path="/finance-tracker"
            element={
              <RequireAuth>
                <FinanceTracker />
              </RequireAuth>
            }
          />
          <Route
            path="/investments"
            element={
              <RequireAuth>
                <InvestmentsPage />
              </RequireAuth>
            }
          />
          <Route
            path="/family-finance"
            element={
              <RequireAuth>
                <FamilyFinancePage />
              </RequireAuth>
            }
          />
          <Route
            path="/finance-expense"
            element={
              <RequireAuth>
                <FinanceExpense />
              </RequireAuth>
            }
          />
          <Route
            path="/trade-execution"
            element={
              <RequireAuth>
                <TradeExecution />
              </RequireAuth>
            }
          />
        </Routes>
      </Suspense>
    </AppLayout>
  );
}
