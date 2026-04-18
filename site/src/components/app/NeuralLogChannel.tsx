"use client";

import { useBridge } from "@/contexts/BridgeContext";
import { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function NeuralLogChannel() {
  const { logs } = useBridge();
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  const getToneClass = (type: string) => {
    switch (type) {
      case "urgent": return "text-red-500 border-l-red-500";
      case "warning": return "text-amber-500 border-l-amber-500";
      case "success": return "text-toxic border-l-toxic";
      case "system": return "text-violet-400 border-l-violet-400 font-bold";
      default: return "text-muted-foreground border-l-border";
    }
  };

  return (
    <div className="flex flex-col h-full bg-black/40 brutalist-border overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-black/60">
        <span className="text-[10px] font-black tracking-widest uppercase opacity-50">
          NEURAL_LOG_CHANNEL
        </span>
        <div className="flex gap-1">
          <div className="w-1.5 h-1.5 rounded-full bg-toxic animate-pulse" />
          <div className="w-1.5 h-1.5 rounded-full bg-toxic/40" />
        </div>
      </div>
      
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 space-y-2 scrollbar-hide font-mono text-xs"
      >
        <AnimatePresence initial={false}>
          {logs.map((log) => (
            <motion.div
              key={log.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className={`pl-3 border-l-2 py-1 leading-relaxed ${getToneClass(log.type)}`}
            >
              <span className="opacity-40 mr-2">[{new Date(log.id).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}]</span>
              {log.message}
            </motion.div>
          ))}
        </AnimatePresence>
        
        {logs.length === 0 && (
          <div className="h-full flex items-center justify-center opacity-20 italic">
            Aguardando sinal neural...
          </div>
        )}
      </div>
    </div>
  );
}
