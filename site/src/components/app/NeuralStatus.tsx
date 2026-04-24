"use client";

import { useBridge } from "@/contexts/BridgeContext";
import { Bell, Cpu, User } from "lucide-react";

export default function NeuralStatus() {
  const { auth, gameState, isReady } = useBridge();

  return (
    <div className="flex w-full flex-wrap items-center justify-between gap-4 border-t border-white/10 bg-black/20 px-6 py-4 backdrop-blur-xl">
      <div className="flex items-center gap-4">
        <div
          className={`h-2.5 w-2.5 rounded-full ${
            isReady ? "bg-toxic shadow-[0_0_14px_rgba(173,255,47,0.7)]" : "bg-red-500"
          }`}
        />
        <div>
          <div className="text-[10px] font-black uppercase tracking-[0.22em] text-white">
            {isReady ? "Coach online" : "Conexao interrompida"}
          </div>
          <div className="text-[11px] text-white/45">Sessao atual: {gameState.phase}</div>
        </div>
      </div>

      <div className="flex items-center gap-6">
        <div className="hidden items-center gap-2 text-white/55 md:flex">
          <Cpu className="h-4 w-4 text-violet-400" />
          <span className="text-[10px] font-mono uppercase tracking-[0.18em]">
            {gameState.phase}
          </span>
        </div>
        <div className="hidden items-center gap-2 text-white/55 md:flex">
          <Bell className="h-4 w-4 text-white/35" />
          <span className="text-[10px] font-mono uppercase tracking-[0.18em]">
            telemetria viva
          </span>
        </div>
        <div className="flex items-center gap-3 rounded-full border border-white/10 bg-white/[0.05] px-3 py-2">
          <div className="flex flex-col items-end">
            <span className="text-[11px] font-semibold text-white">
              {auth?.authenticated ? auth.user?.display_name : "Visitante"}
            </span>
            <span className="text-[10px] text-white/40">
              {gameState.summonerName || "aguardando invocador"}
            </span>
          </div>
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-indigo-700 text-white">
            <User className="h-4 w-4" />
          </div>
        </div>
      </div>
    </div>
  );
}
