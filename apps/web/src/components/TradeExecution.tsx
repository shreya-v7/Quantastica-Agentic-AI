import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";
import { Send } from "lucide-react";

// === Constants ===
const TICKERS = ["AAPL", "GOOGL", "MSFT"];
const TIMEFRAMES = [
  { label: "1 Minute", value: "1m" },
  { label: "5 Minutes", value: "5m" },
  { label: "15 Minutes", value: "15m" },
  { label: "1 Day", value: "1d" },
];
const AGENT_CONFIG = {
  name: "Trade Execution Agent",
  appName: "trade_execution_agent",
  port: 9003,
  server: "34.45.50.210",
  userId: "3333333333",
};

const getRandomSessionId = () => "s_" + Math.random().toString(36).substring(2, 10);
const getTime = () => new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

// === Type Definitions ===
type TradeData = {
  ticker: string;
  timeseries: { time: number; price: number }[];
};

type ChatMessage = {
  role: "user" | "assistant";
  message: string;
  time: string;
};

type FinancialData = {
  bank?: { bankTransactions?: any[] };
  credit?: { score?: number };
  epf?: { total_balance?: number };
  mf?: { total_value?: number };
  netWorth?: { total?: number };
  stock?: { transactions?: any[] };
};

// === StatBox Component ===
const StatBox = ({ label, value, color }: { label: string; value: string; color: string }) => (
  <div className="p-4 border border-zinc-700 rounded-xl">
    <div className="text-xs text-zinc-400">{label}</div>
    <div className={`text-lg font-bold ${color}`}>{value}</div>
  </div>
);

// === Fetch Trade Data ===
const fetchTradeData = async (ticker: string, timeframe: string): Promise<TradeData> => {
  const proxyUrl = "https://api.allorigins.win/get?url=";
  const targetUrl = encodeURIComponent(
    `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=${timeframe}&range=1d`
  );
  const response = await axios.get(`${proxyUrl}${targetUrl}`);
  const data = JSON.parse(response.data.contents);
  const result = data.chart.result[0];
  const times = result.timestamp;
  const prices = result.indicators.quote[0].close;
  const timeseries = times
    .map((t: number, i: number) => ({ time: t * 1000, price: prices[i] }))
    .filter((point: any) => point.price !== null);
  return { ticker, timeseries };
};

