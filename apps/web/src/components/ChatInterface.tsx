import React, { useEffect, useRef, useState } from "react";
import {
  Send,
  LineChart,
  Newspaper,
  Wallet,
} from "lucide-react";
import axios from "axios";


const agents = [
  { name: "Chart Analyzer Agent", icon: <LineChart size={16} /> },
  { name: "News Analyzer Agent", icon: <Newspaper size={16} /> },
  { name: "Wealth Manager Agent", icon: <Wallet size={16} /> },
  { name: "Loan Insurance Agent", icon: <Wallet size={16} /> },
  { name: "Tax Analyzer Agent", icon: <Wallet size={16} /> },
  { name: "Investment Analysis Agent", icon: <Wallet size={16} /> },
];

const getRandomSessionId = () => {
  return "s_" + Math.random().toString(36).substring(2, 10);
};


const mapAgentConfig = (agentName: string): { appName: string; port: number, server: string } => {
  const defaultServer = "localhost";

  switch (agentName) {
    // case "Chart Analyzer Agent":
    //   return { appName: "chart_analyzer_agent", port: 8002 , server: defaultServer };
    case "Wealth Manager Agent":
      return { appName: "wealth_manager_agent", port: 8006, server: defaultServer };
    // case "Tax Analyzer Agent":
    //   return { appName: "tax_analyzer_agent", port: 8000, server: defaultServer };
    case "Loan Insurance Agent":
      return { appName: "loan_insurance_agent", port: 8000, server: '34.45.50.210' };
    case "Investment Analysis Agent":
      return { appName: "investment_agent", port: 8001, server: '34.45.50.210' };
    case "News Analyzer Agent":
      return { appName: "financial_news_analyzer", port: 8000, server: defaultServer };
    default:
      return { appName: "financial_news_analyzer", port: 8000, server: defaultServer};
  }
};


interface Message {
  sender: "user" | "assistant";
  content: string;
  timestamp: string;
}

export type ChatInterfaceProps = {
  /** Embedded in bottom-right dock: tighter layout, title hidden (shell provides header). */
  docked?: boolean;
  /** Set initial agent (e.g. from dock topic). Remount parent with key to reset session. */
  defaultAgentName?: string;
};

const ChatInterface: React.FC<ChatInterfaceProps> = ({ docked = false, defaultAgentName }) => {
  const [selectedAgent, setSelectedAgent] = useState(() => {
    if (defaultAgentName) {
      const match = agents.find((a) => a.name === defaultAgentName);
      if (match) return match;
    }
    return agents[0];
  });
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [userId] = useState("1010101010");


  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, typing]);

  const getTime = () => new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  const handleSend = async () => {
    const text = input.trim();
    if (!text) return;

    const userMsg: Message = {
      sender: "user",
      content: text,
      timestamp: getTime(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setTyping(true);

    const { appName, port, server } = mapAgentConfig(selectedAgent.name);

    let session = sessionId;

    try {
      // If no session yet, create one
      if (!sessionId) {
        session = getRandomSessionId();
        await axios.post(
          `http://${server}:${port}/apps/${appName}/users/${userId}/sessions/${session}`
        );
        setSessionId(session);
      }

      const runPayload = {
        user_id: userId,
        app_name: appName,
        session_id: session,
        new_message: {
          role: "user",
          parts: [
            {
              text,
            },
          ],
        },
        streaming: false,
      };

      const response = await axios.post(`http://${server}:${port}/run`, runPayload);

      const dataArray = response.data;
      const msg = dataArray?.[dataArray.length - 1]?.content?.parts?.[0]?.text || "No valid response text";
      const assistantMsg: Message = {
        sender: "assistant",
        content: msg,
        timestamp: getTime(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [
        ...prev,
        {
          sender: "assistant",
          content: "⚠️ Something went wrong. Please try again later.",
          timestamp: getTime(),
        },
      ]);
    } finally {
      setTyping(false);
    }
  };



  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") handleSend();
  };

  return (
    <div
      className={`relative flex h-full min-h-0 w-full flex-col overflow-hidden font-sans text-foreground ${
        docked
          ? "bg-transparent"
          : "rounded-xl border border-border bg-background dark:border-white/10 dark:bg-gradient-to-br dark:from-[#0b1120] dark:via-[#0f172a] dark:to-[#1e293b]"
      }`}
    >
      {!docked && (
        <div className="pointer-events-none absolute inset-0 hidden bg-[url('/background-grid.svg')] bg-cover opacity-10 dark:block" />
      )}

      <div
        className={`relative z-10 mx-auto flex min-h-0 w-full max-w-3xl flex-1 flex-col px-4 py-4 md:py-6 ${docked ? "px-3 py-3 md:px-3 md:py-3" : ""}`}
      >
        {/* Header — hidden in dock (ChatDock provides title + actions) */}
        {!docked ? (
          <div className="mb-4 flex items-center justify-between gap-3">
            <h1 className="text-2xl font-bold text-foreground">🧠 FinGPT</h1>
            <div className="flex min-w-0 flex-1 justify-end">
              <select
                className="max-w-[min(100%,220px)] rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/40 dark:bg-card"
                value={selectedAgent.name}
                onChange={(e) =>
                  setSelectedAgent(agents.find((a) => a.name === e.target.value) || agents[0])
                }
              >
                {agents.map((a) => (
                  <option key={a.name} value={a.name}>
                    {a.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        ) : (
          <div className="mb-2 shrink-0">
            <label htmlFor="chat-agent-dock" className="sr-only">
              Assistant agent
            </label>
            <select
              id="chat-agent-dock"
              className="w-full rounded-lg border border-input bg-background px-2.5 py-2 text-xs text-foreground shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/40 dark:bg-card"
              value={selectedAgent.name}
              onChange={(e) =>
                setSelectedAgent(agents.find((a) => a.name === e.target.value) || agents[0])
              }
            >
              {agents.map((a) => (
                <option key={a.name} value={a.name}>
                  {a.name}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Chat Container */}
        <div className="min-h-0 flex-1 space-y-4 overflow-y-auto rounded-xl border border-border bg-card p-4 shadow-sm dark:border-white/10 dark:bg-card/80 dark:shadow-xl dark:backdrop-blur-lg md:p-6">
          {messages.length === 0 && (
            <div className="text-muted-foreground text-center text-sm mt-20">
              <p className="mb-1">💡 Try asking something like:</p>
              <p>“What’s my spending this month?” or “Show me investment performance”</p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${
                msg.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-sm rounded-lg px-4 py-3 text-sm shadow-md ${
                  msg.sender === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted border border-border text-card-foreground"
                }`}
              >
                <div
                  className={`mb-1 text-xs ${
                    msg.sender === "user" ? "text-primary-foreground/75" : "text-muted-foreground"
                  }`}
                >
                  {msg.sender === "user" ? "You" : selectedAgent.name} · {msg.timestamp}
                </div>
                {msg.content}
              </div>
            </div>
          ))}

          {typing && (
            <div className="text-sm text-muted-foreground animate-pulse">Assistant is typing...</div>
          )}

          <div ref={messagesEndRef} />
        </div>


        {/* Input */}
        <div className="mt-4 flex items-center gap-2">
          <input
            className="fi-input flex-1 border-input bg-background py-3 dark:bg-muted"
            placeholder="Ask something..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button
            onClick={handleSend}
            className="rounded-lg bg-primary px-5 py-3 font-medium text-primary-foreground transition hover:opacity-95"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
