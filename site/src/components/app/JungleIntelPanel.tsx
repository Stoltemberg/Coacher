"use client";

import { useBridge } from "@/contexts/BridgeContext";
import { motion } from "framer-motion";
import { Compass, ShieldAlert, Target, Zap } from "lucide-react";

export default function JungleIntelPanel() {
  const { jungleIntel: intel } = useBridge();

  if (!intel || (!intel.enemy_jungler_name && !intel.enemy_jungler_champion)) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-8 text-center bg-black/40 brutalist-border opacity-40">
        <Compass className="w-12 h-12 mb-4 animate-spin-slow" />
        <p className="text-xs font-mono uppercase tracking-widest">
          Sincronizando rastreamento de selva...
        </p>
      </div>
    );
  }

  const confidenceColor = intel.confidence > 0.7 ? "text-toxic" : intel.confidence > 0.4 ? "text-amber-500" : "text-red-500";

  return (
    <div className="flex flex-col h-full bg-black/40 brutalist-border overflow-hidden">
      <div className="px-4 py-2 border-b border-border bg-black/60 flex justify-between items-center">
        <span className="text-[10px] font-black tracking-widest uppercase opacity-50">
          JUNGLE_INTEL_STREAM
        </span>
        <span className={`text-[10px] font-mono ${confidenceColor}`}>
          CONFIANÇA: {Math.round(intel.confidence * 100)}%
        </span>
      </div>

      <div className="p-4 space-y-4 overflow-y-auto scrollbar-hide">
        {/* Jungler Info */}
        <div className="grid grid-cols-2 gap-2">
          <div className="p-3 bg-white/5 border border-border">
            <span className="text-[9px] uppercase opacity-40 block mb-1">Inimigo</span>
            <span className="text-sm font-black text-white block truncate">
              {intel.enemy_jungler_champion?.toUpperCase() || "DESCONHECIDO"}
            </span>
          </div>
          <div className="p-3 bg-white/5 border border-border">
            <span className="text-[9px] uppercase opacity-40 block mb-1">Lado Provável</span>
            <span className="text-sm font-black text-toxic block">
              {intel.probable_side?.toUpperCase() || "OFFLINE"}
            </span>
          </div>
        </div>

        {/* Objectives */}
        <div className="grid grid-cols-4 gap-1">
          {Object.entries(intel.objective_presence).map(([obj, val]) => (
            <div key={obj} className="flex flex-col items-center p-2 bg-white/5 border border-border">
              <span className="text-[8px] opacity-40 uppercase">{obj}</span>
              <span className="text-xs font-bold text-white">{val}</span>
            </div>
          ))}
        </div>

        {/* Notes */}
        <div className="space-y-2">
          <span className="text-[9px] uppercase opacity-40 block">Leituras Recentes</span>
          {intel.notes.slice(0, 3).map((note, idx) => (
            <motion.div 
              key={idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-2 bg-white/5 border-l-2 border-violet-500 text-[11px] leading-tight"
            >
              <div className="flex justify-between mb-1">
                <span className="font-bold text-violet-300 uppercase">{note.title}</span>
                <span className="opacity-40">{note.clock}</span>
              </div>
              <p className="text-muted-foreground">{note.detail}</p>
            </motion.div>
          ))}
          {intel.notes.length === 0 && (
            <p className="text-[10px] opacity-20 italic">Aguardando rastro do jungler...</p>
          )}
        </div>
      </div>
    </div>
  );
}
