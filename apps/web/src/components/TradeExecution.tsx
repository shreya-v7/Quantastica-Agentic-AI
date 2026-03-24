import React, { useEffect, useState, useRef, useMemo } from "react";
import axios from "axios";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";
import { Send } from "lucide-react";
import { useUiStore } from "../store/uiStore";

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

const selectClass =
  "rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground shadow-sm transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/40 dark:bg-card";

const StatBox = ({ label, value, valueClass }: { label: string; value: string; valueClass: string }) => (
  <div className="rounded-xl border border-border bg-card p-4 text-card-foreground shadow-sm">
    <div className="fi-caption">{label}</div>
    <div className={`text-lg font-semibold tabular-nums ${valueClass}`}>{value}</div>
  </div>
);

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

function chartPalette(isDark: boolean) {
  if (isDark) {
    return {
      title: "#e8edf4",
      axis: "#94a3b8",
      grid: "#334155",
      tooltipBg: "#1e293b",
      tooltipText: "#f1f5f9",
      series: "#38bdf8",
    };
  }
  return {
    title: "#0f172a",
    axis: "#475569",
    grid: "#e2e8f0",
    tooltipBg: "#ffffff",
    tooltipText: "#0f172a",
    series: "#3d4aad",
  };
}

const TradeExecution: React.FC = () => {
  const theme = useUiStore((s) => s.theme);
  const isDark = theme === "dark";

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
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
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
        const res = await Promise.all(files.map((f) => axios.get(`${baseDir}/${f}`)));
        const [bank, credit, epf, mf, netWorth, stock] = res.map((r) => r.data);
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
    const text = input.trim();
    if (!text) return;
    const time = getTime();
    const userMessage: ChatMessage = { role: "user", message: text, time };
    setChat((prev) => [...prev, userMessage]);
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
          parts: [{ text }],
        },
        context: {
          financial_data: finance || {},
        },
        streaming: false,
      };

      const response = await axios.post(`http://${server}:${port}/run`, payload);
      const reply = response.data?.at(-1)?.content?.parts?.[0]?.text || "No response received.";

      setChat((prev) => [...prev, { role: "assistant", message: reply, time: getTime() }]);
    } catch (err) {
      console.error("Chat error:", err);
      setChat((prev) => [
        ...prev,
        { role: "assistant", message: "⚠️ Error reaching the server.", time: getTime() },
      ]);
    } finally {
      setTyping(false);
    }
  };

  const prices = trade?.timeseries.map((p) => p.price) || [];
  const averagePrice = prices.length ? prices.reduce((a, b) => a + b, 0) / prices.length : 0;
  const min = Math.min(...prices);
  const max = Math.max(...prices);
  const last = prices.at(-1) || 0;
  const volatility = prices.length ? ((max - min) / averagePrice) * 100 : 0;
  const changePct = prices.length ? ((last - prices[0]) / prices[0]) * 100 : 0;

  const chartOptions = useMemo(() => {
    const c = chartPalette(isDark);
    const tfLabel = TIMEFRAMES.find((tf) => tf.value === selectedTimeframe)?.label ?? "";
    if (!trade) {
      return {
        chart: { type: "line" as const, backgroundColor: "transparent", height: 400 },
        title: { text: "" },
      };
    }
    return {
      chart: { type: "line" as const, backgroundColor: "transparent", height: 400 },
      title: {
        text: `${trade.ticker} — ${tfLabel}`,
        style: { color: c.title, fontSize: "16px", fontWeight: "600" },
      },
      xAxis: {
        type: "datetime",
        labels: { style: { color: c.axis } },
        gridLineColor: c.grid,
        lineColor: c.grid,
      },
      yAxis: {
        title: { text: "Price (USD)", style: { color: c.axis } },
        labels: { style: { color: c.axis } },
        gridLineColor: c.grid,
      },
      series: [
        {
          name: `${trade.ticker} price`,
          data: trade.timeseries.map((pt) => [pt.time, pt.price]),
          color: c.series,
          type: "line" as const,
          marker: { enabled: false },
        },
      ],
      legend: { enabled: false },
      credits: { enabled: false },
      tooltip: {
        xDateFormat: "%H:%M",
        backgroundColor: c.tooltipBg,
        borderColor: c.grid,
        style: { color: c.tooltipText },
      },
    };
  }, [trade, selectedTimeframe, isDark]);

  return (
    <div className="min-h-screen w-full space-y-8 overflow-x-hidden bg-background px-4 py-6 text-foreground sm:px-6 md:px-0">
      <div className="flex flex-wrap items-end gap-6">
        <div className="flex flex-col gap-2">
          <label htmlFor="trade-ticker" className="text-sm font-medium text-foreground">
            Ticker
          </label>
          <select
            id="trade-ticker"
            className={selectClass}
            value={selectedTicker}
            onChange={(e) => setSelectedTicker(e.target.value)}
          >
            {TICKERS.map((ticker) => (
              <option key={ticker} value={ticker}>
                {ticker}
              </option>
            ))}
          </select>
        </div>
        <div className="flex flex-col gap-2">
          <label htmlFor="trade-timeframe" className="text-sm font-medium text-foreground">
            Timeframe
          </label>
          <select
            id="trade-timeframe"
            className={selectClass}
            value={selectedTimeframe}
            onChange={(e) => setSelectedTimeframe(e.target.value)}
          >
            {TIMEFRAMES.map((tf) => (
              <option key={tf.value} value={tf.value}>
                {tf.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
        <div className="rounded-xl border border-border bg-card/50 p-4 shadow-sm dark:bg-card/30">
          {loading ? (
            <p className="text-sm text-muted-foreground">Loading chart…</p>
          ) : trade ? (
            <HighchartsReact highcharts={Highcharts} options={chartOptions} />
          ) : (
            <p className="text-sm text-muted-foreground">No data available</p>
          )}
        </div>

        <div className="relative flex h-[450px] flex-col rounded-xl border border-border bg-card p-4 shadow-sm">
          <div className="mb-3 text-sm font-semibold text-foreground">Trade assistant</div>

          <div className="flex-1 space-y-3 overflow-y-auto pr-2" style={{ maxHeight: "calc(100% - 56px)" }}>
            {chat.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[70%] rounded-lg p-3 text-sm ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "border border-border bg-muted text-foreground"
                  }`}
                >
                  <div
                    className={`mb-1 text-xs ${
                      msg.role === "user" ? "text-primary-foreground/80" : "text-muted-foreground"
                    }`}
                  >
                    {msg.role === "user" ? "You" : "Assistant"} · {msg.time}
                  </div>
                  {msg.message}
                </div>
              </div>
            ))}
            {typing && (
              <div className="animate-pulse text-sm text-muted-foreground">Assistant is typing…</div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="mt-3 flex items-center gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendChat()}
              className="fi-input flex-1 py-2.5"
              placeholder="Ask about trade insights, price action…"
              aria-label="Message"
            />
            <button
              type="button"
              onClick={sendChat}
              className="inline-flex items-center justify-center rounded-lg bg-primary px-4 py-2.5 text-primary-foreground transition hover:opacity-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/40"
              aria-label="Send"
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 text-center md:grid-cols-4">
        <StatBox label="Latest price" value={`$${last.toFixed(2)}`} valueClass="text-primary" />
        <StatBox
          label="Average price"
          value={`$${averagePrice.toFixed(2)}`}
          valueClass="text-sky-600 dark:text-sky-400"
        />
        <StatBox
          label="Volatility"
          value={`${volatility.toFixed(2)}%`}
          valueClass="text-violet-600 dark:text-violet-400"
        />
        <StatBox
          label="Change"
          value={`${changePct >= 0 ? "+" : ""}${changePct.toFixed(2)}%`}
          valueClass={
            changePct >= 0 ? "text-emerald-600 dark:text-emerald-400" : "text-red-600 dark:text-red-400"
          }
        />
      </div>
    </div>
  );
};

export default TradeExecution;
