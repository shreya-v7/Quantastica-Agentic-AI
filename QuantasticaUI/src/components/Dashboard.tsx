import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  Calendar,
  Bell,
  User,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react";
import { Link } from "react-router-dom";

function Dashboard() {
  const [newsData, setNewsData] = useState([]);

  const fetchNews = async (query: string) => {
    try {
      const response = await axios.post(
        "http://localhost:5000/getHeadlines",
        { topic: query },
        { headers: { "Content-Type": "application/json" } }
      );
      setNewsData(response.data || []);
    } catch (error) {
      console.error("Error fetching news:", error);
    }
  };

  useEffect(() => {
    fetchNews("stock market");
  }, []);

  const getColor = (index: number) => {
    const colors = ["bg-purple-400", "bg-blue-400", "bg-green-400", "bg-yellow-400", "bg-pink-400"];
    return colors[index % colors.length];
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col md:flex-row">
      <main className="flex-1 px-4 sm:px-6 md:px-10 py-6 md:py-8 space-y-10 max-w-full overflow-x-hidden">
        {/* Top Bar */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 animate-fade-in gap-4 md:gap-0">
          <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
          <div className="flex items-center gap-4">
            <IconButton>
              <Calendar className="h-5 w-5 text-accent" />
            </IconButton>
            <IconButton>
              <Bell className="h-5 w-5 text-accent" />
            </IconButton>
            <div className="rounded-full bg-card w-10 h-10 flex items-center justify-center shadow-lg ring-2 ring-accent/30 transition-all duration-300 hover:scale-105">
              <User className="h-6 w-6 text-accent" />
            </div>
          </div>
        </div>

        {/* Greeting Card */}
        <div className="bg-gradient-to-tr from-[#1e2761] via-[#232b5d] to-[#1a1f3c] rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.3)] p-6 md:p-8 flex flex-col md:flex-row md:items-center md:justify-between gap-6 animate-gradient-x glass border border-white/10 transition-all duration-500 hover:shadow-2xl hover:ring-1 hover:ring-accent">
          <div>
            <h3 className="text-2xl font-semibold mb-1 text-white">Hello, "Alex! 👋</h3>
            <p className="text-white/80 max-w-md">Your AI Financial Assistant is ready to help</p>
            <div className="flex gap-3 mt-4 flex-wrap">
              <Link to="/chat" className="bg-accentBlue text-white px-4 py-2 rounded-lg hover:bg-accentBlue/90 transition">
                <AnimatedButton>Start Chatting</AnimatedButton>
              </Link>

            </div>
          </div>
          <div className="bg-background/60 rounded-xl p-6 flex flex-col items-center justify-center min-w-[260px] shadow-inner glass">
            <div className="flex items-center gap-3 mb-2">
              <User className="h-6 w-6 text-accent" />
              <span className="font-semibold text-accent">FinanceAI Assistant</span>
            </div>
            <p className="text-sm opacity-70 text-center max-w-xs">
              "Ask me about your finances, investments, or latest market news!"
            </p>
          </div>
        </div>

        {/* Financial Overview Cards */}
        <div className="mb-8 animate-fade-in">
          <h4 className="text-xl font-semibold mb-4">Financial Overview</h4>
          <div className="grid gap-6 md:grid-cols-3 sm:grid-cols-2 grid-cols-1">
            <OverviewCard label="Income" value="₹85,400" change="+12%" positive />
            <OverviewCard label="Expenses" value="₹42,150" change="-8%" positive={false} />
            <OverviewCard label="Savings" value="₹43,250" change="+16%" positive />
          </div>
        </div>

        {/* Latest News (Dynamic Integration) */}
        <div className="animate-fade-in">
          <div className="flex justify-between items-center mb-4">
            <h4 className="text-xl font-semibold">Latest Financial News</h4>
            <button
              className="text-accent text-sm font-medium hover:underline transition"
              onClick={() => fetchNews("finance")}
            >
              Refresh
            </button>
          </div>
          <div className="space-y-3">
            {newsData.length > 0 ? (
              newsData.map((item: any, index: number) => (
                <NewsItem
                  key={index}
                  source={item.source || "Unknown"}
                  headline={item.headline || item.title || "No headline"}
                  time={item.publishedAt || "Just now"}
                  color={getColor(index)}
                />
              ))
            ) : (
              <p className="text-muted-foreground text-sm">No news available.</p>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

// IconButton
function IconButton({ children }: { children: React.ReactNode }) {
  return (
    <button className="rounded-full bg-card p-3 shadow-lg hover:bg-background transition-all duration-200 hover:scale-110 ring-2 ring-accent/10">
      {children}
    </button>
  );
}

// AnimatedButton
function AnimatedButton({ children, outline = false }: { children: React.ReactNode; outline?: boolean }) {
  return outline ? (
    <button className="bg-background text-foreground border border-accent px-4 py-2 rounded-lg font-medium transition-all duration-200 hover:bg-accent hover:text-accent-foreground hover:scale-105 shadow-md">
      {children}
    </button>
  ) : (
    <button className="bg-accent text-accent-foreground px-4 py-2 rounded-lg font-medium transition-all duration-200 hover:scale-105 hover:shadow-lg hover:bg-accent/80">
      {children}
    </button>
  );
}

// OverviewCard
function OverviewCard({
  label,
  value,
  change,
  positive,
}: {
  label: string;
  value: string;
  change: string;
  positive: boolean;
}) {
  return (
    <div className="bg-card/80 backdrop-blur-md rounded-2xl shadow-xl p-6 flex flex-col gap-2 transition-transform duration-300 hover:-translate-y-1 hover:shadow-2xl hover:ring-2 hover:ring-accent/30 glass">
      <div className="text-sm opacity-80">{label}</div>
      <div className="text-2xl font-semibold">{value}</div>
      <div
        className={`flex items-center gap-1 text-sm mt-1 ${
          positive ? "text-green-400" : "text-red-400"
        }`}
      >
        {positive ? (
          <ArrowUpRight className="h-4 w-4" />
        ) : (
          <ArrowDownRight className="h-4 w-4" />
        )}
        {change} from last month
      </div>
    </div>
  );
}

// NewsItem
function NewsItem({
  source,
  headline,
  time,
  color,
}: {
  source: string;
  headline: string;
  time: string;
  color: string;
}) {
  return (
    <div className="bg-card/80 backdrop-blur-md rounded-xl p-4 flex items-center gap-4 shadow transition-transform duration-300 hover:scale-105 glass max-w-full border border-white/10 hover:ring-1 hover:ring-accent/30">
      <span className={`px-3 py-1 rounded-full text-xs font-semibold text-background ${color}`}>
        {source}
      </span>
      <div className="flex flex-col">
        <div className="font-medium">{headline}</div>
        <div className="text-xs opacity-60">{time}</div>
      </div>
    </div>
  );
}

export default Dashboard;
