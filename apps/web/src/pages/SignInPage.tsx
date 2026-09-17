import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { api, getAccessToken, setAccessToken } from "../lib/api";
import { BrandMark, Disclaimer } from "../components/Disclaimer";
import { Badge, Card, IstClock, PrimaryButton } from "../components/ui";
import { ThemeToggle } from "../components/ThemeToggle";
import { ErrorState } from "../components/states";

export function SignInPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [signedIn, setSignedIn] = useState(Boolean(getAccessToken()));

  const login = useMutation({
    mutationFn: ({ email, password, totp }: { email: string; password: string; totp?: string }) =>
      api.login(email, password, totp),
    onSuccess: (pair) => {
      setAccessToken(pair.accessToken);
      setSignedIn(true);
      navigate("/desk");
    },
  });

  const register = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      api.register(email, password),
    onSuccess: () => setMode("login"),
  });

  const pending = login.isPending || register.isPending;
  const error = (login.error ?? register.error) as Error | null;

  return (
    <div className="hud-line min-h-screen bg-paper-100">
      <header className="mx-auto flex max-w-6xl items-center justify-between border-b border-ink-200 px-6 py-4">
        <Link to="/">
          <BrandMark />
        </Link>
        <div className="flex items-center gap-6">
          <IstClock />
          <ThemeToggle />
          <Link to="/desk" className="text-sm text-ink-500 hover:text-ink-900">
            Continue to desk
          </Link>
        </div>
      </header>
      <div className="mx-auto max-w-md px-6 py-16">
        <p className="font-mono text-[10px] uppercase tracking-label text-pine-500">// access</p>
        <h1 className="mt-2 font-display text-4xl font-light tracking-tight">Sign in</h1>
        <p className="mt-2 text-sm text-ink-500">
          In local development the API may run without auth. Production always requires a session.
        </p>

        {signedIn ? (
          <Card className="mt-8">
            <div className="flex items-center justify-between">
              <span className="text-sm text-ink-600">You have an active session.</span>
              <Badge tone="low">signed in</Badge>
            </div>
            <div className="mt-4 flex gap-3">
              <Link to="/desk">
                <PrimaryButton type="button">Go to desk</PrimaryButton>
              </Link>
              <button
                onClick={() => {
                  setAccessToken(null);
                  setSignedIn(false);
                }}
                className="text-sm text-ink-500"
              >
                Sign out
              </button>
            </div>
          </Card>
        ) : (
          <Card className="mt-8">
            <div className="mb-4 flex gap-2">
              {(["login", "register"] as const).map((m) => (
                <button
                  key={m}
                  onClick={() => setMode(m)}
                  className={`px-3 py-1.5 text-sm font-medium ${
                    mode === m ? "bg-pine-600 text-[rgb(var(--on-accent))]" : "border border-ink-200 text-ink-600"
                  }`}
                >
                  {m === "login" ? "Sign in" : "Create account"}
                </button>
              ))}
            </div>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                const f = new FormData(e.currentTarget);
                const email = String(f.get("email"));
                const password = String(f.get("password"));
                if (mode === "login") {
                  login.mutate({ email, password, totp: String(f.get("totp") || "") || undefined });
                } else {
                  register.mutate({ email, password });
                }
              }}
              className="space-y-3"
            >
              <input
                name="email"
                type="email"
                placeholder="you@example.in"
                required
                className="field"
              />
              <input
                name="password"
                type="password"
                placeholder="Password (min 10 chars)"
                required
                minLength={mode === "register" ? 10 : 1}
                className="field"
              />
              {mode === "login" && (
                <input
                  name="totp"
                  placeholder="TOTP code if enabled"
                  className="field"
                />
              )}
              <PrimaryButton disabled={pending} className="w-full">
                {mode === "login" ? "Sign in" : "Create account"}
              </PrimaryButton>
            </form>
            {register.isSuccess && mode === "login" && (
              <p className="mt-3 text-sm text-pine-500">Account created. Sign in now.</p>
            )}
            {error && (
              <div className="mt-3">
                <ErrorState message={error.message} />
              </div>
            )}
          </Card>
        )}
        <Disclaimer className="mt-6" />
      </div>
    </div>
  );
}
