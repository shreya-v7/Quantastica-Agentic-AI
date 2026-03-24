import { lazy, Suspense } from "react";
import { motion } from "framer-motion";

const ChatInterface = lazy(() => import("../../components/ChatInterface"));

export default function ChatPage() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="mx-auto flex h-[calc(100vh-7.5rem)] min-h-[480px] max-w-5xl flex-col"
    >
      <div className="mb-4 shrink-0">
        <p className="text-sm font-medium text-muted-foreground">Assistant</p>
        <h1 className="text-2xl font-semibold tracking-tight">Chat</h1>
      </div>
      <div className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-sm">
        <Suspense
          fallback={
            <div className="flex h-full min-h-[320px] items-center justify-center p-8">
              <div className="h-full w-full max-w-md space-y-3">
                <div className="h-10 rounded-xl fi-shimmer" />
                <div className="h-24 rounded-2xl fi-shimmer" />
                <div className="h-24 rounded-2xl fi-shimmer" />
              </div>
            </div>
          }
        >
          <ChatInterface />
        </Suspense>
      </div>
    </motion.div>
  );
}
