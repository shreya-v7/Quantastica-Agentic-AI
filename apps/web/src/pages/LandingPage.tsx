import { Link } from "react-router-dom";
import { BrandMark, Disclaimer } from "../components/Disclaimer";
import { Frame, IstClock, LiveDot, PrimaryButton } from "../components/ui";
import { ThemeToggle } from "../components/ThemeToggle";

const STEPS = [
  { name: "Planner", detail: "Turns the question into a strict JSON plan." },
  { name: "Researcher", detail: "Computes weights, cost, and allocation from holdings." },
  { name: "Retrieve", detail: "Hybrid search over your statements. Dense plus BM25." },
  { name: "Risk", detail: "HHI, top-5 share, diversification. Unit tested, no LLM." },
  { name: "Insight", detail: "Findings must cite metric ids that actually exist." },
  { name: "Summarizer", detail: "Plain language. Same numbers. A refusal if it cannot." },
];

const TELEMETRY = [
  ["REGIME", "WATCH"],
  ["LOT", "CLOCK"],
  ["HHI", "TRIPWIRE"],
  ["80C", "HEADROOM"],
];

export function LandingPage() {
  return (
    <div className="hud-line min-h-screen bg-paper-100 text-ink-900">
      <header className="border-b border-ink-200/80">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <BrandMark />
          <div className="hidden items-center gap-5 font-mono text-[11px] uppercase tracking-label text-ink-400 md:flex">
            <span className="inline-flex items-center gap-2 text-pine-500">
              <LiveDot /> sys.local
            </span>
            <span>compute-first</span>
            <IstClock />
          </div>
          <nav className="flex items-center gap-6 text-[13px]">
            <a href="#method" className="hidden text-ink-500 hover:text-ink-900 sm:inline">
              Method
            </a>
            <a href="#product" className="hidden text-ink-500 hover:text-ink-900 sm:inline">
              Product
            </a>
            <ThemeToggle />
            <Link to="/signin" className="text-ink-500 hover:text-ink-900">
              Sign in
            </Link>
            <Link to="/desk">
              <PrimaryButton type="button">Open desk</PrimaryButton>
            </Link>
          </nav>
        </div>
      </header>

      <section className="mx-auto grid max-w-6xl items-center gap-12 px-6 pb-20 pt-14 lg:grid-cols-[1.15fr_0.85fr] lg:pt-20">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-label text-pine-500">
            Exception control plane
          </p>
          <h1 className="mt-5 max-w-2xl font-display text-[3.4rem] font-light leading-[0.95] tracking-tight text-ink-900 md:text-[5.2rem]">
            The book changes.
            <br />
            <span className="text-neon">The rupee fires.</span>
          </h1>
          <p className="mt-7 max-w-xl text-[15px] leading-7 text-ink-500">
            A desk for Indian household exceptions: regime, lot clock, concentration, deductions.
            Calculators produce every rupee. The model classifies and writes. It does not invent
            figures.
          </p>
          <div className="mt-9 flex flex-wrap gap-3">
            <Link to="/desk">
              <PrimaryButton type="button">Open the queue</PrimaryButton>
            </Link>
            <Link
              to="/demo"
              className="border border-ink-200 px-4 py-2.5 text-sm font-medium text-ink-700 hover:border-pine-500 hover:text-ink-900"
            >
              3-minute demo
            </Link>
            <Link
              to="/ask"
              className="border border-ink-200 px-4 py-2.5 text-sm font-medium text-ink-700 hover:border-pine-500 hover:text-ink-900"
            >
              Ask a follow-up
            </Link>
          </div>
          <div className="mt-12 grid grid-cols-2 gap-px border border-ink-200 bg-ink-200 sm:grid-cols-4">
            {TELEMETRY.map(([k, v]) => (
              <div key={k} className="bg-paper-100 px-4 py-3">
                <p className="font-mono text-[10px] tracking-label text-ink-400">{k}</p>
                <p className="mt-1 font-mono text-xs text-pine-500">{v}</p>
              </div>
            ))}
          </div>
          <Disclaimer className="mt-6 max-w-md" />
        </div>

        <Frame label="run 06" className="p-6 pt-8">
          <div className="scan-mask">
          <div className="flex items-center justify-between">
            <p className="font-mono text-[11px] uppercase tracking-label text-ink-400">query</p>
            <p className="inline-flex items-center gap-2 font-mono text-[11px] text-pine-500">
              <LiveDot /> live trace
            </p>
          </div>
          <p className="mt-4 font-mono text-sm text-ink-800">
            How concentrated is the Mehta book?
            <span className="ml-0.5 inline-block h-4 w-1.5 translate-y-0.5 bg-pine-500 animate-blink" />
          </p>
          <ol className="mt-6 space-y-0">
            {STEPS.map((step, i) => (
              <li key={step.name} className="grid grid-cols-[52px_1fr] gap-3 border-t border-ink-200/80 py-3">
                <p className="font-mono text-[11px] text-pine-500">
                  {String(i + 1).padStart(2, "0")}
                </p>
                <div>
                  <p className="font-display text-sm tracking-wide text-ink-900">{step.name}</p>
                  <p className="mt-0.5 text-[13px] leading-5 text-ink-500">{step.detail}</p>
                </div>
              </li>
            ))}
          </ol>
          </div>
        </Frame>
      </section>

      <section id="method" className="border-y border-ink-200">
        <div className="mx-auto grid max-w-6xl gap-px bg-ink-200 px-0 md:grid-cols-3">
          {[
            {
              n: "01",
              title: "Compute first",
              body: "Old vs new regime, SIP math, HHI, FOIR. If the calculator cannot run, we ask for the missing input instead of guessing.",
            },
            {
              n: "02",
              title: "Retrieve with proof",
              body: "LlamaIndex chunks, pgvector plus Postgres BM25, fused with reciprocal rank fusion. Answers cite the passage.",
            },
            {
              n: "03",
              title: "Eval before ship",
              body: "India golden cases must match calculator output in CI. A FinanceBench sample checks retrieval. RAGAS is optional, never a substitute.",
            },
          ].map((item) => (
            <div key={item.title} className="bg-paper-100 px-8 py-14">
              <p className="font-mono text-[11px] text-pine-500">{item.n}</p>
              <h2 className="mt-3 font-display text-2xl font-light tracking-tight text-ink-900">
                {item.title}
              </h2>
              <p className="mt-4 max-w-sm text-sm leading-6 text-ink-500">{item.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="product" className="mx-auto max-w-6xl px-6 py-16">
        <h2 className="font-mono text-[11px] uppercase tracking-label text-ink-400">Stack</h2>
        <div className="mt-6 grid gap-px overflow-hidden border border-ink-200 bg-ink-200 md:grid-cols-2">
          {[
            "LangGraph pipeline with a persisted step trace",
            "MCP server so Cursor and Claude can call the same calculators",
            "Postgres, Redis, GCS or S3. Local, GCP, or AWS from one factory",
            "Paper trading, alerts, Account Aggregator and Kite stubs when you are ready",
          ].map((line, i) => (
            <div key={line} className="flex items-start gap-4 bg-paper-100 px-5 py-4">
              <span className="font-mono text-[11px] text-pine-500">
                {String(i + 1).padStart(2, "0")}
              </span>
              <p className="text-sm leading-6 text-ink-700">{line}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="border-t border-ink-200 px-6 py-10">
        <div className="mx-auto flex max-w-6xl flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <BrandMark />
          <Disclaimer />
        </div>
      </footer>
    </div>
  );
}
