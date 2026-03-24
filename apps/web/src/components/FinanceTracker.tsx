import React, { useState, useEffect } from "react";
import axios from "axios";
import { DollarSign, BarChart2, TrendingUp, Lightbulb, PlusCircle } from "lucide-react";
import ProfileSection from "./ProfileSection";

interface Transaction {
  id: number;
  type: "investment" | "expense";
  category: string;
  amount: number;
  date: string;
  description?: string;
}


const userId = "1010101010"; // Replace with real userId from context or auth if needed


// Helper to get full month name
const getMonthName = (monthNumber: number) => {
  return new Date(0, monthNumber - 1).toLocaleString('default', { month: 'long' });
};


export default function FinanceTracker() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [newExpense, setNewExpense] = useState({ category: "", amount: "", date: "" });
  const [predictedExpense, setPredictedExpense] = useState<number | null>(null);
  const [predictedSavings, setPredictedSavings] = useState<number | null>(null);
  const [predictedIncome, setPredictedIncome] = useState<number | null>(null);
  const [, setUserProfile] = useState<any>(null);
  const [predictionMonth, setPredictionMonth] = useState<number>(0);
  const [predictionYear, setPredictionYear] = useState<number>(0);
  const [savingRate, setSavingRate] = useState<number>(0);


 useEffect(() => {
  const fetchProfile = async () => {
    try {
      const res = await axios.get(`http://localhost:5001/user/${userId}/profile`);
      setUserProfile(res.data.profile);
    } catch (err) {
      console.error("Failed to fetch profile:", err);
    }
  };
  fetchProfile();
}, []);

  // Fetch transactions from backend
 useEffect(() => {
  const fetchTransactions = async () => {
    try {
      const res = await axios.get(`http://localhost:5001/transactions/${userId}`);
      const data = res.data;

      const mapped: Transaction[] = data.transactions.map((txn: any, index: number) => ({
        id: index + 1,
        type: txn.transaction_type_name === "CREDIT" ? "investment" : "expense",
        category: txn.transaction_narration || "Misc",
        amount: txn.transaction_amount,
        date: txn.transaction_date,
        description: txn.transaction_narration,
      }));

      setTransactions(mapped);
    } catch (err) {
      console.error("Failed to fetch transactions:", err);
    }
  };

  fetchTransactions();
}, []);

useEffect(() => {
  const fetchPredictions = async () => {
    try {
      const today = new Date();
      const res = await axios.post("http://localhost:5001/predict/both", {
        user_id: userId,
        month: today.getMonth() + 1, // JS months are 0-based
        year: today.getFullYear(),
      });
      console.log("Predictions response:", res.data);
      setPredictedExpense(res.data.prediction.expenditure);
      setPredictedSavings(res.data.prediction.savings);
      setPredictedIncome(res.data.prediction.income);
      setPredictionMonth(res.data.prediction.month);
      setPredictionYear(res.data.prediction.year);
      setSavingRate(res.data.prediction.savings_rate);
    } catch (err) {
      console.error("Failed to fetch predictions:", err);
    }
  };
  fetchPredictions();
}, [transactions]);



{/* Recent Transactions */}
<section className="bg-card p-6 rounded-2xl shadow-lg glass max-w-4xl mx-auto animate-slide-up">
  <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
    <BarChart2 className="w-6 h-6 text-accent" /> Recent Transactions
  </h2>
  <ul className="divide-y divide-gray-700">
    {transactions.slice().reverse().map(txn => (
      <li key={txn.id} className="flex justify-between py-3">
        <div>
          <p className="font-medium text-white">{txn.category}</p>
          <p className="text-sm text-gray-400">{new Date(txn.date).toDateString()}</p>
        </div>
        <div className={`text-lg font-semibold ${txn.type === "investment" ? "text-red-500" : "text-green-400"}`}>
          ₹{txn.amount.toLocaleString()}
        </div>
      </li>
    ))}
  </ul>
