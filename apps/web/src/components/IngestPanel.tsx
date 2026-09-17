import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api, type IngestResult } from "../lib/api";
import { Card, GhostButton, PrimaryButton } from "./ui";

const FORM16_FIXTURE = {
  kind: "form16",
  employer: "Northstar Labs Pvt Ltd",
  pan_masked: "ABCDE****F",
  basic_salary: { amount: 3_600_000, source_quote: "Basic Salary 3600000", page: 1 },
  confidence: 0.92,
};

export function IngestPanel({
  householdId,
  onQueue,
}: {
  householdId: string;
  onQueue: (queue: unknown) => void;
}) {
  const queryClient = useQueryClient();
  const [kind, setKind] = useState("form16");
  const [raw, setRaw] = useState("");
  const [review, setReview] = useState<IngestResult | null>(null);
  const [patch, setPatch] = useState("");

  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: ["desk-queue", householdId] });
  };

  const ingest = useMutation({
    mutationFn: () =>
      api.ingestBook({
        household_id: householdId,
        kind,
        raw_text: raw,
        vlm_override: kind === "form16" && !raw ? FORM16_FIXTURE : undefined,
      }),
    onSuccess: (data) => {
      if (data.status === "needs_review") setReview(data);
      else {
        setReview(null);
        if (data.queue) onQueue(data.queue);
        refresh();
      }
    },
  });

  const resume = useMutation({
    mutationFn: () => {
          let parsed: Record<string, unknown> = {};
          if (patch.trim()) {
            try {
              parsed = JSON.parse(patch) as Record<string, unknown>;
            } catch {
              throw new Error("Patch must be JSON object text.");
            }
          }
      return api.resumeIngest(review?.threadId || "", parsed);
    },
    onSuccess: (data) => {
      setReview(null);
      if (data.queue) onQueue(data.queue);
      refresh();
    },
  });

  return (
    <Card className="mb-6">
      <h2 className="mb-1 font-semibold text-ink-900">Ingest</h2>
      <p className="mb-4 text-xs text-ink-500">
        Form 16, AIS, CAS, or a text event. Low confidence pauses for review. No silent
        defaults.
      </p>
      <div className="flex flex-wrap gap-2">
        <select
          className="border border-ink-200 bg-paper-50 px-3 py-2 text-sm"
          value={kind}
          onChange={(e) => setKind(e.target.value)}
        >
          <option value="form16">Form 16</option>
          <option value="ais">AIS</option>
          <option value="cas">CAS</option>
          <option value="text_event">Text event</option>
        </select>
        <GhostButton type="button" onClick={() => ingest.mutate()} disabled={ingest.isPending}>
          {kind === "form16" ? "Drop Form 16 fixture" : "Parse"}
        </GhostButton>
      </div>
      {kind === "text_event" && (
        <textarea
          className="mt-3 field w-full"
          rows={3}
          placeholder="Add a 12 lakh bonus on 12 Sep 2026"
          value={raw}
          onChange={(e) => setRaw(e.target.value)}
        />
      )}
      {ingest.error && (
        <p className="mt-3 text-xs text-red-400">{(ingest.error as Error).message}</p>
      )}
      {review && (
        <div className="mt-4 border-t border-ink-200 pt-4">
          <p className="text-sm text-ink-800">Needs review. Missing: {(review.missingFields || []).join(", ") || "fields"}</p>
          <pre className="mt-2 overflow-auto bg-ink-50 p-3 font-mono text-[11px]">
            {JSON.stringify(review.extracted, null, 2)}
          </pre>
          <textarea
            className="mt-2 field w-full font-mono text-xs"
            rows={3}
            placeholder='{"amount_inr": 1200000}'
            value={patch}
            onChange={(e) => setPatch(e.target.value)}
          />
          <PrimaryButton
            type="button"
            className="mt-2"
            onClick={() => resume.mutate()}
            disabled={resume.isPending}
          >
            Resume apply
          </PrimaryButton>
        </div>
      )}
    </Card>
  );
}
