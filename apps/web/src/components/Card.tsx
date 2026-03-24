import type { ReactNode } from "react";
import { motion } from "framer-motion";

type CardProps = {
  children: ReactNode;
  className?: string;
  variant?: "default" | "gradient";
};

export function Card({ children, className = "", variant = "default" }: CardProps) {
  const base =
    "rounded-2xl border border-border bg-card p-5 text-card-foreground shadow-sm transition-shadow duration-300 hover:shadow-lg fi-glow";
  const gradient =
    variant === "gradient"
      ? "relative overflow-hidden bg-gradient-to-br from-primary/10 via-card to-card dark:from-primary/15 dark:via-card dark:to-background"
      : "";

  return (
    <motion.div
      whileHover={{ y: -2, transition: { duration: 0.2 } }}
      className={`${base} ${gradient} ${className}`.trim()}
    >
      {variant === "gradient" && (
        <div
          className="pointer-events-none absolute inset-0 opacity-40 dark:opacity-30"
          style={{
            background:
              "radial-gradient(ellipse 80% 60% at 100% 0%, hsl(var(--primary) / 0.25), transparent 55%)",
          }}
        />
      )}
      <div className="relative z-[1]">{children}</div>
    </motion.div>
  );
}
