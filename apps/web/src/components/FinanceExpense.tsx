import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  DollarSign,
  BarChart2,
  TrendingUp,
  Lightbulb,
  PlusCircle,
} from "lucide-react";

interface BackendTransaction {
  id: string;
  date: string;
  description: string;
  amount: number;
  type: "credit" | "debit";
}

interface Transaction {
  id: number;
  type: "investment" | "expense";
  category: string;
  amount: number;
  date: string;
  description?: string;
}

interface TransactionResponse {
  transactions: BackendTransaction[];
}

export default function FinanceTracker() {
  // const { userId } = useParams<{ userId: string }>();
  const userId = 1010101010;
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [newExpense, setNewExpense] = useState({
    category: "",
    amount: "",
    date: "",
  });
  const [predictedExpense, setPredictedExpense] = useState<number | null>(null);
  const [error, setError] = useState("");

  const fetchTransactions = async () => {
    if (!userId) return;
    setError("");
    console.log("Fetching transactions for user:", userId);
    try {
      const res = await axios.get<TransactionResponse>(
        `http://localhost:5001/transactions/${userId}`
      );
      console.log("Fetched transactions:", res.data.transactions);  
      const mapped = res.data.transactions.map((txn) => ({
        id: parseInt(txn.id),
        type: txn.type === "credit" ? "investment" as "investment" : "expense" as "expense",
        category: txn.description || "Misc",
        amount: txn.amount,
        date: txn.date,
        description: txn.description,
      }));
      setTransactions(mapped);
    } catch (err) {
      setError("Unable to fetch transactions.");
    }
  };

  // Initial data fetch
  useEffect(() => {
    fetchTransactions();
  }, [userId]);

  // Calculate totals
  const totalInvestments = transactions
    .filter((t) => t.type === "investment")
    .reduce((sum, t) => sum + t.amount, 0);

  const totalExpenses = transactions
    .filter((t) => t.type === "expense")
    .reduce((sum, t) => sum + t.amount, 0);

  const expensesByCategory = transactions
    .filter((t) => t.type === "expense")
    .reduce<Record<string, number>>((acc, t) => {
      acc[t.category] = (acc[t.category] || 0) + t.amount;
      return acc;
    }, {});

  useEffect(() => {
    const expenses = transactions.filter((t) => t.type === "expense");
    if (expenses.length < 2) {
      setPredictedExpense(null);
      return;
    }
    const sorted = expenses.sort(
      (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
    );
    const firstDate = new Date(sorted[0].date);
    const lastDate = new Date(sorted[sorted.length - 1].date);
    const diffDays =
      (lastDate.getTime() - firstDate.getTime()) / (1000 * 60 * 60 * 24);
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

    setTransactions((prev) => [
      ...prev,
      {
        id: prev.length + 1,
        type: "expense",
        category: newExpense.category,
        amount: amountNum,
        date: newExpense.date,
      },
    ]);
    setNewExpense({ category: "", amount: "", date: "" });
  };

  return (
    <div className="min-h-screen bg-background text-foreground p-6 sm:p-10 max-w-5xl mx-auto space-y-10 animate-fade-in">
      <h1 className="text-4xl font-bold mb-6 flex items-center gap-3">
        <DollarSign className="w-8 h-8 text-accent" />
        Finance Tracker
      </h1>

      {error && <div className="text-red-500">{error}</div>}

      {/* Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <Card
          title="Total Investments"
          value={`₹${totalInvestments.toLocaleString()}`}
          icon={<DollarSign />}
        />
        <Card
          title="Total Expenses"
          value={`₹${totalExpenses.toLocaleString()}`}
          icon={<BarChart2 />}
        />
      </div>

      {/* Expense Categories */}
      <section className="bg-card p-6 rounded-2xl shadow-lg glass">
        <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
          <BarChart2 className="w-6 h-6 text-accent" /> Expense Breakdown by
          Category
        </h2>
        <ul className="space-y-2">
          {Object.entries(expensesByCategory).map(([category, amount]) => (
            <li
              key={category}
              className="flex justify-between border-b border-border py-2 hover:bg-accent/20 transition rounded-md px-2 cursor-pointer"
            >
              <span>{category}</span>
              <span>₹{amount.toLocaleString()}</span>
            </li>
          ))}
        </ul>
      </section>

      {/* Prediction */}
      <section className="bg-gradient-to-r from-accentBlue/40 to-accentPurple/30 p-6 rounded-2xl shadow-lg max-w-4xl mx-auto animate-slide-up text-center">
        <h2 className="text-2xl font-semibold flex justify-center items-center gap-3 mb-2">
          <TrendingUp className="w-6 h-6 text-accent" />
          Predicted Expenses Next Month
        </h2>
        {predictedExpense !== null ? (
          <p className="text-lg font-bold">
            ₹{predictedExpense.toLocaleString()}
          </p>
        ) : (
          <p className="text-muted-foreground">
            Insufficient data to predict expenses
          </p>
        )}
      </section>

      {/* Suggestions */}
      <section className="bg-card p-6 rounded-2xl shadow-lg glass max-w-4xl mx-auto animate-slide-up">
        <h2 className="text-2xl font-semibold mb-3 flex items-center gap-2">
          <Lightbulb className="w-6 h-6 text-accent" />
          Savings Suggestions
        </h2>
        {suggestions.length > 0 ? (
          <ul className="list-disc pl-6 space-y-2 text-card-foreground">
            {suggestions.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        ) : (
          <p>No suggestions at this time. Keep up the good work!</p>
        )}
      </section>

      {/* Add Expense Form */}
      <form
        onSubmit={addExpense}
        className="bg-card p-6 rounded-2xl shadow-lg max-w-4xl mx-auto glass space-y-4"
      >
        <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
          <PlusCircle className="w-6 h-6 text-accent" /> Add New Expense
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <input
            type="text"
            placeholder="Category (e.g. Food)"
            className="p-3 rounded-md bg-background border border-border focus:outline-none focus:ring-2 focus:ring-primary text-foreground"
            value={newExpense.category}
            onChange={(e) =>
              setNewExpense({ ...newExpense, category: e.target.value })
            }
            required
          />
          <input
            type="number"
            placeholder="Amount (₹)"
            className="p-3 rounded-md bg-background border border-border focus:outline-none focus:ring-2 focus:ring-primary text-foreground"
            value={newExpense.amount}
            onChange={(e) =>
              setNewExpense({ ...newExpense, amount: e.target.value })
            }
            required
            min={1}
          />
          <input
            type="date"
            className="p-3 rounded-md bg-background border border-border focus:outline-none focus:ring-2 focus:ring-primary text-foreground"
            value={newExpense.date}
            onChange={(e) =>
              setNewExpense({ ...newExpense, date: e.target.value })
            }
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

function Card({
  title,
  value,
  icon,
}: {
  title: string;
  value: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="group bg-card rounded-xl p-6 shadow-lg hover:shadow-accent transition-all border border-border transform hover:-translate-y-1 hover:scale-105 duration-300 cursor-default">
      <div className="flex items-center gap-3 mb-3">
        {icon}
        <h3 className="text-lg font-semibold group-hover:text-accent transition-colors">
          {title}
        </h3>
      </div>
      <p className="text-2xl font-bold mb-2">{value}</p>
    </div>
  );
}
