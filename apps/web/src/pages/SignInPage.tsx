import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api, getAccessToken, setAccessToken } from "../lib/api";
import { Card, PageHeader, Badge } from "../components/ui";
import { ErrorState } from "../components/states";

export function SignInPage() {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [signedIn, setSignedIn] = useState(Boolean(getAccessToken()));

  const login = useMutation({
    mutationFn: ({ email, password, totp }: { email: string; password: string; totp?: string }) =>
      api.login(email, password, totp),
    onSuccess: (pair) => {
      setAccessToken(pair.accessToken);
      setSignedIn(true);
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
    <div className="mx-auto max-w-md">
      <PageHeader
        title="Sign in"
        subtitle="In dev the API runs without auth, so this is optional. In prod a session is required."
      />

      {signedIn ? (
        <Card>
          <div className="flex items-center justify-between">
            <span className="text-sm text-ink-600">You have an active session.</span>
            <Badge tone="low">signed in</Badge>
          </div>
          <button
            onClick={() => {
              setAccessToken(null);
              setSignedIn(false);
            }}
            className="mt-4 rounded-lg border border-ink-200 px-3 py-1.5 text-sm text-ink-600"
          >
            Sign out
          </button>
        </Card>
      ) : (
        <Card>
          <div className="mb-4 flex gap-2">
            {(["login", "register"] as const).map((m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`rounded-lg px-3 py-1.5 text-sm font-medium ${
                  mode === m ? "bg-brand-600 text-white" : "border border-ink-200 text-ink-600"
                }`}
              >
                {m === "login" ? "Sign in" : "Register"}
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
              className="w-full rounded-lg border border-ink-200 px-3 py-2 text-sm"
            />
            <input
              name="password"
              type="password"
              placeholder="Password (min 10 chars)"
              required
              minLength={mode === "register" ? 10 : 1}
              className="w-full rounded-lg border border-ink-200 px-3 py-2 text-sm"
            />
            {mode === "login" && (
              <input
                name="totp"
                placeholder="TOTP code (if enabled)"
                className="w-full rounded-lg border border-ink-200 px-3 py-2 text-sm"
              />
            )}
            <button
              disabled={pending}
              className="w-full rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              {mode === "login" ? "Sign in" : "Create account"}
            </button>
          </form>
          {register.isSuccess && mode === "login" && (
            <p className="mt-3 text-sm text-emerald-600">Account created. Sign in now.</p>
          )}
          {error && (
            <div className="mt-3">
              <ErrorState message={error.message} />
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
