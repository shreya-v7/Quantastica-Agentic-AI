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
    <div className="min-h-screen bg-darkBlue text-white p-4 sm:p-6 md:p-10 space-y-10 animate-fade-in">
      {/* Page header */}
      <div className="text-center">
        <h1 className="text-4xl font-extrabold mb-3 text-accent drop-shadow-lg">
          Family Finance
        </h1>
        <p className="text-gray-400 max-w-2xl mx-auto text-sm sm:text-base">
          Manage shared expenses, budgeting, and savings goals as a family.
          Transparency builds trust.
        </p>
      </div>

      {/* Add Family Member Card */}
      <div className="bg-[#161b22] p-6 rounded-2xl shadow-[0_8px_24px_rgba(0,0,0,0.5)] space-y-4 hover:shadow-accentBlue transition-all">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <PlusCircle className="text-accent h-5 w-5" /> Add Family Member
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <input
            type="text"
            placeholder="Name"
            value={newMember.name}
            onChange={(e) => setNewMember({ ...newMember, name: e.target.value })}
            className="px-4 py-2 rounded-lg bg-[#0d1117] text-white border border-gray-700 focus:outline-none focus:ring-2 focus:ring-accentBlue shadow-inner"
          />
          <input
            type="text"
            placeholder="Role"
            value={newMember.role}
            onChange={(e) => setNewMember({ ...newMember, role: e.target.value })}
            className="px-4 py-2 rounded-lg bg-[#0d1117] text-white border border-gray-700 focus:outline-none focus:ring-2 focus:ring-accentBlue shadow-inner"
          />
          <input
            type="number"
            placeholder="Contribution ₹"
            value={newMember.contribution}
            onChange={(e) =>
              setNewMember({ ...newMember, contribution: e.target.value })
            }
            className="px-4 py-2 rounded-lg bg-[#0d1117] text-white border border-gray-700 focus:outline-none focus:ring-2 focus:ring-accentBlue shadow-inner"
          />
        </div>
        <button
          onClick={addMember}
          className="mt-2 bg-accentBlue hover:bg-accentPurple text-white px-6 py-2 rounded-lg transition-all shadow-lg hover:scale-105"
        >
          Add Member
        </button>
      </div>

      {/* Family Members List */}
      <div className="bg-[#161b22] p-6 rounded-2xl shadow-xl space-y-6">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <Users className="text-accent h-5 w-5" /> Family Members
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {family.map((member) => (
            <div
              key={member.id}
              className="bg-[#0d1117] border border-gray-700 rounded-xl p-4 shadow-md hover:shadow-accentBlue transition-all hover:scale-[1.02]"
            >
              <p className="font-medium text-lg">{member.name}</p>
              <p className="text-sm text-gray-400">{member.role}</p>
              <p className="text-accent mt-2 font-semibold">
                ₹{member.contribution.toLocaleString()}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Budget Overview */}
      <div className="bg-[#161b22] p-6 rounded-2xl shadow-xl space-y-6">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <PieChart className="text-accent h-5 w-5" /> Budget Overview
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
          <div className="text-center">
            <p className="text-white text-lg">
              Total Budget: ₹{budget.toLocaleString()}
            </p>
            <p className="text-green-400 text-lg">
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
      <div className="bg-[#161b22] p-6 rounded-2xl shadow-xl space-y-4">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <Target className="text-accent h-5 w-5" /> Savings Goal Progress
        </h2>
        <div className="w-full bg-gray-800 rounded-full h-5">
          <div
            className="bg-accentBlue h-5 rounded-full text-right pr-2 text-xs font-semibold flex items-center justify-end"
            style={{ width: `${savingsProgress}%` }}
          >
            {savingsProgress}%
          </div>
        </div>
        <p className="text-gray-400 text-sm">Goal: ₹{goal.toLocaleString()}</p>
      </div>

      {/* Summary & Actions */}
      <div className="bg-gradient-to-r from-accentBlue/30 to-accentPurple/20 p-6 md:p-8 rounded-2xl shadow-2xl max-w-6xl mx-auto text-center animate-slide-up">
        <div className="flex items-center justify-center gap-3 text-accent mb-2">
          <Home className="h-5 w-5" />
          <h3 className="text-lg font-semibold">Family Contribution Summary</h3>
        </div>
        <p className="text-white text-xl font-bold">
          ₹{totalContribution.toLocaleString()}
        </p>
        <p className="text-sm text-gray-300 mt-2">
          Total shared contributions across all family accounts.
        </p>
        <div className="flex justify-center gap-4 mt-4 flex-wrap">
          <button className="flex items-center gap-2 bg-accentBlue px-4 py-2 rounded-lg text-sm hover:bg-accentPurple transition shadow hover:scale-105">
            <AlarmClock className="h-4 w-4" /> Bill Reminder
          </button>
          <button className="flex items-center gap-2 bg-accentBlue px-4 py-2 rounded-lg text-sm hover:bg-accentPurple transition shadow hover:scale-105">
            <FileDown className="h-4 w-4" /> Export Data
          </button>
        </div>
      </div>
    </div>
  );
};

export default FamilyFinancePage;
