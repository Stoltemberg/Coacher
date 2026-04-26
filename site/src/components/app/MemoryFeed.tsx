"use client";

import { useBridge } from "@/contexts/BridgeContext";
import { motion, AnimatePresence } from "framer-motion";
import { Brain } from "lucide-react";

export default function MemoryFeed() {
  const { summary } = useBridge();
  const memories = summary?.memory || [];

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <div className="custom-scrollbar flex-1 space-y-3 overflow-y-auto p-4">
        <AnimatePresence initial={false}>
          {memories.map((entry, idx) => (
            <motion.article
              key={idx}
              initial={{ opacity: 0, y: 12, filter: "blur(4px)" }}
              animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
              transition={{ delay: idx * 0.05, type: "spring", stiffness: 200, damping: 20 }}
              className="group relative overflow-hidden rounded-2xl border border-white/8 bg-white/[0.04] p-4 transition-all hover:border-white/15 hover:bg-white/[0.06]"
            >
              <div
                className={`absolute bottom-0 left-0 top-0 w-[2px] opacity-50 transition-all duration-300 group-hover:opacity-100 ${
                  entry.tone === "success"
                    ? "bg-toxic"
                    : entry.tone === "urgent"
                      ? "bg-red-500"
                      : entry.tone === "warning"
                        ? "bg-amber-500"
                        : "bg-violet-500/30"
                }`}
              />
              <div className="absolute inset-0 bg-gradient-to-r from-white/[0.05] to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
              <div className="relative z-10 mb-1 flex items-start justify-between pl-2">
                <h4 className="text-[11px] font-semibold text-white">{entry.title}</h4>
                {entry.tone && (
                  <div
                    className={`mt-0.5 h-1.5 w-1.5 shrink-0 rounded-full ${
                      entry.tone === "success"
                        ? "bg-toxic animate-pulse-toxic"
                        : entry.tone === "urgent"
                          ? "bg-red-500 animate-pulse"
                          : entry.tone === "warning"
                            ? "bg-amber-500"
                            : "bg-white/20"
                    }`}
                  />
                )}
              </div>
              <p className="relative z-10 break-words pl-2 text-[11px] leading-relaxed text-white/58">{entry.note}</p>
              {entry.meta && (
                <span className="relative z-10 mt-2 block pl-2 text-[9px] font-mono uppercase tracking-[0.14em] text-white/30">
                  {entry.meta}
                </span>
              )}
            </motion.article>
          ))}
        </AnimatePresence>

        {memories.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center space-y-4 p-6">
            <div className="flex h-20 w-20 items-center justify-center rounded-full border border-white/10 bg-white/[0.03]">
              <Brain className="h-6 w-6 text-violet-300/45" />
            </div>
            <div className="text-center opacity-60">
              <p className="text-[11px] font-semibold text-white/80">Memoria vazia</p>
              <p className="mx-auto mt-2 max-w-[180px] text-[10px] leading-relaxed text-white/40">
                Nenhuma entrada detectada. Aguardando primeira partida.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
