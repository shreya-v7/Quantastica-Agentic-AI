import { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";
import { AppLayout } from "./layout";

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
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/insights" element={<InsightsPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/news" element={<NewsAnalysisPage />} />
          <Route path="/group-investments" element={<GroupInvestmentsPage />} />
          <Route path="/finance-tracker" element={<FinanceTracker />} />
          <Route path="/investments" element={<InvestmentsPage />} />
          <Route path="/family-finance" element={<FamilyFinancePage />} />
          <Route path="/finance-expense" element={<FinanceExpense />} />
          <Route path="/trade-execution" element={<TradeExecution />} />
        </Routes>
      </Suspense>
    </AppLayout>
  );
}