</section>

  const totalInvestments = transactions
    .filter(t => t.type === "investment")
    .reduce((sum, t) => sum + t.amount, 0);

  const totalExpenses = transactions
    .filter(t => t.type === "expense")
    .reduce((sum, t) => sum + t.amount, 0);

  const expensesByCategory = transactions
    .filter(t => t.type === "expense")
    .reduce<Record<string, number>>((acc, t) => {
      acc[t.category] = (acc[t.category] || 0) + t.amount;
      return acc;
    }, {});

  useEffect(() => {
    const expenses = transactions.filter(t => t.type === "expense");
    if (expenses.length < 2) {
      setPredictedExpense(null);
      return;
    }
    const sorted = [...expenses].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
    const firstDate = new Date(sorted[0].date);
    const lastDate = new Date(sorted[sorted.length - 1].date);
    const diffDays = (lastDate.getTime() - firstDate.getTime()) / (1000 * 60 * 60 * 24);
    if (diffDays <= 0) {
      setPredictedExpense(null);
      return;
    }
    const totalSpent = expenses.reduce((sum, t) => sum + t.amount, 0);
    const avgDaily = totalSpent / diffDays;
    setPredictedExpense(Math.round(avgDaily * 30));
  }, [transactions]);

  const suggestions = Object.entries(expensesByCategory)
    .filter(([_, amount]) => amount > totalExpenses * 0.3)
    .map(([category]) => `Consider reducing your spending on ${category}.`);

  const addExpense = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newExpense.category || !newExpense.amount || !newExpense.date) return;

    const amountNum = Number(newExpense.amount);
    if (isNaN(amountNum) || amountNum <= 0) return;

    setTransactions(prev => [
      ...prev,
      {
        id: prev.length + 1,
        type: "expense",
        category: newExpense.category,
        amount: amountNum,
        date: newExpense.date,
      }
    ]);
    setNewExpense({ category: "", amount: "", date: "" });
  };

  return (
    <div className="min-h-screen bg-darkBlue text-white p-6 sm:p-10 max-w-5xl mx-auto space-y-10 animate-fade-in">
      <h1 className="text-4xl font-bold mb-6 flex items-center gap-3">
        <DollarSign className="w-8 h-8 text-accent" />
        Finance Tracker
      </h1>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <Card title="Total Investments" value={`₹${totalInvestments.toLocaleString()}`} icon={<DollarSign />} />
        <Card title="Total Expenses" value={`₹${totalExpenses.toLocaleString()}`} icon={<BarChart2 />} />
      </div>

      {/* Expense Categories */}
      <section className="bg-[#161b22] p-6 rounded-2xl shadow-lg glass">
        <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
          <BarChart2 className="w-6 h-6 text-accent" /> Expense Breakdown by Category
        </h2>
        <ul className="space-y-2">
          {Object.entries(expensesByCategory).map(([category, amount]) => (
            <li key={category} className="flex justify-between border-b border-gray-700 py-2 hover:bg-accent/20 transition rounded-md px-2 cursor-pointer">
              <span>{category}</span>
              <span>₹{amount.toLocaleString()}</span>
            </li>
          ))}
        </ul>
      </section>

    <section className="bg-gradient-to-r from-accentBlue/50 to-accentPurple/30 p-6 rounded-2xl shadow-xl max-w-4xl mx-auto animate-slide-up text-center text-white">
      <h2 className="text-3xl font-bold flex justify-center items-center gap-3 mb-6">
        <TrendingUp className="w-6 h-6 text-accent" />
        Forecast Summary – {getMonthName(predictionMonth)} {predictionYear}
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 text-lg font-medium">
      
       <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 border border-gray-700 p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 cursor-default">
  <p className="text-xs font-semibold uppercase text-gray-400 tracking-wide mb-1">Predicted Expenditure</p>
  <p className="text-3xl font-extrabold text-red-500 drop-shadow-sm">
    ₹{predictedExpense?.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",")}
  </p>
