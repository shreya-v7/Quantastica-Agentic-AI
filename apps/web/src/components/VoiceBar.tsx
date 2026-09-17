import { useMutation } from "@tanstack/react-query";
import { Mic } from "lucide-react";
import { useState } from "react";
import { api, type SpeechResult } from "../lib/api";
import { GhostButton } from "./ui";

export function VoiceBar({
  householdId,
  onQueue,
}: {
  householdId: string;
  onQueue?: () => void;
}) {
  const [heard, setHeard] = useState<SpeechResult | null>(null);
  const speak = useMutation({
    mutationFn: (utterance: string) => api.transcribe(householdId, `text:${utterance}`),
    onSuccess: (data) => {
      setHeard(data);
      onQueue?.();
    },
  });

  return (
    <div className="mb-4 space-y-2">
      <div className="flex flex-wrap gap-2">
        <GhostButton
          type="button"
          className="inline-flex items-center gap-2"
          disabled={speak.isPending}
          onClick={() => speak.mutate("What fired for Mehta")}
        >
          <Mic className="h-4 w-4" />
          Ask the queue
        </GhostButton>
        <GhostButton
          type="button"
          disabled={speak.isPending}
          onClick={() => speak.mutate("Why is the Reliance row there")}
        >
          Why Reliance
        </GhostButton>
        <GhostButton
          type="button"
          disabled={speak.isPending}
          onClick={() => speak.mutate("Add a 12 lakh bonus on 12 Sep 2026")}
        >
          Dictate bonus
        </GhostButton>
      </div>
      {heard?.answer && (
        <p className="text-sm text-ink-700">
          <span className="font-mono text-[10px] uppercase tracking-label text-pine-500">
            {heard.intent}
          </span>{" "}
          {heard.answer}
        </p>
      )}
      {speak.error && <p className="text-xs text-red-400">{(speak.error as Error).message}</p>}
    </div>
  );
}
