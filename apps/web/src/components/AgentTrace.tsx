import { CheckCircle2, CircleDashed, Loader2, XCircle } from "lucide-react";
import type { AgentStep } from "@quantastica/types";

function StepIcon({ status }: { status: AgentStep["status"] }) {
  if (status === "completed") return <CheckCircle2 className="h-4 w-4 text-pine-500" />;
  if (status === "failed") return <XCircle className="h-4 w-4 text-red-400" />;
  if (status === "running") return <Loader2 className="h-4 w-4 animate-spin text-pine-500" />;
  return <CircleDashed className="h-4 w-4 text-ink-400" />;
}

export function AgentTrace({ steps }: { steps: AgentStep[] }) {
  if (steps.length === 0) {
    return <p className="text-sm text-ink-500">Waiting for the first step...</p>;
  }
  return (
    <ol className="space-y-3">
      {steps.map((step) => (
        <li key={step.name} className="flex gap-3">
          <div className="mt-0.5">
            <StepIcon status={step.status} />
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <span className="font-mono text-[13px] font-medium capitalize text-ink-900">{step.name}</span>
              <span className="text-xs text-ink-400">{step.durationMs.toFixed(0)} ms</span>
            </div>
            <p className="text-sm text-ink-500">{step.inputSummary}</p>
            {step.outputSummary && (
              <p className="mt-1 text-sm text-ink-700">{step.outputSummary}</p>
            )}
            {step.error && <p className="mt-1 text-sm text-red-400">{step.error}</p>}
          </div>
        </li>
      ))}
    </ol>
  );
}
