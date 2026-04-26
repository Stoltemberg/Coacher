"use client";

import { useBridge } from "@/contexts/BridgeContext";
import { Activity, Bell, Cpu, Sparkles, User } from "lucide-react";

interface NeuralStatusProps {
  mode?: "expanded" | "compact";
}

export default function NeuralStatus({ mode = "expanded" }: NeuralStatusProps) {
  const { auth, gameState, isReady, settings } = useBridge();

  if (mode === "compact") {
    return (
      <div className="flex h-full flex-col justify-between p-5">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <div
              className={`h-2.5 w-2.5 rounded-full ${
                isReady ? "bg-toxic shadow-[0_0_14px_rgba(173,255,47,0.7)]" : "bg-red-500"
              }`}
            />
            <div className="text-[10px] font-black uppercase tracking-[0.2em] text-white/88">
              {isReady ? "Coach online" : "Conexao interrompida"}
            </div>
          </div>
          <div className="text-[11px] leading-6 text-white/48">
            Sessao atual em <span className="text-white/82">{gameState.phase}</span>.
          </div>
        </div>

        <div className="grid gap-2 sm:grid-cols-2">
          <div className="rounded-2xl border border-white/8 bg-white/[0.03] px-3 py-3">
            <div className="text-[9px] font-mono uppercase tracking-[0.16em] text-white/35">perfil</div>
            <div className="mt-1 text-[11px] font-semibold text-white">
              {auth?.authenticated ? auth.user?.display_name : "Visitante"}
            </div>
          </div>
          <div className="rounded-2xl border border-white/8 bg-white/[0.03] px-3 py-3">
            <div className="text-[9px] font-mono uppercase tracking-[0.16em] text-white/35">voz</div>
            <div className="mt-1 text-[11px] font-semibold text-white">
              {settings?.voice_personality === "minerva" ? "Minerva" : "Padrao"}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full min-h-0 flex-col justify-between px-6 pb-6 pt-2">
      <div className="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-4">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5 text-[9px] font-mono uppercase tracking-[0.18em] text-white/52">
            <Sparkles className="h-3.5 w-3.5 text-toxic" />
            cockpit central
          </div>
          <div>
            <div className="text-[10px] font-mono uppercase tracking-[0.2em] text-toxic/78">core loop</div>
            <h3 className="mt-3 max-w-2xl text-[34px] font-semibold leading-[1.05] tracking-[-0.06em] text-white">
              Estado vivo da partida com leitura limpa, sem overlay brigando por viewport.
            </h3>
            <p className="mt-3 max-w-xl text-[12px] leading-7 text-white/46">
              Fase atual, identidade da sessao e status do coach ficam no centro. Match intel, selva e memoria saem
              para paineis dedicados, sem esmagar a visao principal.
            </p>
          </div>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
          <div className="rounded-[24px] border border-white/10 bg-black/20 px-4 py-4">
            <div className="flex items-center gap-2 text-[9px] font-mono uppercase tracking-[0.16em] text-white/35">
              <Activity className={`h-3.5 w-3.5 ${isReady ? "text-toxic" : "text-red-400"}`} />
              sessao
            </div>
            <div className="mt-3 text-lg font-semibold text-white">{gameState.phase}</div>
            <div className="mt-1 text-[11px] text-white/45">
              {gameState.championName || "Aguardando campeao"}
            </div>
          </div>
          <div className="rounded-[24px] border border-white/10 bg-black/20 px-4 py-4">
            <div className="flex items-center gap-2 text-[9px] font-mono uppercase tracking-[0.16em] text-white/35">
              <Cpu className="h-3.5 w-3.5 text-violet-400" />
              runtime
            </div>
            <div className="mt-3 text-lg font-semibold text-white">
              {isReady ? "Bridge online" : "Bridge aguardando"}
            </div>
            <div className="mt-1 text-[11px] text-white/45">
              {settings?.voice_personality === "minerva" ? "voz minerva ativa" : "voz padrao ativa"}
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 grid gap-3 xl:grid-cols-[0.9fr_0.9fr_1.2fr]">
        <div className="rounded-[24px] border border-white/10 bg-white/[0.04] px-4 py-4">
          <div className="flex items-center gap-2 text-[9px] font-mono uppercase tracking-[0.16em] text-white/35">
            <Bell className="h-3.5 w-3.5 text-white/35" />
            telemetria
          </div>
          <div className="mt-3 text-sm font-semibold text-white">
            {isReady ? "Fluxo ao vivo" : "Sincronizacao pendente"}
          </div>
          <div className="mt-1 text-[11px] leading-6 text-white/45">
            O coach usa estado local, draft, live client e memoria para manter o loop decisorio vivo.
          </div>
        </div>

        <div className="rounded-[24px] border border-white/10 bg-white/[0.04] px-4 py-4">
          <div className="flex items-center gap-2 text-[9px] font-mono uppercase tracking-[0.16em] text-white/35">
            <User className="h-3.5 w-3.5 text-white/35" />
            operador
          </div>
          <div className="mt-3 text-sm font-semibold text-white">
            {auth?.authenticated ? auth.user?.display_name : "Visitante"}
          </div>
          <div className="mt-1 text-[11px] leading-6 text-white/45">
            {gameState.summonerName || "Aguardando invocador"}
          </div>
        </div>

        <div className="rounded-[24px] border border-toxic/10 bg-toxic/[0.05] px-4 py-4">
          <div className="text-[9px] font-mono uppercase tracking-[0.16em] text-toxic/75">prioridade do coach</div>
          <div className="mt-3 text-sm font-semibold text-white">
            {isReady
              ? "Separar leitura principal de suporte lateral para evitar interface esmagada."
              : "Esperando bridge e cliente para preencher a sessao."}
          </div>
          <div className="mt-1 text-[11px] leading-6 text-white/45">
            O viewport principal fica dedicado ao estado da partida; informacao secundaria vive em paineis proprios.
          </div>
        </div>
      </div>
    </div>
  );
}
