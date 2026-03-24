import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  onAuthStateChanged,
} from "firebase/auth";
import { doc, setDoc } from "firebase/firestore";
import { Link, useNavigate } from "react-router-dom";
import {
  ArrowRight,
  ChevronLeft,
  Lock,
  Mail,
  Phone,
  Shield,
  Sparkles,
  User,
} from "lucide-react";
import { auth, db } from "../auth/firebase";

const brandFeatures = [
  {
    icon: Sparkles,
    title: "Agentic intelligence",
    copy: "Purpose-built models for portfolio context and execution.",
  },
  {
    icon: Shield,
    title: "Enterprise-grade trust",
    copy: "Encryption in transit, auditable sessions, and clear data boundaries.",
  },
  {
    icon: Lock,
    title: "Unified workspace",
    copy: "One surface for insights, chat, and market workflows.",
  },
] as const;

export default function AuthPage() {
  const navigate = useNavigate();
  const [isSignup, setIsSignup] = useState(false);
  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    phone: "",
    password: "",
    confirmPassword: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (isSignup) {
        if (formData.password !== formData.confirmPassword) {
          setError("Passwords do not match.");
          setLoading(false);
          return;
        }

        const userCred = await createUserWithEmailAndPassword(
          auth,
          formData.email,
          formData.password
        );
        const uid = userCred.user.uid;

        await setDoc(doc(db, "users", uid), {
          fullName: formData.fullName,
          email: formData.email,
          phone: formData.phone,
          createdAt: new Date().toISOString(),
        });

        localStorage.setItem("userId", uid);
        navigate("/dashboard");
      } else {
        const userCred = await signInWithEmailAndPassword(
          auth,
          formData.email,
          formData.password
        );
        const uid = userCred.user.uid;
        localStorage.setItem("userId", uid);
        navigate("/dashboard");
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Authentication failed.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        localStorage.setItem("userId", user.uid);
      } else {
        localStorage.removeItem("userId");
      }
    });
    return () => unsubscribe();
  }, []);

  return (
    <div className="dark relative min-h-screen w-full overflow-hidden bg-background text-foreground">
      {/* Ambient mesh + grid */}
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.45]"
        style={{
          background:
            "radial-gradient(ellipse 80% 50% at 50% -20%, rgba(56, 189, 248, 0.25), transparent), radial-gradient(ellipse 60% 40% at 100% 0%, rgba(139, 92, 246, 0.18), transparent), radial-gradient(ellipse 50% 30% at 0% 100%, rgba(34, 211, 238, 0.12), transparent)",
        }}
      />
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.35]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }}
      />

      <div className="relative z-10 flex min-h-screen flex-col lg:flex-row">
        {/* Brand column */}
        <aside className="relative flex flex-1 flex-col justify-between border-b border-border/60 px-8 py-10 lg:max-w-[min(44%,520px)] lg:border-b-0 lg:border-r lg:px-12 lg:py-14">
          <div>
            <Link
              to="/"
              className="group inline-flex items-center gap-2 text-sm font-medium text-muted-foreground transition hover:text-foreground"
            >
              <ChevronLeft className="h-4 w-4 transition group-hover:-translate-x-0.5" aria-hidden />
              Back to home
            </Link>

            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
              className="mt-12 lg:mt-16"
            >
              <div className="inline-flex items-center gap-2 rounded-full border border-border/80 bg-muted/50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-primary">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
                Secure access
              </div>
              <h1 className="mt-6 max-w-md text-3xl font-semibold tracking-tight text-foreground md:text-4xl md:leading-[1.15]">
                Intelligence for modern{" "}
                <span className="bg-gradient-to-r from-sky-300 via-primary to-violet-400 bg-clip-text text-transparent">
                  financial operations
                </span>
              </h1>
              <p className="fi-body mt-4 max-w-sm">
                Sign in to sync your workspace, insights, and agent sessions across devices.
              </p>
            </motion.div>
          </div>

          <motion.ul
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.15, duration: 0.5 }}
            className="mt-12 hidden space-y-6 lg:mt-0 lg:block"
          >
            {brandFeatures.map(({ icon: Icon, title, copy }) => (
              <li
                key={title}
                className="flex gap-4 rounded-2xl border border-border/60 bg-card/30 p-4 backdrop-blur-sm transition hover:border-border hover:bg-card/50"
              >
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary/15 text-primary">
                  <Icon className="h-5 w-5" strokeWidth={1.5} aria-hidden />
                </div>
                <div>
                  <p className="text-sm font-medium text-foreground">{title}</p>
                  <p className="fi-caption mt-1">{copy}</p>
                </div>
              </li>
            ))}
          </motion.ul>

          <p className="fi-caption mt-8 hidden lg:block">
            By continuing you agree to our terms and privacy standards for regulated data handling.
          </p>
        </aside>

        {/* Form column */}
        <main className="flex flex-1 items-center justify-center px-4 py-12 sm:px-8 lg:py-0">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
            className="w-full max-w-[400px]"
          >
            <div className="mb-8 flex items-center justify-between gap-4 lg:hidden">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/20 text-primary">
                <Sparkles className="h-5 w-5" aria-hidden />
              </div>
            </div>

            <div className="rounded-3xl border border-border bg-card/90 p-8 shadow-xl backdrop-blur-xl sm:p-10">
              <div className="mb-8">
                <div className="mb-2 hidden items-center gap-2 lg:flex">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/15">
                    <Sparkles className="h-4 w-4 text-primary" aria-hidden />
                  </div>
                  <span className="text-sm font-semibold tracking-tight text-foreground">Quantastica</span>
                </div>
                <h2 className="text-2xl font-semibold tracking-tight text-foreground">
                  {isSignup ? "Create your account" : "Welcome back"}
                </h2>
                <p className="fi-body mt-2">
                  {isSignup
                    ? "Set up your profile to access the full platform."
                    : "Enter your credentials to open your workspace."}
                </p>
              </div>

              <AnimatePresence mode="wait">
                {error && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mb-6 overflow-hidden rounded-xl border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive"
                    role="alert"
                  >
                    {error}
                  </motion.div>
                )}
              </AnimatePresence>

              <form onSubmit={handleSubmit} className="space-y-5">
                {isSignup && (
                  <AuthField
                    icon={User}
                    label="Full name"
                    name="fullName"
                    autoComplete="name"
                    value={formData.fullName}
                    onChange={handleChange}
                  />
                )}

                <AuthField
                  icon={Mail}
                  label="Work email"
                  name="email"
                  type="email"
                  autoComplete={isSignup ? "email" : "username"}
                  value={formData.email}
                  onChange={handleChange}
                />

                {isSignup && (
                  <AuthField
                    icon={Phone}
                    label="Phone"
                    name="phone"
                    type="tel"
                    autoComplete="tel"
                    placeholder="+1 · · · · · · · · · ·"
                    value={formData.phone}
                    onChange={handleChange}
                  />
                )}

                <AuthField
                  icon={Lock}
                  label="Password"
                  name="password"
                  type="password"
                  autoComplete={isSignup ? "new-password" : "current-password"}
                  value={formData.password}
                  onChange={handleChange}
                />

                {isSignup && (
                  <AuthField
                    icon={Lock}
                    label="Confirm password"
                    name="confirmPassword"
                    type="password"
                    autoComplete="new-password"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                  />
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="group relative mt-2 flex w-full items-center justify-center gap-2 overflow-hidden rounded-xl bg-primary py-3.5 text-sm font-semibold text-primary-foreground shadow-md transition hover:opacity-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {loading ? (
                    <span className="inline-flex items-center gap-2">
                      <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                      Signing in…
                    </span>
                  ) : (
                    <>
                      {isSignup ? "Create account" : "Sign in"}
                      <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" aria-hidden />
                    </>
                  )}
                </button>
              </form>

              <div className="mt-8 border-t border-border pt-6 text-center text-sm text-muted-foreground">
                {isSignup ? "Already registered?" : "New to the platform?"}{" "}
                <button
                  type="button"
                  onClick={() => {
                    setIsSignup(!isSignup);
                    setError(null);
                  }}
                  className="font-semibold text-primary underline-offset-4 transition hover:underline"
                >
                  {isSignup ? "Sign in" : "Create an account"}
                </button>
              </div>
            </div>

            <p className="fi-caption mt-6 text-center lg:hidden">
              Protected sign-in. Quantastica encrypts credentials in transit.
            </p>
          </motion.div>
        </main>
      </div>
    </div>
  );
}

function AuthField({
  icon: Icon,
  label,
  name,
  value,
  onChange,
  type = "text",
  placeholder = "",
  autoComplete,
}: {
  icon: React.ComponentType<{ className?: string; strokeWidth?: number }>;
  label: string;
  name: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  type?: string;
  placeholder?: string;
  autoComplete?: string;
}) {
  return (
    <div className="space-y-2">
      <label htmlFor={name} className="fi-eyebrow block">
        {label}
      </label>
      <div className="relative">
        <Icon
          className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
          strokeWidth={1.5}
          aria-hidden
        />
        <input
          id={name}
          type={type}
          name={name}
          required
          autoComplete={autoComplete}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          className="fi-input py-3 pl-11 pr-4 text-sm"
        />
      </div>
    </div>
  );
}