</div>

<div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 border border-gray-700 p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 cursor-default">
  <p className="text-xs font-semibold uppercase text-gray-400 tracking-wide mb-1">Predicted Savings</p>
  <p className="text-3xl font-extrabold text-emerald-400 drop-shadow-sm">
    ₹{predictedSavings?.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",")}
  </p>
</div>

<div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 border border-gray-700 p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 cursor-default">
  <p className="text-xs font-semibold uppercase text-gray-400 tracking-wide mb-1">Predicted Income</p>
  <p className="text-3xl font-extrabold text-sky-400 drop-shadow-sm">
    ₹{predictedIncome?.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",")}
  </p>
</div>


      </div>

      {/* Savings Rate Bar */}
      <div className="text-left max-w-xl mx-auto">
        <p className="mb-2 text-sm font-semibold">Predicted Savings Rate</p>
        <div className="w-full h-4 bg-white/20 rounded-full overflow-hidden shadow-inner">
          <div
            className="h-full bg-green-400 transition-all duration-500"
            style={{ width: `${savingRate?.toFixed(2) || 0}%` }}
          />
        </div>
        <p className="text-sm mt-2 font-medium">{savingRate?.toFixed(2)}%</p>
      </div>
    </section>



          <section className="bg-card p-6 rounded-2xl shadow-lg glass max-w-4xl mx-auto animate-slide-up">
            <h2 className="text-2xl font-semibold mb-3 flex items-center gap-2">
              <Lightbulb className="w-6 h-6 text-accent" />
              Savings Suggestions
            </h2>
            {suggestions.length > 0 ? (
              <ul className="list-disc pl-6 space-y-2 text-gray-300">
                {suggestions.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            ) : (
              <p>No suggestions at this time. Keep up the good work!</p>
            )}
          </section>

      {/* Profile Section */}

<ProfileSection />

      {/* Add Expense Form */}
      <form onSubmit={addExpense} className="bg-card p-6 rounded-2xl shadow-lg max-w-4xl mx-auto glass space-y-4">
        <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
          <PlusCircle className="w-6 h-6 text-accent" /> Add New Expense
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <input
            type="text"
            placeholder="Category (e.g. Food)"
            className="p-3 rounded-md bg-background border border-gray-700 focus:outline-none focus:ring-2 focus:ring-accent text-white"
            value={newExpense.category}
            onChange={e => setNewExpense({ ...newExpense, category: e.target.value })}
            required
          />
          <input
            type="number"
            placeholder="Amount (₹)"
            className="p-3 rounded-md bg-background border border-gray-700 focus:outline-none focus:ring-2 focus:ring-accent text-white"
            value={newExpense.amount}
            onChange={e => setNewExpense({ ...newExpense, amount: e.target.value })}
            required
            min={1}
          />
          <input
            type="date"
            className="p-3 rounded-md bg-background border border-gray-700 focus:outline-none focus:ring-2 focus:ring-accent text-white"
            value={newExpense.date}
            onChange={e => setNewExpense({ ...newExpense, date: e.target.value })}
            required
          />
        </div>
        <button
          type="submit"
          className="bg-accent text-accent-foreground px-6 py-3 rounded-lg font-semibold hover:scale-105 transition-transform shadow-lg"
        >
          Add Expense
        </button>
      </form>
    </div>
  );
}

function Card({ title, value, icon }: { title: string; value: string; icon: React.ReactNode }) {
  return (
    <div className="group bg-[#161b22] rounded-xl p-6 shadow-lg hover:shadow-accent transition-all border border-gray-700 transform hover:-translate-y-1 hover:scale-105 duration-300 cursor-default">
      <div className="flex items-center gap-3 mb-3">
        {icon}
        <h3 className="text-lg font-semibold group-hover:text-accent transition-colors">{title}</h3>
      </div>
      <p className="text-2xl font-bold mb-2">{value}</p>
    </div>
  );
}
