"use client";

import { useBridge } from "@/contexts/BridgeContext";
import { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface NeuralLogChannelProps {
  limit?: number;
  compact?: boolean;
}

export default function NeuralLogChannel({ limit, compact = false }: NeuralLogChannelProps) {
  const { logs } = useBridge();
  const scrollRef = useRef<HTMLDivElement>(null);
  const visibleLogs = typeof limit === "number" ? logs.slice(-limit) : logs;

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  const getToneClass = (type: string) => {
    switch (type) {
      case "urgent":
        return "text-red-300";
      case "warning":
        return "text-amber-300";
      case "success":
        return "text-toxic";
      case "system":
        return "text-violet-300";
      default:
        return "text-white/55";
    }
  };

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <div ref={scrollRef} className={`custom-scrollbar flex-1 space-y-2 overflow-y-auto ${compact ? "p-3 pb-4" : "p-4 pb-6"}`}>
        <AnimatePresence initial={false}>
          {visibleLogs.map((log) => (
            <motion.div
              key={log.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex items-start gap-3 rounded-2xl border border-white/8 bg-white/[0.03] ${compact ? "px-3 py-2.5" : "px-4 py-3"} ${getToneClass(log.type)}`}
            >
              <span className="mt-1 h-2.5 w-2.5 shrink-0 rounded-full bg-current opacity-80" />
              <div className="min-w-0 flex-1">
                <div className="mb-1 text-[9px] font-mono uppercase tracking-[0.16em] opacity-35">
                  {new Date(log.id).toLocaleTimeString([], {
                    hour12: false,
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit",
                  })}
                </div>
                <span className={`block text-white/82 ${compact ? "text-[10px] leading-5" : "text-[11px]"}`}>{log.message}</span>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {visibleLogs.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center gap-3 opacity-30">
            <div className="h-10 w-10 rounded-full border border-white/10 bg-white/[0.03]" />
            <span className="text-[11px] text-white/45">Sem eventos recentes por enquanto.</span>
          </div>
        )}
      </div>
    </div>
  );
}
