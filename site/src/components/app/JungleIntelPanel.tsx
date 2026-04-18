"use client";

import { useBridge } from "@/contexts/BridgeContext";
import { motion, AnimatePresence } from "framer-motion";
import { Compass, Activity, Radar } from "lucide-react";

const STATIC_BLIPS = [...Array(3)].map(() => ({
  top: `${20 + Math.random() * 60}%`,
  left: `${20 + Math.random() * 60}%`
}));

export default function JungleIntelPanel() {
  const { jungleIntel: intel } = useBridge();

  const isEmpty = !intel || (!intel.enemy_jungler_name && !intel.enemy_jungler_champion);

  return (
    <div className="flex flex-col h-full bg-black/60 brutalist-border overflow-hidden relative group">
      {/* HUD Background Decoration */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden opacity-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-toxic/20 via-transparent to-transparent" />
        <div className="absolute inset-0" style={{ backgroundImage: 'linear-gradient(0deg, transparent 24%, rgba(34, 197, 94, 0.05) 25%, rgba(34, 197, 94, 0.05) 26%, transparent 27%, transparent 74%, rgba(34, 197, 94, 0.05) 75%, rgba(34, 197, 94, 0.05) 76%, transparent 77%, transparent), linear-gradient(90deg, transparent 24%, rgba(34, 197, 94, 0.05) 25%, rgba(34, 197, 94, 0.05) 26%, transparent 27%, transparent 74%, rgba(34, 197, 94, 0.05) 75%, rgba(34, 197, 94, 0.05) 76%, transparent 77%, transparent)', backgroundSize: '40px 40px' }} />
      </div>

      <div className="px-4 py-2 border-b border-border bg-black/80 flex justify-between items-center relative z-10">
        <div className="flex items-center gap-2">
          <Radar className="w-3 h-3 text-toxic animate-pulse" />
          <span className="text-[10px] font-black tracking-widest uppercase opacity-70">
            JUNGLE_TRACKER_V4
          </span>
        </div>
        {!isEmpty && (
          <div className="flex items-center gap-3">
            <div className="flex flex-col items-end">
               <span className="text-[8px] uppercase opacity-40 leading-none">Confiança</span>
               <span className={`text-[10px] font-mono font-bold ${intel.confidence > 0.7 ? "text-toxic" : "text-amber-500"}`}>
                {Math.round(intel.confidence * 100)}%
              </span>
            </div>
            <div className="h-6 w-[2px] bg-border" />
            <Activity className="w-3 h-3 text-toxic/50" />
          </div>
        )}
      </div>

      <div className="flex-1 relative overflow-hidden">
        <AnimatePresence mode="wait">
          {isEmpty ? (
            <motion.div 
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 flex flex-col items-center justify-center p-8 text-center"
            >
              {/* Animated Scanner Radar */}
              <div className="relative w-32 h-32 mb-6">
                <motion.div 
                  animate={{ rotate: 360 }}
                  transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                  className="absolute inset-0 rounded-full border border-toxic/20"
                >
                  <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1px] h-1/2 bg-gradient-to-t from-toxic to-transparent origin-bottom" />
                </motion.div>
                <div className="absolute inset-4 rounded-full border border-toxic/10 border-dashed" />
                <div className="absolute inset-8 rounded-full border border-toxic/5" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <Compass className="w-8 h-8 text-toxic/40 animate-pulse" />
                </div>
                
                {/* Random Blips */}
                {STATIC_BLIPS.map((blip, i) => (
                  <motion.div
                    key={i}
                    animate={{ 
                      opacity: [0, 1, 0],
                      scale: [0.5, 1.5, 0.5]
                    }}
                    transition={{ 
                      duration: 2, 
                      repeat: Infinity, 
                      delay: i * 0.7,
                      ease: "easeInOut" 
                    }}
                    className="absolute w-1 h-1 bg-toxic rounded-full shadow-[0_0_8px_rgba(34,197,94,0.8)]"
                    style={{ 
                      top: blip.top, 
                      left: blip.left 
                    }}
                  />
                ))}
              </div>

              <div className="space-y-1">
                <p className="text-[11px] font-black font-mono uppercase tracking-[0.2em] text-white/90">
                  Sincronizando Telemetria
                </p>
                <div className="flex items-center justify-center gap-1">
                  <span className="w-1 h-1 bg-toxic animate-bounce" style={{ animationDelay: '0s' }} />
                  <span className="w-1 h-1 bg-toxic animate-bounce" style={{ animationDelay: '0.2s' }} />
                  <span className="w-1 h-1 bg-toxic animate-bounce" style={{ animationDelay: '0.4s' }} />
                </div>
                <p className="text-[9px] font-mono uppercase opacity-30 mt-4 max-w-[200px] leading-relaxed">
                  Aguardando eventos de selva para iniciar rastreamento neural...
                </p>
              </div>
            </motion.div>
          ) : (
            <motion.div 
              key="content"
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              className="h-full flex flex-col p-4 space-y-4 overflow-y-auto scrollbar-hide bg-black/20"
            >
              {/* Jungler Info HUD */}
              <div className="grid grid-cols-2 gap-2">
                <div className="relative p-3 bg-white/5 border border-border group/card overflow-hidden">
                  <div className="absolute top-0 left-0 w-1 h-full bg-toxic/50 scale-y-0 group-hover/card:scale-y-100 transition-transform duration-300" />
                  <span className="text-[8px] font-black uppercase opacity-40 block mb-1 tracking-tighter">Inimigo_HVD</span>
                  <span className="text-sm font-black text-white block truncate tracking-tight">
                    {intel.enemy_jungler_champion?.toUpperCase() || "DESCONHECIDO"}
                  </span>
                </div>
                <div className="relative p-3 bg-white/5 border border-border group/card overflow-hidden">
                  <div className="absolute top-0 right-0 w-1 h-full bg-toxic/50 scale-y-0 group-hover/card:scale-y-100 transition-transform duration-300" />
                  <span className="text-[8px] font-black uppercase opacity-40 block mb-1 tracking-tighter">Lado_Provável</span>
                  <span className="text-sm font-black text-toxic block tracking-tight animate-pulse-slow">
                    {intel.probable_side?.toUpperCase() || "OFFLINE"}
                  </span>
                </div>
              </div>

              {/* Objectives Grid */}
              <div className="grid grid-cols-4 gap-1">
                {Object.entries(intel.objective_presence).map(([obj, val]) => (
                  <div key={obj} className="flex flex-col items-center p-2 bg-black/40 border border-border/50 hover:border-toxic/30 transition-colors">
                    <span className="text-[7px] font-black opacity-30 uppercase tracking-widest">{obj}</span>
                    <span className={`text-xs font-bold ${val > 0 ? "text-white" : "text-white/20"}`}>{val}</span>
                  </div>
                ))}
              </div>

              {/* Intelligence Stream */}
              <div className="space-y-2 flex-1 pt-2 border-t border-border/30">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-[9px] font-black uppercase opacity-40 tracking-widest flex items-center gap-1">
                    <Activity className="w-2 h-2" /> Live_Intel_Stream
                  </span>
                  <div className="flex gap-1">
                    <div className="w-1 h-1 rounded-full bg-toxic animate-ping" />
                    <div className="w-1 h-1 rounded-full bg-toxic/20" />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <AnimatePresence initial={false}>
                    {intel.notes.slice(0, 4).map((note, idx) => (
                      <motion.div 
                        key={`${note.clock}-${idx}`}
                        initial={{ opacity: 0, x: -10, height: 0 }}
                        animate={{ opacity: 1, x: 0, height: 'auto' }}
                        className="relative p-2 bg-white/[0.03] border-l-2 border-toxic/40 group/note overflow-hidden"
                      >
                        <div className="absolute inset-0 bg-gradient-to-r from-toxic/5 to-transparent translate-x-[-100%] group-hover/note:translate-x-0 transition-transform duration-500" />
                        <div className="flex justify-between items-start mb-1 relative z-10">
                          <span className="text-[10px] font-black text-toxic/90 uppercase">{note.title}</span>
                          <span className="text-[9px] font-mono opacity-30">[{note.clock}]</span>
                        </div>
                        <p className="text-[11px] text-zinc-400 leading-tight relative z-10 font-medium">{note.detail}</p>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                  
                  {intel.notes.length === 0 && (
                    <motion.div 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="h-24 flex items-center justify-center border border-dashed border-border/30 rounded"
                    >
                      <p className="text-[10px] opacity-20 italic font-mono uppercase tracking-tighter">Aguardando rastro...</p>
                    </motion.div>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Footer Status Bar */}
      <div className="px-3 py-1 bg-toxic/5 border-t border-toxic/10 flex justify-between items-center relative z-10">
        <span className="text-[7px] font-mono uppercase opacity-30 text-toxic">Neural_Engine_Active</span>
        <div className="flex gap-[2px]">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="w-[3px] h-[3px] bg-toxic opacity-20 animate-pulse" style={{ animationDelay: `${i * 0.1}s` }} />
          ))}
        </div>
      </div>
    </div>
  );
}
