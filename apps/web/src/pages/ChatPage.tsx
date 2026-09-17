import { useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";
import type { AgentRun } from "@quantastica/types";
import { api } from "../lib/api";
import { usePortfolios } from "../hooks/useApi";
import { Badge, Card, PageHeader, PrimaryButton } from "../components/ui";
import { Disclaimer } from "../components/Disclaimer";
import { ErrorState } from "../components/states";
import { AgentTrace } from "../components/AgentTrace";
import type { ChatResponse } from "../lib/domain";
import { VoiceBar } from "../components/VoiceBar";

interface Turn {
  role: "user" | "assistant";
  text: string;
  response?: ChatResponse;
  run?: AgentRun;
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
  const [docTitle, setDocTitle] = useState("");
  const [docText, setDocText] = useState("");

  const documents = useQuery({ queryKey: ["documents"], queryFn: api.listDocuments });
  const flags = useQuery({ queryKey: ["flags"], queryFn: api.flags });
  const [tradeNote, setTradeNote] = useState<string | null>(null);
  const ingest = useMutation({
    mutationFn: () => api.ingestDocument(docTitle, docText),
    onSuccess: () => {
      setDocTitle("");
      setDocText("");
      documents.refetch();
    },
  });

  const chat = useMutation({
    mutationFn: async (text: string) => {
      const response = await api.chat(text, portfolioId || undefined, parseParams(text));
      const runId = response.data?.runId;
      const run =
        typeof runId === "string" ? await api.getRun(runId).catch(() => undefined) : undefined;
      return { response, run };
    },
    onSuccess: ({ response, run }, text) => {
      setTurns((prev) => [
        ...prev,
        { role: "user", text },
        { role: "assistant", text: response.answer, response, run },
      ]);
      setMessage("");
    },
  });

  const send = (text: string) => {
    if (!text.trim()) return;
    const trimmed = text.trim();
    if (flags.data?.tradingChat && /^(buy|sell)\b/i.test(trimmed)) {
      api
        .parseTrade(trimmed)
        .then((parsed) => {
          const draft = parsed.draft as { clarification?: string; side?: string; quantity?: number; symbol?: string } | undefined;
          const notes = (parsed.notes as string[] | undefined) ?? [];
          setTradeNote(
            draft?.clarification ||
              `${draft?.side} ${draft?.quantity} ${draft?.symbol}. Confirm on Trades. ${notes.join(" ")}`,
          );
          setMessage("");
        })
        .catch((err: Error) => setTradeNote(err.message));
      return;
    }
    chat.mutate(trimmed);
  };

  return (
    <div>
      <PageHeader
        title="Ask"
        subtitle="Tax, SIP, concentration, quotes, and your documents. Numbers come from calculators and holdings. The model only writes."
      />

      <div className="mb-4 flex flex-wrap items-center gap-3">
        <select
          value={portfolioId}
          onChange={(e) => setPortfolioId(e.target.value)}
          className="field max-w-xs"
        >
          <option value="">No portfolio context</option>
          {(portfolios.data ?? []).map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
        <Link to="/agents" className="text-sm text-pine-500">
          Open a full analysis run
        </Link>
      </div>

      <VoiceBar householdId="hh_mehta" />
      {tradeNote && <p className="mb-4 text-sm text-ink-700">{tradeNote}</p>}

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_280px]">
        <div>
          <div className="space-y-3">
            {turns.length === 0 && (
              <Card>
                <p className="mb-3 text-sm text-ink-500">Try one of these</p>
                <div className="flex flex-wrap gap-2">
                  {SUGGESTIONS.map((s) => (
                    <button
                      key={s}
                      onClick={() => send(s)}
                      className="border border-ink-200 px-3 py-1 text-sm text-ink-600 hover:bg-ink-50"
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
                    <div className="border border-pine-700 bg-pine-700 px-4 py-2 text-sm text-[rgb(var(--on-accent))]">
                      {turn.text}
                    </div>
                  ) : (
                    <Card>
                      <div className="mb-2 flex flex-wrap items-center gap-2">
                        <Badge tone="info">{turn.response?.intent}</Badge>
                        {turn.response?.needsInput && <Badge tone="medium">needs input</Badge>}
                      </div>
                      <p className="whitespace-pre-wrap text-sm leading-6 text-ink-800">{turn.text}</p>
                      {turn.response?.needsInput && (
                        <p className="mt-2 text-xs text-ink-500">
                          Provide: {turn.response.needsInput.join(", ")}
                        </p>
                      )}
                      {turn.response?.citations && turn.response.citations.length > 0 && (
                        <p className="mt-2 font-mono text-[11px] text-ink-400">
                          Cites: {turn.response.citations.join(" · ")}
                        </p>
                      )}
                      {turn.run && (
                        <div className="mt-4 border-t border-ink-100 pt-4">
                          <p className="mb-2 font-mono text-[11px] uppercase tracking-label text-ink-400">
                            How this was computed
                          </p>
                          <AgentTrace steps={turn.run.steps} />
                        </div>
                      )}
                    </Card>
                  )}
                </div>
              </div>
            ))}

            {chat.isPending && <p className="text-sm text-ink-400">Computing...</p>}
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
              placeholder="Ask about tax, SIP, your portfolio, a stock, or an uploaded statement"
              className="field flex-1 py-3 font-mono text-[13px]"
            />
            <PrimaryButton type="submit" disabled={chat.isPending}>
              Send
            </PrimaryButton>
          </form>
          <Disclaimer className="mt-3" />
        </div>

        <aside className="space-y-4">
          <Card>
            <h2 className="font-mono text-[11px] uppercase tracking-label text-ink-400">Documents</h2>
            <p className="mt-1 text-xs text-ink-500">
              Statements are chunked with LlamaIndex and retrieved with hybrid search.
            </p>
            <form
              className="mt-3 space-y-2"
              onSubmit={(e) => {
                e.preventDefault();
                if (docTitle.trim() && docText.trim()) ingest.mutate();
              }}
            >
              <input
                value={docTitle}
                onChange={(e) => setDocTitle(e.target.value)}
                placeholder="Title"
                className="field"
              />
              <textarea
                value={docText}
                onChange={(e) => setDocText(e.target.value)}
                placeholder="Paste CAS, 10-K excerpt, or a note"
                rows={4}
                className="field"
              />
              <PrimaryButton type="submit" disabled={ingest.isPending} className="w-full">
                {ingest.isPending ? "Indexing..." : "Index document"}
              </PrimaryButton>
            </form>
            {ingest.error && <p className="mt-2 text-xs text-red-400">{(ingest.error as Error).message}</p>}
            <ul className="mt-3 space-y-1 text-xs text-ink-500">
              {(documents.data ?? []).map((d) => (
                <li key={d.id}>{d.title}</li>
              ))}
              {documents.data?.length === 0 && <li>No documents yet.</li>}
            </ul>
          </Card>
        </aside>
      </div>
    </div>
  );
}

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
