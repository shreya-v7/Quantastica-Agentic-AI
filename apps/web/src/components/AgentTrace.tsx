import { CheckCircle2, CircleDashed, Loader2, XCircle } from "lucide-react";
import type { AgentStep } from "@quantastica/types";

function StepIcon({ status }: { status: AgentStep["status"] }) {
  if (status === "completed") return <CheckCircle2 className="h-5 w-5 text-emerald-600" />;
  if (status === "failed") return <XCircle className="h-5 w-5 text-red-600" />;
  if (status === "running") return <Loader2 className="h-5 w-5 animate-spin text-brand-600" />;
  return <CircleDashed className="h-5 w-5 text-ink-400" />;
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
              <span className="font-medium capitalize text-ink-900">{step.name}</span>
              <span className="text-xs text-ink-400">{step.durationMs.toFixed(0)} ms</span>
            </div>
            <p className="text-sm text-ink-500">{step.inputSummary}</p>
            {step.outputSummary && (
              <p className="mt-1 text-sm text-ink-700">{step.outputSummary}</p>
            )}
            {step.error && <p className="mt-1 text-sm text-red-600">{step.error}</p>}
          </div>
        </li>
      ))}
    </ol>
  );
}
