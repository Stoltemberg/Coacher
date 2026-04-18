"use client";

import { useBridge } from "@/contexts/BridgeContext";
import { motion } from "framer-motion";
import { Users, Swords } from "lucide-react";

export default function MatchIntelPanel() {
  const { matchIntel } = useBridge();

  if (matchIntel.length === 0) return null;

  return (
    <div className="flex flex-col bg-black/40 brutalist-border overflow-hidden">
      <div className="px-4 py-2 border-b border-border bg-black/60 flex justify-between items-center">
        <span className="text-[10px] font-black tracking-widest uppercase opacity-50">
          ENEMY_TEAM_CORE_STATS
        </span>
        <Swords className="w-3 h-3 text-toxic" />
      </div>

      <div className="p-3 grid grid-cols-1 gap-2 overflow-y-auto scrollbar-hide">
        {matchIntel.map((player, idx) => (
          <motion.div
            key={player.name}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="flex items-center justify-between p-2 bg-white/5 border border-border/50 hover:border-toxic/30 transition-colors"
          >
            <div className="flex flex-col">
              <span className="text-[10px] font-black text-white truncate max-w-[120px]">
                {player.name.toUpperCase()}
              </span>
              <span className="text-[8px] font-mono text-muted-foreground">
                {player.champion.toUpperCase() || 'DESCONHECIDO'}
              </span>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="text-right">
                <span className="text-[8px] block opacity-40 uppercase">ELO</span>
                <span className="text-[10px] font-bold text-violet-300">{player.rank || '--'}</span>
              </div>
              <div className="text-right min-w-[40px]">
                <span className="text-[8px] block opacity-40 uppercase">WR</span>
                <span className="text-[10px] font-bold text-toxic">{player.winrate || '--'}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
