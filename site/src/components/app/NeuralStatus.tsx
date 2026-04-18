"use client";

import { useBridge } from "@/contexts/BridgeContext";
import { motion } from "framer-motion";
import { Activity, Bell, Cpu, User } from "lucide-react";

export default function NeuralStatus() {
  const { gameState, auth, isReady } = useBridge();

  return (
    <div className="flex items-center justify-between w-full h-16 border-b border-border bg-black/40 px-6 backdrop-blur-md">
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-3">
          <div className={`w-2 h-2 rounded-full ${isReady ? 'bg-toxic animate-pulse' : 'bg-red-500'}`} />
          <span className="text-[10px] font-black tracking-[0.2em] uppercase">
            {isReady ? 'SYSTEM_ONLINE' : 'LINK_TERMINATED'}
          </span>
        </div>
        
        <div className="h-4 w-[1px] bg-border" />

        <div className="flex items-center gap-2">
          <Cpu className="w-3 h-3 text-violet-400" />
          <span className="text-[10px] font-mono opacity-60 uppercase">
            {gameState.phase}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-8">
        <div className="hidden md:flex flex-col items-end">
          <span className="text-[10px] opacity-40 uppercase font-mono tracking-widest">Invoke_Summoner</span>
          <span className="text-sm font-black text-white">{gameState.summonerName || 'AGUARDANDO...'}</span>
        </div>

        <div className="flex items-center gap-4">
          <div className="p-2 transition-colors hover:bg-white/5 cursor-pointer rounded-sm border border-transparent hover:border-border">
            <Bell className="w-4 h-4 text-muted-foreground" />
          </div>
          
          <div className="flex items-center gap-3 pl-4 border-l border-border h-8">
            <div className="flex flex-col items-end mr-1">
              <span className="text-[10px] font-bold text-violet-300">
                {auth?.authenticated ? auth.user?.display_name : 'VISITANTE'}
              </span>
              <span className="text-[8px] opacity-40 uppercase">NEURAL_ID</span>
            </div>
            <div className="w-8 h-8 rounded-sm bg-gradient-to-br from-violet-600 to-indigo-900 border border-violet-400/30 flex items-center justify-center">
              <User className="w-4 h-4 text-white" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