// === Main Component ===
const TradeExecution: React.FC = () => {
  const [selectedTicker, setSelectedTicker] = useState(TICKERS[0]);
  const [selectedTimeframe, setSelectedTimeframe] = useState(TIMEFRAMES[0].value);
  const [trade, setTrade] = useState<TradeData | null>(null);
  const [loading, setLoading] = useState(true);
  const [chat, setChat] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [typing, setTyping] = useState(false);
  const [finance, setFinance] = useState<FinancialData | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  };


  useEffect(() => {
    scrollToBottom();
  }, [chat, typing]);

  useEffect(() => {
    loadTrade(selectedTicker, selectedTimeframe);
    const interval = setInterval(() => loadTrade(selectedTicker, selectedTimeframe), 30000);
    return () => clearInterval(interval);
  }, [selectedTicker, selectedTimeframe]);

  useEffect(() => {
    const loadFinance = async () => {
      try {
        const baseDir = "/test_data_dir/3333333333";
        const files = [
          "fetch_bank_transactions.json",
          "fetch_credit_report.json",
          "fetch_epf_details.json",
          "fetch_mf_transactions.json",
          "fetch_net_worth.json",
          "fetch_stock_transactions.json",
        ];
        const res = await Promise.all(files.map(f => axios.get(`${baseDir}/${f}`)));
        const [bank, credit, epf, mf, netWorth, stock] = res.map(r => r.data);
        setFinance({ bank, credit, epf, mf, netWorth, stock });
      } catch (err) {
        console.error("Finance data error", err);
      }
    };
    loadFinance();
  }, []);

  const loadTrade = async (ticker: string, timeframe: string) => {
    setLoading(true);
    try {
      const result = await fetchTradeData(ticker, timeframe);
      setTrade(result);
    } catch (err) {
      console.error(err);
      setTrade(null);
    }
    setLoading(false);
  };

  const sendChat = async () => {
    if (!input.trim()) return;
    const time = getTime();
    const userMessage: ChatMessage = { role: "user", message: input, time };
    setChat(prev => [...prev, userMessage]);
    setInput("");
    setTyping(true);

    const { appName, port, server, userId } = AGENT_CONFIG;
    let session = sessionId;

    try {
      if (!session) {
        session = getRandomSessionId();
        await axios.post(`http://${server}:${port}/apps/${appName}/users/${userId}/sessions/${session}`);
        setSessionId(session);
      }

      const payload = {
        user_id: userId,
        app_name: appName,
        session_id: session,
        new_message: {
          role: "user",
          parts: [{ text: input }],
        },
        context: {
          financial_data: finance || {}, // attach full raw finance data separately here
        },
        streaming: false,
      };

      const response = await axios.post(`http://${server}:${port}/run`, payload);
      let reply = response.data?.at(-1)?.content?.parts?.[0]?.text || "No response received.";

      setChat(prev => [...prev, { role: "assistant", message: reply, time: getTime() }]);
    } catch (err) {
      console.error("Chat error:", err);
      setChat(prev => [...prev, { role: "assistant", message: "⚠️ Error reaching the server.", time: getTime() }]);
    } finally {
      setTyping(false);
    }
  };



  const prices = trade?.timeseries.map(p => p.price) || [];
  const averagePrice = prices.length ? prices.reduce((a, b) => a + b, 0) / prices.length : 0;
  const min = Math.min(...prices);
  const max = Math.max(...prices);
  const last = prices.at(-1) || 0;
  const volatility = prices.length ? ((max - min) / averagePrice) * 100 : 0;
  const changePct = prices.length ? ((last - prices[0]) / prices[0]) * 100 : 0;

  return (
    <div className="min-h-screen w-full text-white px-6 py-8 space-y-8 overflow-x-hidden">
      {/* Ticker and Timeframe Selection */}
      <div className="flex flex-wrap items-center gap-4">
        <div>
          <label className="text-sm font-semibold mr-2">Ticker</label>
          <select
            className="bg-zinc-900 border border-zinc-700 rounded px-3 py-1"
            value={selectedTicker}
            onChange={e => setSelectedTicker(e.target.value)}
          >
            {TICKERS.map(ticker => <option key={ticker} value={ticker}>{ticker}</option>)}
          </select>
        </div>
        <div>
          <label className="text-sm font-semibold mr-2">Timeframe</label>
          <select
            className="bg-zinc-900 border border-zinc-700 rounded px-3 py-1"
            value={selectedTimeframe}
            onChange={e => setSelectedTimeframe(e.target.value)}
          >
            {TIMEFRAMES.map(tf => <option key={tf.value} value={tf.value}>{tf.label}</option>)}
          </select>
        </div>
      </div>

      {/* Chart and Chat Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          {loading ? <p>Loading chart...</p> : trade ? (
            <HighchartsReact highcharts={Highcharts} options={{
              chart: { type: "line", backgroundColor: "transparent", height: 400 },
              title: {
                text: `${trade?.ticker ?? ""} - ${TIMEFRAMES.find(tf => tf.value === selectedTimeframe)?.label ?? ""}`,
                style: { color: "#fff" }
              },
              xAxis: { type: "datetime", labels: { style: { color: "#ccc" } }, gridLineColor: "#333" },
              yAxis: {
                title: { text: "Price (USD)", style: { color: "#fff" } },
                labels: { style: { color: "#ccc" } },
                gridLineColor: "#333"
              },
              series: [{
                name: `${trade?.ticker ?? ""} Price`,
                data: trade.timeseries.map(pt => [pt.time, pt.price]),
                color: "#4fd1c5",
                type: "line",
                marker: { enabled: false }
              }],
              legend: { enabled: false },
              credits: { enabled: false },
              tooltip: { xDateFormat: "%H:%M", backgroundColor: "#222", style: { color: "#fff" } },
            }} />
          ) : <p>No data available</p>}
        </div>

        {/* Chat */}
        <div className="flex flex-col border border-zinc-700 rounded-xl p-4 h-[450px] relative">
          {/* Bot Header */}
          <div className="flex items-center gap-2 mb-3 text-white text-sm font-semibold">
            🤖 Let’s Trade with Bot
          </div>

          {/* Scrollable Chat Messages */}
          <div
            className="flex-1 overflow-y-auto space-y-3 pr-2"
            style={{ maxHeight: "calc(100% - 56px)" }}
          >
            {chat.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`p-3 rounded-lg max-w-[70%] ${msg.role === "user"
                      ? "bg-accent text-black"
                      : "bg-zinc-800 text-white"
                    }`}
                >
                  <div className="text-xs opacity-60 mb-1">
                    {msg.role === "user" ? "You" : "Assistant"} • {msg.time}
                  </div>
                  {msg.message}
                </div>
              </div>
            ))}
            {typing && (
              <div className="text-sm text-gray-400 animate-pulse">Assistant is typing...</div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="flex items-center gap-2 mt-3">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendChat()}
              className="flex-1 bg-zinc-800 border border-zinc-700 text-white rounded px-4 py-2"
              placeholder="Ask about trade insights, price action..."
            />
            <button
              onClick={sendChat}
              className="bg-accent text-black px-4 py-2 rounded-lg hover:bg-opacity-80 transition"
            >
              <Send size={16} />
            </button>
          </div>
        </div>



      </div>

      {/* Trade Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
        <StatBox label="Latest Price" value={`$${last.toFixed(2)}`} color="text-accent" />
        <StatBox label="Average Price" value={`$${averagePrice.toFixed(2)}`} color="text-yellow-300" />
        <StatBox label="Volatility" value={`${volatility.toFixed(2)}%`} color="text-purple-400" />
        <StatBox label="Change (%)" value={`${changePct >= 0 ? "+" : ""}${changePct.toFixed(2)}%`} color={changePct >= 0 ? "text-green-400" : "text-red-400"} />
      </div>
    </div>
  );
};

export default TradeExecution;
