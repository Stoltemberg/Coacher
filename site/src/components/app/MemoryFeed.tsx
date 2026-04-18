"use client";

import { useBridge } from "@/contexts/BridgeContext";
import { motion, AnimatePresence } from "framer-motion";
import { Brain, History } from "lucide-react";

export default function MemoryFeed() {
  const { summary } = useBridge();
  const memories = summary?.memory || [];

  return (
    <div className="flex flex-col h-full bg-black/40 brutalist-border overflow-hidden">
      <div className="px-4 py-2 border-b border-border bg-black/60 flex justify-between items-center">
        <span className="text-[10px] font-black tracking-widest uppercase opacity-50">
          NEURAL_MEMORY_FEED
        </span>
        <Brain className="w-3 h-3 text-violet-400" />
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-hide">
        <AnimatePresence initial={false}>
          {memories.map((entry, idx) => (
            <motion.article
              key={idx}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="p-3 bg-white/5 border border-border group hover:border-violet-500/50 transition-colors"
            >
              <div className="flex items-start justify-between mb-1">
                <h4 className="text-[10px] font-black uppercase text-violet-300">
                  {entry.title}
                </h4>
                {entry.tone && (
                  <div className={`w-1.5 h-1.5 rounded-full ${
                    entry.tone === 'success' ? 'bg-toxic' : 
                    entry.tone === 'urgent' ? 'bg-red-500' : 
                    entry.tone === 'warning' ? 'bg-amber-500' : 'bg-white/20'
                  }`} />
                )}
              </div>
              <p className="text-xs text-muted-foreground leading-relaxed">
                {entry.note}
              </p>
              {entry.meta && (
                <span className="text-[9px] mt-2 block opacity-30 font-mono italic">
                  {entry.meta}
                </span>
              )}
            </motion.article>
          ))}
        </AnimatePresence>

        {memories.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center opacity-20 text-center space-y-3">
            <History className="w-8 h-8" />
            <p className="text-[10px] uppercase tracking-tighter">
              Nenhuma entrada de memória profunda detectada.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
