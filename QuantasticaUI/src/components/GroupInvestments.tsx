import { useState } from "react";
import {
  Users,
  MessageCircle,
  DollarSign,
  CheckCircle,
  Megaphone,
  ArrowLeft,
  ArrowRight,
} from "lucide-react";

interface Friend {
  id: number;
  name: string;
  email: string;
  online: boolean;
}

interface Investment {
  id: number;
  friendId: number;
  amount: number;
  date: string;
  status: "Pending" | "Confirmed";
}

const friendsData: Friend[] = [
  { id: 1, name: "Alice Johnson", email: "alice@example.com", online: true },
  { id: 2, name: "Bob Smith", email: "bob@example.com", online: false },
  { id: 3, name: "Charlie Davis", email: "charlie@example.com", online: true },
];

export default function GroupInvestments() {
  // Step state: 1 = Announce IPO, 2 = Select collaborators, 3 = Dashboard
  const [step, setStep] = useState(1);

  // IPO announcement form state
  const [ipoTitle, setIpoTitle] = useState("");
  const [ipoDescription, setIpoDescription] = useState("");
  const [targetAmount, setTargetAmount] = useState("");
  const [deadline, setDeadline] = useState("");

  // Collaborators selected
  const [selectedFriends, setSelectedFriends] = useState<Friend[]>([]);

  // Investments for demo, you can integrate backend later
  const [investmentsData, setInvestmentsData] = useState<Investment[]>([
    { id: 1, friendId: 1, amount: 50000, date: "2025-07-20", status: "Confirmed" },
    { id: 2, friendId: 2, amount: 30000, date: "2025-07-21", status: "Pending" },
    { id: 3, friendId: 3, amount: 45000, date: "2025-07-22", status: "Confirmed" },
  ]);

  // Chat messages
  const [chatMessages, setChatMessages] = useState<
    { id: number; sender: string; text: string }[]
  >([]);
  const [chatInput, setChatInput] = useState("");

  // Utility: total confirmed investments sum
  const totalInvested = investmentsData
    .filter((inv) => inv.status === "Confirmed")
    .reduce((sum, inv) => sum + inv.amount, 0);

  // Toggle friend selection in collaborators page
  const toggleFriendSelection = (friend: Friend) => {
    setSelectedFriends((prev) =>
      prev.some((f) => f.id === friend.id)
        ? prev.filter((f) => f.id !== friend.id)
        : [...prev, friend]
    );
  };

  // Handle send chat message
  const handleSendMessage = () => {
    if (chatInput.trim() === "") return;
    setChatMessages((prev) => [
      ...prev,
      { id: prev.length + 1, sender: "You", text: chatInput.trim() },
    ]);
    setChatInput("");
  };

  // Navigation helpers
  const canGoNextStep = () => {
    if (step === 1) {
      return ipoTitle.trim() !== "" && targetAmount.trim() !== "" && deadline.trim() !== "";
    }
    if (step === 2) {
      return selectedFriends.length > 0;
    }
    return true;
  };

  // Reset form on start
  const resetForm = () => {
    setIpoTitle("");
    setIpoDescription("");
    setTargetAmount("");
    setDeadline("");
    setSelectedFriends([]);
    setInvestmentsData([]);
    setChatMessages([]);
  };

  return (
    <div className="min-h-screen bg-background text-foreground p-6 sm:p-10 space-y-10 max-w-7xl mx-auto">
      <h1 className="text-4xl font-bold mb-8 flex items-center gap-3">
        <Megaphone className="h-8 w-8 text-accent" /> Group Investments
      </h1>

      {/* Stepper / Navigation */}
      <div className="flex items-center justify-center gap-6 mb-10">
        {[1, 2, 3].map((s) => (
          <button
            key={s}
            onClick={() => setStep(s)}
            disabled={s > step && !canGoNextStep()}
            className={`rounded-full w-10 h-10 flex items-center justify-center font-semibold transition
              ${
                s === step
                  ? "bg-accent text-accent-foreground shadow-lg"
                  : "bg-card text-gray-400 hover:bg-accent/50 hover:text-accent-foreground"
              }
              ${s > step && !canGoNextStep() ? "cursor-not-allowed opacity-40" : "cursor-pointer"}
            `}
          >
            {s}
          </button>
        ))}
      </div>

      {/* Steps Content */}
      {step === 1 && (
        <section className="bg-card rounded-2xl p-8 shadow-lg glass max-w-4xl mx-auto animate-slide-up space-y-6">
          <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
            <Megaphone className="h-6 w-6 text-accent" />
            Announce New IPO / Mutual Fund
          </h2>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (canGoNextStep()) setStep(2);
            }}
            className="space-y-4"
          >
            <div>
              <label className="block mb-1 font-medium">Investment Title *</label>
              <input
                type="text"
                value={ipoTitle}
                onChange={(e) => setIpoTitle(e.target.value)}
                placeholder="E.g. XYZ Ltd IPO"
                className="w-full rounded-md border border-gray-700 bg-background p-3 focus:outline-none focus:ring-2 focus:ring-accent text-foreground"
                required
              />
            </div>
            <div>
              <label className="block mb-1 font-medium">Description</label>
              <textarea
                value={ipoDescription}
                onChange={(e) => setIpoDescription(e.target.value)}
                placeholder="Details about this investment opportunity"
                className="w-full rounded-md border border-gray-700 bg-background p-3 resize-y min-h-[100px] focus:outline-none focus:ring-2 focus:ring-accent text-foreground"
              />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block mb-1 font-medium">Target Amount (₹) *</label>
                <input
                  type="number"
                  value={targetAmount}
                  onChange={(e) => setTargetAmount(e.target.value)}
                  placeholder="E.g. 10,00,000"
                  className="w-full rounded-md border border-gray-700 bg-background p-3 focus:outline-none focus:ring-2 focus:ring-accent text-foreground"
                  min={0}
                  required
                />
              </div>
              <div>
                <label className="block mb-1 font-medium">Deadline *</label>
                <input
                  type="date"
                  value={deadline}
                  onChange={(e) => setDeadline(e.target.value)}
                  className="w-full rounded-md border border-gray-700 bg-background p-3 focus:outline-none focus:ring-2 focus:ring-accent text-foreground"
                  required
                />
              </div>
            </div>
            <div className="flex justify-end gap-4 pt-6">
              <button
                type="reset"
                onClick={resetForm}
                className="bg-red-600 px-6 py-2 rounded-lg font-semibold text-white hover:bg-red-700 transition"
              >
                Reset
              </button>
              <button
                type="submit"
                disabled={!canGoNextStep()}
                className={`bg-accent px-6 py-2 rounded-lg font-semibold text-accent-foreground transition
                  ${!canGoNextStep() ? "opacity-50 cursor-not-allowed" : "hover:bg-accent/80"}`}
              >
                Next
              </button>
            </div>
          </form>
        </section>
      )}

      {step === 2 && (
        <section className="bg-card rounded-2xl p-8 shadow-lg glass max-w-6xl mx-auto animate-slide-up space-y-6">
          <h2 className="text-2xl font-semibold flex items-center gap-2">
            <Users className="h-6 w-6 text-accent" />
            Select Collaborators
          </h2>
          <p className="text-gray-400 mb-4">
            Pick friends who will join you in this investment group.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 max-h-[400px] overflow-y-auto">
            {friendsData.map((friend) => {
              const selected = selectedFriends.some((f) => f.id === friend.id);
              return (
                <div
                  key={friend.id}
                  onClick={() => toggleFriendSelection(friend)}
                  className={`flex items-center gap-4 p-4 rounded-xl cursor-pointer shadow-md transition-shadow duration-300
                    ${
                      selected
                        ? "bg-accent text-accent-foreground shadow-accent"
                        : "bg-[#161b22] hover:shadow-accent"
                    }
                  `}
                >
                  <div
                    className={`w-12 h-12 rounded-full flex items-center justify-center font-semibold text-xl ${
                      friend.online ? "bg-green-500" : "bg-gray-600"
                    }`}
                  >
                    {friend.name[0]}
                  </div>
                  <div>
                    <p className="font-semibold">{friend.name}</p>
                    <p className="text-sm text-gray-400">{friend.email}</p>
                    <p
                      className={`text-xs font-medium mt-1 ${
                        friend.online ? "text-green-400" : "text-gray-500"
                      }`}
                    >
                      {friend.online ? "Online" : "Offline"}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
          <div className="flex justify-between pt-6">
            <button
              onClick={() => setStep(1)}
              className="bg-card text-foreground px-6 py-2 rounded-lg font-semibold shadow-md hover:bg-background transition"
            >
              <ArrowLeft className="inline-block mr-2" />
              Back
            </button>
            <button
              onClick={() => canGoNextStep() && setStep(3)}
              disabled={!canGoNextStep()}
              className={`bg-accent px-6 py-2 rounded-lg font-semibold text-accent-foreground transition
                ${!canGoNextStep() ? "opacity-50 cursor-not-allowed" : "hover:bg-accent/80"}`}
            >
              Next
              <ArrowRight className="inline-block ml-2" />
            </button>
          </div>
        </section>
      )}

      {step === 3 && (
        <section className="space-y-10 max-w-7xl mx-auto animate-slide-up">
          <div className="bg-gradient-to-tr from-[#1e2761] via-[#232b5d] to-[#1a1f3c] rounded-2xl shadow-2xl p-6 md:p-8 flex flex-col md:flex-row md:items-center md:justify-between gap-6 glass">
            <div>
              <h3 className="text-2xl font-semibold mb-1">{ipoTitle} Investment Group</h3>
              <p className="opacity-80 max-w-md">{ipoDescription || "No description provided."}</p>
              <p className="mt-2 text-sm opacity-70">
                Target: <span className="font-semibold">₹{Number(targetAmount).toLocaleString()}</span> | Deadline:{" "}
                <span className="font-semibold">{new Date(deadline).toLocaleDateString()}</span>
              </p>
            </div>
            <div className="bg-background/60 rounded-xl p-6 flex flex-col items-center justify-center min-w-[260px] glass">
              <div className="flex items-center gap-3 mb-2">
                <Users className="h-6 w-6 text-accent" />
                <span className="font-semibold">Collaborators</span>
              </div>
              <p className="text-sm opacity-70 text-center max-w-xs">
                {selectedFriends.length} collaborator{selectedFriends.length !== 1 ? "s" : ""} joined
              </p>
            </div>
          </div>

          {/* Investment Tracking */}
          <div className="bg-card/80 backdrop-blur-md rounded-2xl shadow-xl p-6 flex flex-col gap-2 transition-transform duration-300 hover:-translate-y-1 hover:shadow-2xl hover:ring-2 hover:ring-accent/30 glass">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <DollarSign className="h-6 w-6 text-accent" />
              Investment Tracking
            </h2>
            <div className="overflow-x-auto max-h-[280px]">
              <table className="min-w-full text-left text-sm">
                <thead className="border-b border-gray-700">
                  <tr>
                    <th className="p-3">Collaborator</th>
                    <th className="p-3">Amount (₹)</th>
                    <th className="p-3">Date</th>
                    <th className="p-3">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {investmentsData.map((inv) => {
                    const friend = friendsData.find((f) => f.id === inv.friendId);
                    return (
                      <tr
                        key={inv.id}
                        className="border-b border-gray-700 hover:bg-background/30 transition-colors cursor-pointer"
                      >
                        <td className="p-3">{friend?.name || "Unknown"}</td>
                        <td className="p-3">{inv.amount.toLocaleString()}</td>
                        <td className="p-3">{new Date(inv.date).toLocaleDateString()}</td>
                        <td className="p-3">
                          <span
                            className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold ${
                              inv.status === "Confirmed"
                                ? "bg-green-600 text-green-100"
                                : "bg-yellow-600 text-yellow-100"
                            }`}
                          >
                            {inv.status === "Confirmed" && <CheckCircle className="h-4 w-4" />}
                            {inv.status}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            <p className="text-right font-semibold text-lg mt-4">
              Total Confirmed Investment: ₹{totalInvested.toLocaleString()}
            </p>
          </div>

          {/* Contribution History + Chat */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Contribution History */}
            <div className="bg-card rounded-2xl p-6 shadow-lg animate-slide-up glass max-h-[400px] overflow-y-auto">
              <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
                <DollarSign className="h-6 w-6 text-accent" />
                Contribution History
              </h2>
              <ul className="space-y-4">
                {investmentsData
                  .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
                  .map((inv) => {
                    const friend = friendsData.find((f) => f.id === inv.friendId);
                    return (
                      <li
                        key={inv.id}
                        className="flex justify-between items-center p-4 bg-[#161b22] rounded-lg shadow hover:shadow-accent transition-shadow duration-300"
                      >
                        <div>
                          <p>
                            <span className="font-semibold">{friend?.name || "Unknown"}</span> contributed{" "}
                            <span className="font-semibold">₹{inv.amount.toLocaleString()}</span>
                          </p>
                          <p className="text-xs opacity-70">{new Date(inv.date).toLocaleDateString()}</p>
                        </div>
                        <span
                          className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold ${
                            inv.status === "Confirmed"
                              ? "bg-green-600 text-green-100"
                              : "bg-yellow-600 text-yellow-100"
                          }`}
                        >
                          {inv.status === "Confirmed" && <CheckCircle className="h-4 w-4" />}
                          {inv.status}
                        </span>
                      </li>
                    );
                  })}
              </ul>
            </div>

            {/* Chat Box */}
            <div className="bg-card rounded-2xl p-6 shadow-lg animate-slide-up glass flex flex-col max-h-[400px]">
              <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
                <MessageCircle className="h-6 w-6 text-accent" />
                Group Chat
              </h2>
              <div className="flex-1 overflow-y-auto mb-4 space-y-3 border border-gray-700 rounded-md p-3 bg-[#0d1117]">
                {chatMessages.length === 0 && (
                  <p className="text-gray-400 text-center mt-6">No messages yet. Start chatting!</p>
                )}
                {chatMessages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`p-2 rounded-md max-w-[80%] ${
                      msg.sender === "You" ? "bg-accent text-accent-foreground ml-auto" : "bg-card"
                    }`}
                  >
                    <p className="text-sm font-semibold">{msg.sender}</p>
                    <p>{msg.text}</p>
                  </div>
                ))}
              </div>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSendMessage();
                }}
                className="flex gap-3"
              >
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Type a message..."
                  className="flex-1 rounded-md px-4 py-2 bg-[#0d1117] border border-gray-700 focus:outline-none focus:ring-2 focus:ring-accent text-white"
                />
                <button
                  type="submit"
                  className="bg-accent px-4 py-2 rounded-md text-accent-foreground font-semibold hover:bg-accent/80 transition-all duration-200"
                >
                  Send
                </button>
              </form>
            </div>
          </div>

          <div className="flex justify-between pt-6">
            <button
              onClick={() => setStep(2)}
              className="bg-card text-foreground px-6 py-2 rounded-lg font-semibold shadow-md hover:bg-background transition"
            >
              <ArrowLeft className="inline-block mr-2" />
              Back
            </button>
            <button
              onClick={() => {
                resetForm();
                setStep(1);
              }}
              className="bg-green-600 px-6 py-2 rounded-lg font-semibold text-white hover:bg-green-700 transition"
            >
              Finish & New Investment
            </button>
          </div>
        </section>
      )}
    </div>
  );
}
