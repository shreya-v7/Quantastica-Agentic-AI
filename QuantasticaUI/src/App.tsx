import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import NewsAnalysisPage from './components/NewsAnalysis';
import GroupInvestmentsPage from './components/GroupInvestments';
import FinanceTracker from './components/FinanceTracker';
import InvestmentsPage from './components/Investments';
import FamilyFinancePage from './components/FamilyFinance';
import LandingPage from './components/LandingPage';
import FinanceExpense from './components/FinanceExpense';
import ChatInterface from './components/ChatInterface';
import AuthPage from './components/AuthPage';
import TradeExecution from './components/TradeExecution';

function LayoutWrapper() {
  const location = useLocation();

  // Determine if we are on the landing page
  const hideSidebar = location.pathname === '/' || location.pathname === '/auth';

  return (
    <div className="flex min-h-screen bg-background text-foreground">
      {!hideSidebar && <Sidebar />}
      <main className="flex-1 p-6 md:p-10 overflow-auto">
        <Routes>
          <Route path='/' element={<LandingPage />} />
          <Route path="/auth" element={<AuthPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/chat" element={<ChatInterface />} />
          <Route path="/news" element={<NewsAnalysisPage />} />
          <Route path="/group-investments" element={<GroupInvestmentsPage />} />
          <Route path='/finance-tracker' element={<FinanceTracker />} />
          <Route path='/investments' element={<InvestmentsPage />} />
          <Route path='/family-finance' element={<FamilyFinancePage />} />
          <Route path='/finance-expense' element={<FinanceExpense />} />
          <Route path='/trade-execution' element={<TradeExecution />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <Router>
      <LayoutWrapper />
    </Router>
  );
}

export default App;
