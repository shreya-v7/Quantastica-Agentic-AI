import React, { useState } from "react";
import {
  Users,
  Home,
  PlusCircle,
  PieChart,
  AlarmClock,
  Target,
  FileDown,
} from "lucide-react";
import {
  ResponsiveContainer,
  PieChart as RePieChart,
  Pie,
  Cell,
  Tooltip,
} from "recharts";

const COLORS = ["#00C49F", "#FFBB28", "#FF8042", "#0088FE"];

const mockFamily = [
  { id: 1, name: "Riya Patel", role: "Mother", contribution: 35000 },
  { id: 2, name: "Arjun Patel", role: "Father", contribution: 50000 },
  { id: 3, name: "Ishaan Patel", role: "Son", contribution: 12000 },
];

const expenseCategories = [
  { name: "Groceries", value: 15000 },
  { name: "Utilities", value: 7000 },
  { name: "Education", value: 18000 },
  { name: "Loans", value: 10000 },
];

const FamilyFinancePage: React.FC = () => {
  const [family, setFamily] = useState(mockFamily);
  const [newMember, setNewMember] = useState({
    name: "",
    role: "",
    contribution: "",
  });
  const [budget] = useState(150000);
  const [goal] = useState(200000);

  const totalContribution = family.reduce((sum, f) => sum + f.contribution, 0);
  const remainingBudget = budget - totalContribution;
  const savingsProgress = ((totalContribution / goal) * 100).toFixed(1);

  const addMember = () => {
    if (newMember.name && newMember.role && newMember.contribution) {
      const updated = [
        ...family,
        {
          id: family.length + 1,
          name: newMember.name,
          role: newMember.role,
          contribution: parseInt(newMember.contribution),
        },
      ];
      setFamily(updated);
      setNewMember({ name: "", role: "", contribution: "" });
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground p-4 sm:p-6 md:p-10 space-y-10 animate-fade-in">
      {/* Page header */}
      <div className="text-center">
        <h1 className="mb-3 text-balance text-4xl font-bold tracking-tight text-foreground">
          Family Finance
        </h1>
        <p className="mx-auto max-w-2xl text-sm leading-relaxed text-foreground/80 dark:text-foreground/75 sm:text-base">
          Manage shared expenses, budgeting, and savings goals as a family.
          Transparency builds trust.
        </p>
      </div>

      {/* Add Family Member Card */}
      <div className="bg-card p-6 rounded-2xl shadow-[0_8px_24px_rgba(0,0,0,0.5)] space-y-4 hover:shadow-lg hover:shadow-primary/15 transition-all">
        <h2 className="flex items-center gap-2 text-xl font-semibold text-foreground">
          <PlusCircle className="h-5 w-5 shrink-0 text-primary" aria-hidden /> Add Family Member
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <input
            type="text"
            placeholder="Name"
            value={newMember.name}
            onChange={(e) => setNewMember({ ...newMember, name: e.target.value })}
            className="px-4 py-2 rounded-lg bg-muted text-foreground border border-border focus:outline-none focus:ring-2 focus:ring-accentBlue shadow-inner"
          />
          <input
            type="text"
            placeholder="Role"
            value={newMember.role}
            onChange={(e) => setNewMember({ ...newMember, role: e.target.value })}
            className="px-4 py-2 rounded-lg bg-muted text-foreground border border-border focus:outline-none focus:ring-2 focus:ring-accentBlue shadow-inner"
          />
          <input
            type="number"
            placeholder="Contribution ₹"
            value={newMember.contribution}
            onChange={(e) =>
              setNewMember({ ...newMember, contribution: e.target.value })
            }
            className="px-4 py-2 rounded-lg bg-muted text-foreground border border-border focus:outline-none focus:ring-2 focus:ring-accentBlue shadow-inner"
          />
        </div>
        <button
          onClick={addMember}
          className="mt-2 rounded-lg bg-primary px-6 py-2 text-primary-foreground shadow-lg transition-all hover:scale-105 hover:opacity-95"
        >
          Add Member
        </button>
      </div>

      {/* Family Members List */}
      <div className="bg-card p-6 rounded-2xl shadow-xl space-y-6">
        <h2 className="flex items-center gap-2 text-xl font-semibold text-foreground">
          <Users className="h-5 w-5 shrink-0 text-primary" aria-hidden /> Family Members
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {family.map((member) => (
            <div
              key={member.id}
              className="bg-muted border border-border rounded-xl p-4 shadow-md hover:shadow-lg hover:shadow-primary/15 transition-all hover:scale-[1.02]"
            >
              <p className="font-medium text-lg">{member.name}</p>
              <p className="text-sm text-muted-foreground">{member.role}</p>
              <p className="mt-2 font-semibold text-primary">
                ₹{member.contribution.toLocaleString()}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Budget Overview */}
      <div className="bg-card p-6 rounded-2xl shadow-xl space-y-6">
        <h2 className="flex items-center gap-2 text-xl font-semibold text-foreground">
          <PieChart className="h-5 w-5 shrink-0 text-primary" aria-hidden /> Budget Overview
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
          <div className="text-center">
            <p className="text-foreground text-lg">
              Total Budget: ₹{budget.toLocaleString()}
            </p>
            <p className="text-lg font-medium text-emerald-700 dark:text-emerald-400">
              Remaining Budget: ₹{remainingBudget.toLocaleString()}
            </p>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <RePieChart>
              <Pie
                data={expenseCategories}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={70}
                dataKey="value"
              >
                {expenseCategories.map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </RePieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Savings Goal Progress */}
      <div className="bg-card p-6 rounded-2xl shadow-xl space-y-4">
        <h2 className="flex items-center gap-2 text-xl font-semibold text-foreground">
          <Target className="h-5 w-5 shrink-0 text-primary" aria-hidden /> Savings Goal Progress
        </h2>
        <div className="h-5 w-full rounded-full bg-muted">
          <div
            className="flex h-5 items-center justify-end rounded-full bg-primary pr-2 text-right text-xs font-semibold text-primary-foreground"
            style={{ width: `${savingsProgress}%` }}
          >
            {savingsProgress}%
          </div>
        </div>
        <p className="text-muted-foreground text-sm">Goal: ₹{goal.toLocaleString()}</p>
      </div>

      {/* Summary & Actions */}
      <div className="mx-auto max-w-6xl rounded-2xl border border-border/60 bg-gradient-to-r from-primary/10 via-muted/40 to-primary/5 p-6 text-center shadow-lg dark:from-primary/15 dark:via-muted/20 dark:to-primary/10 md:p-8">
        <div className="mb-2 flex items-center justify-center gap-3 text-foreground">
          <Home className="h-5 w-5 shrink-0 text-primary" aria-hidden />
          <h3 className="text-lg font-semibold">Family Contribution Summary</h3>
        </div>
        <p className="text-xl font-bold text-foreground">
          ₹{totalContribution.toLocaleString()}
        </p>
        <p className="mt-2 text-sm text-foreground/75 dark:text-foreground/70">
          Total shared contributions across all family accounts.
        </p>
        <div className="flex justify-center gap-4 mt-4 flex-wrap">
          <button className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground shadow transition hover:scale-105 hover:opacity-95">
            <AlarmClock className="h-4 w-4" /> Bill Reminder
          </button>
          <button className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground shadow transition hover:scale-105 hover:opacity-95">
            <FileDown className="h-4 w-4" /> Export Data
          </button>
        </div>
      </div>
    </div>
  );
};

export default FamilyFinancePage;
