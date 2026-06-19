import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "../lib/api";
import { usePortfolios } from "../hooks/useApi";
import { Card, PageHeader, Badge } from "../components/ui";
import { ErrorState } from "../components/states";
import type { ChatResponse } from "../lib/domain";

interface Turn {
  role: "user" | "assistant";
  text: string;
  response?: ChatResponse;
}

const SUGGESTIONS = [
  "Compare my tax under the old and new regime",
  "What SIP do I need for 2 crore in 15 years?",
  "How concentrated is my portfolio?",
  "What is the latest price of RELIANCE.NS?",
];

export function ChatPage() {
  const portfolios = usePortfolios();
  const [portfolioId, setPortfolioId] = useState("");
  const [message, setMessage] = useState("");
  const [turns, setTurns] = useState<Turn[]>([]);

  const chat = useMutation({
    mutationFn: (text: string) =>
      api.chat(text, portfolioId || undefined, parseParams(text)),
    onSuccess: (response, text) => {
      setTurns((prev) => [
        ...prev,
        { role: "user", text },
        { role: "assistant", text: response.answer, response },
      ]);
      setMessage("");
    },
  });

  const send = (text: string) => {
    if (text.trim()) chat.mutate(text.trim());
  };

  return (
    <div>
      <PageHeader
        title="Ask Quantastica"
        subtitle="Conversational answers grounded in deterministic calculators and your portfolio."
      />

      <div className="mb-4 flex flex-wrap gap-3">
        <select
          value={portfolioId}
          onChange={(e) => setPortfolioId(e.target.value)}
          className="rounded-lg border border-ink-200 px-3 py-2 text-sm"
        >
          <option value="">No portfolio context</option>
          {(portfolios.data ?? []).map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-3">
        {turns.length === 0 && (
          <Card>
            <p className="mb-3 text-sm text-ink-500">Try one of these:</p>
            <div className="flex flex-wrap gap-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="rounded-full border border-ink-200 px-3 py-1 text-sm text-ink-600 hover:bg-ink-100"
                >
                  {s}
                </button>
              ))}
            </div>
          </Card>
        )}

        {turns.map((turn, i) => (
          <div key={i} className={turn.role === "user" ? "flex justify-end" : ""}>
            <div className={turn.role === "user" ? "max-w-[80%]" : "w-full"}>
              {turn.role === "user" ? (
                <div className="rounded-xl bg-brand-600 px-4 py-2 text-sm text-white">
                  {turn.text}
                </div>
              ) : (
                <Card>
                  <div className="mb-2 flex items-center gap-2">
                    <Badge tone="info">{turn.response?.intent}</Badge>
                    {turn.response?.needsInput && <Badge tone="medium">needs input</Badge>}
                  </div>
                  <p className="whitespace-pre-wrap text-sm text-ink-800">{turn.text}</p>
                  {turn.response?.needsInput && (
                    <p className="mt-2 text-xs text-ink-500">
                      Provide: {turn.response.needsInput.join(", ")}
                    </p>
                  )}
                  {turn.response?.data && (
                    <pre className="mt-3 overflow-x-auto rounded-lg bg-ink-50 p-3 text-xs text-ink-600">
                      {JSON.stringify(turn.response.data, null, 2)}
                    </pre>
                  )}
                </Card>
              )}
            </div>
          </div>
        ))}

        {chat.isPending && <p className="text-sm text-ink-400">Thinking...</p>}
        {chat.error && <ErrorState message={(chat.error as Error).message} />}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(message);
        }}
        className="mt-4 flex gap-2"
      >
        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask about tax, SIP, affordability, your portfolio, or a stock"
          className="flex-1 rounded-lg border border-ink-200 px-4 py-2 text-sm"
        />
        <button
          type="submit"
          disabled={chat.isPending}
          className="rounded-lg bg-brand-600 px-5 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  );
}

// Pull obvious numbers out of free text so computational intents have inputs to work
// with. The server still validates and asks for anything missing.
function parseParams(text: string): Record<string, unknown> {
  const params: Record<string, unknown> = {};
  const salary = text.match(/salary\s+(?:of\s+)?([\d,]+)/i);
  if (salary) params.basicSalary = Number(salary[1].replace(/,/g, ""));
  const crore = text.match(/([\d.]+)\s*crore/i);
  const lakh = text.match(/([\d.]+)\s*lakh/i);
  if (crore) params.targetInr = Number(crore[1]) * 1_00_00_000;
  else if (lakh) params.targetInr = Number(lakh[1]) * 1_00_000;
  const years = text.match(/(\d+)\s*year/i);
  if (years) params.years = Number(years[1]);
  return params;
}
