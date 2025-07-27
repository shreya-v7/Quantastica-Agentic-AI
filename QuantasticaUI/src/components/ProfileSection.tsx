import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  CreditCard,
  TrendingUp,
  TrendingDown,
  BarChart2,
  Landmark,
  RefreshCcw,
  ShieldCheck,
  ReceiptText,
  Calendar
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";

const formatNumber = (num: number) =>
  num?.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");

const ProfileSection = () => {
  const [profile, setProfile] = useState<any>(null);
  const [monthlyHistory, setMonthlyHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await axios.get(
          "http://localhost:5001/user/1010101010/profile"
        );
        if (res.data?.success) {
          setProfile(res.data.profile);
          setMonthlyHistory(res.data.monthly_history);
        }
      } catch (error) {
        console.error("Error fetching profile:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  if (loading) return <p className="text-white text-sm px-6">Loading profile...</p>;

  if (!profile)
    return (
      <p className="text-red-400 text-sm px-6">
        Unable to load profile data. Please try again later.
      </p>
    );

  return (
    <section className="mt-12 px-6 lg:px-12 max-w-7xl mx-auto">
      <h2 className="text-2xl font-bold mb-6 flex items-center gap-2 text-white">
        <ShieldCheck className="w-6 h-6 text-green-400" />
        Financial Profile Summary
      </h2>

      {/* Profile Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 text-sm sm:text-base mb-12">
        <ProfileCard
          icon={<CreditCard className="text-purple-400" />}
          label="Primary Bank"
          value={profile.primary_bank}
        />
        <ProfileCard
          icon={<BarChart2 className="text-blue-400" />}
          label="Net Flow"
          value={`₹${formatNumber(profile.net_flow)}`}
        />
        <ProfileCard
          icon={<CreditCard className="text-red-400" />}
          label="Total Debit"
          value={`₹${formatNumber(profile.total_debit)}`}
        />
        <ProfileCard
          icon={<CreditCard className="text-green-400" />}
          label="Total Credit"
          value={`₹${formatNumber(profile.total_credit)}`}
        />
        <ProfileCard
          icon={<TrendingUp className="text-green-500" />}
          label="Max Balance"
          value={`₹${formatNumber(profile.max_balance)}`}
        />
        <ProfileCard
          icon={<TrendingDown className="text-red-500" />}
          label="Min Balance"
          value={`₹${formatNumber(profile.min_balance)}`}
        />
        <ProfileCard
          icon={<Landmark className="text-yellow-400" />}
          label="Avg Balance"
          value={`₹${formatNumber(profile.avg_balance)}`}
        />
        <ProfileCard
          icon={<RefreshCcw className="text-purple-400" />}
          label="Credit/Debit Ratio"
          value={profile.credit_debit_ratio.toFixed(2)}
        />
        <ProfileCard
          icon={<ReceiptText className="text-cyan-300" />}
          label="Transactions"
          value={profile.total_transactions}
        />
      </div>

      {/* Monthly History Line Chart */}
      <div className="bg-white/5 rounded-2xl border border-white/10 shadow-md p-6 mb-12">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Calendar className="w-5 h-5 text-yellow-400" />
          Monthly Savings & Expenditure
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={monthlyHistory}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2c2c2c" />
            <XAxis dataKey="month" stroke="#ccc" />
            <YAxis stroke="#ccc" />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="expenditure" stroke="#ef4444" strokeWidth={2} />
            <Line type="monotone" dataKey="savings" stroke="#22c55e" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
};

const ProfileCard = ({
  icon,
  label,
  value
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
}) => (
  <div className="bg-white/5 backdrop-blur-sm p-5 rounded-2xl shadow-md hover:scale-[1.02] transition-all border border-white/10">
    <div className="flex items-center gap-3 mb-2 text-gray-300">
      {icon}
      <span className="uppercase font-semibold tracking-wide">{label}</span>
    </div>
    <p className="text-xl font-bold text-white">{value}</p>
  </div>
);

export default ProfileSection;
