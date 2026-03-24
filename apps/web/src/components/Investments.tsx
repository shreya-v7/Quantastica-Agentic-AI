import React, { useState } from "react";
import { PieChart, TrendingUp, DollarSign, CreditCard, Home, Briefcase } from "lucide-react";

interface Investment {
  id: number;
  type: "Mutual Fund" | "IPO" | "Stock" | "Real Estate";
  name: string;
  amountInvested: number;
  currentValue: number;
  profitLoss: number;
  expenses?: number;
  loanDue?: number;
}

const sampleInvestments: Investment[] = [
  {
    id: 1,
    type: "Mutual Fund",
    name: "HDFC Equity Fund",
    amountInvested: 120000,
    currentValue: 150000,
    profitLoss: 30000,
    expenses: 1200,
    loanDue: 0,
  },
  {
    id: 2,
    type: "IPO",
    name: "XYZ Ltd IPO",
    amountInvested: 50000,
    currentValue: 70000,
    profitLoss: 20000,
    expenses: 500,
  },
  {
    id: 3,
    type: "Stock",
    name: "TCS",
    amountInvested: 200000,
    currentValue: 185000,
    profitLoss: -15000,
    expenses: 1000,
  },
  {
    id: 4,
    type: "Real Estate",
    name: "Mumbai Apartment",
    amountInvested: 5000000,
    currentValue: 5500000,
    profitLoss: 500000,
    expenses: 25000,
    loanDue: 1000000,
  },
];

export default function InvestmentsPage() {
  const [investments] = useState<Investment[]>(sampleInvestments);

  // Totals
  const totalInvested = investments.reduce((sum, i) => sum + i.amountInvested, 0);
  const totalCurrentValue = investments.reduce((sum, i) => sum + i.currentValue, 0);
  const totalProfitLoss = investments.reduce((sum, i) => sum + i.profitLoss, 0);
  const totalExpenses = investments.reduce((sum, i) => sum + (i.expenses ?? 0), 0);
  const totalLoanDue = investments.reduce((sum, i) => sum + (i.loanDue ?? 0), 0);

  return (
    <div className="min-h-screen max-w-7xl mx-auto p-6 sm:p-10 space-y-10 animate-fade-in">
      <h1 className="text-4xl font-bold flex items-center gap-3 mb-6">
        <Briefcase className="w-8 h-8 text-accent" /> Investments Overview
      </h1>

      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-5 gap-6">
        <SummaryCard title="Total Invested" value={`₹${totalInvested.toLocaleString()}`} icon={<DollarSign />} />
        <SummaryCard title="Current Value" value={`₹${totalCurrentValue.toLocaleString()}`} icon={<TrendingUp />} />
        <SummaryCard
          title="Profit / Loss"
          value={`₹${totalProfitLoss.toLocaleString()}`}
          icon={<PieChart />}
          positive={totalProfitLoss >= 0}
        />
        <SummaryCard title="Total Expenses" value={`₹${totalExpenses.toLocaleString()}`} icon={<CreditCard />} />
        <SummaryCard title="Total Loan Due" value={`₹${totalLoanDue.toLocaleString()}`} icon={<Home />} />
      </div>

      {/* Detailed investments table */}
      <section className="bg-card p-6 rounded-2xl shadow-lg glass">
        <h2 className="text-2xl font-semibold mb-6">Investment Details</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full border-collapse border border-border rounded-md">
            <thead>
              <tr className="border-b border-border">
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Amount Invested</th>
                <th className="px-4 py-3">Current Value</th>
                <th className="px-4 py-3">Profit / Loss</th>
                <th className="px-4 py-3">Expenses</th>
                <th className="px-4 py-3">Loan Due</th>
              </tr>
            </thead>
            <tbody>
              {investments.map((inv) => {
                const profitClass = inv.profitLoss >= 0 ? "text-green-400" : "text-red-500";
                return (
                  <tr
                    key={inv.id}
                    className="border-b border-border hover:bg-accent/20 transition cursor-pointer"
                  >
                    <td className="px-4 py-3 capitalize">{inv.type}</td>
                    <td className="px-4 py-3 font-semibold">{inv.name}</td>
                    <td className="px-4 py-3">₹{inv.amountInvested.toLocaleString()}</td>
                    <td className="px-4 py-3">₹{inv.currentValue.toLocaleString()}</td>
                    <td className={`px-4 py-3 font-semibold ${profitClass}`}>
                      ₹{inv.profitLoss.toLocaleString()}
                    </td>
                    <td className="px-4 py-3">₹{(inv.expenses ?? 0).toLocaleString()}</td>
                    <td className="px-4 py-3">₹{(inv.loanDue ?? 0).toLocaleString()}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function SummaryCard({
  title,
  value,
  icon,
  positive = true,
}: {
  title: string;
  value: string;
  icon: React.ReactNode;
  positive?: boolean;
}) {
  return (
    <div
      className={`group bg-card rounded-xl p-6 shadow-lg border border-border flex flex-col gap-3 hover:shadow-accent hover:-translate-y-1 hover:scale-105 transition-transform duration-300 cursor-default glass`}
    >
      <div className="flex items-center gap-3">{icon}</div>
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className={`text-2xl font-bold ${positive ? "text-green-400" : "text-red-500"}`}>{value}</p>
    </div>
  );
}
