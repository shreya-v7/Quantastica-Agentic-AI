import React, { useRef, useState } from "react";
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

const ChatInterface: React.FC = () => {
  const [selectedAgent, setSelectedAgent] = useState(agents[0]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [userId] = useState("1010101010");


  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // useEffect(() => {
  //   scrollToBottom();
  // }, [messages, typing]);

  const getTime = () => new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  const handleSend = async () => {
  if (!input.trim()) return;

  const userMsg: Message = {
    sender: "user",
    content: input,
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
            text: input,
          },
        ],
      },
      streaming: false,
    };
    console.log("🚀 Payload being sent to /run:", runPayload);

    // Send the message
    const response = await axios.post(`http://${server}:${port}/run`, runPayload);

    console.log("Response from agent:", response.data);

    const dataArray = response.data;
    const msg = dataArray?.[dataArray.length - 1]?.content?.parts?.[0]?.text || "No valid response text";
      console.log("Result text:", msg);
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
    <div className="min-h-screen w-full bg-gradient-to-br from-[#0b1120] via-[#0f172a] to-[#1e293b] text-white font-sans relative overflow-hidden">
      <div className="absolute inset-0 opacity-10 bg-[url('/background-grid.svg')] bg-cover" />

      <div className="max-w-3xl mx-auto px-4 py-6 relative z-10 flex flex-col min-h-screen">
        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold">🧠 FinGPT</h1>
          <div className="flex gap-2 items-center">
            <select
              className="bg-[#1e293b] text-white border border-gray-700 rounded-md px-3 py-2 text-sm"
              value={selectedAgent.name}
              onChange={(e) =>
                setSelectedAgent(
                  agents.find((a) => a.name === e.target.value) || agents[0]
                )
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

        {/* Chat Container */}
        <div className="flex-1 overflow-y-auto bg-[#1e293b]/70 border border-white/10 rounded-xl p-6 backdrop-blur-lg shadow-xl space-y-4">
          {messages.length === 0 && (
            <div className="text-gray-400 text-center text-sm mt-20">
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
                    ? "bg-accentBlue text-white"
                    : "bg-[#0f172a] border border-gray-700 text-gray-200"
                }`}
              >
                <div className="text-xs opacity-60 mb-1">
                  {msg.sender === "user" ? "You" : selectedAgent.name} • {msg.timestamp}
                </div>
                {msg.content}
              </div>
            </div>
          ))}

          {typing && (
            <div className="text-sm text-gray-400 animate-pulse">Assistant is typing...</div>
          )}

          <div ref={messagesEndRef} />
        </div>


        {/* Input */}
        <div className="mt-4 flex items-center gap-2">
          <input
            className="flex-1 px-4 py-3 bg-[#0f172a] border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-accentBlue"
            placeholder="Ask something..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button
            onClick={handleSend}
            className="px-5 py-3 bg-accentBlue hover:bg-accentBlue/90 rounded-lg text-white font-medium"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
