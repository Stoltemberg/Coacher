"use client";

import { useState } from "react";
import { AnimatePresence, motion, Variants } from "framer-motion";
import {
  Activity,
  Database,
  LayoutDashboard,
  Logs,
  ShieldCheck,
  Settings,
  Target,
  Terminal,
  X,
} from "lucide-react";

import { useBridge } from "@/contexts/BridgeContext";

import ChampionBackground from "./ChampionBackground";
import JungleIntelPanel from "./JungleIntelPanel";
import MatchIntelPanel from "./MatchIntelPanel";
import MemoryFeed from "./MemoryFeed";
import NeuralLogChannel from "./NeuralLogChannel";
import NeuralStatus from "./NeuralStatus";
import SettingsPanel from "./SettingsPanel";
import { HudPanel } from "./HudPanel";
import StatusBar from "../layout/StatusBar";

const sidebarVariants: Variants = {
  hidden: { opacity: 0, x: -20 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { staggerChildren: 0.05, delayChildren: 0.1 },
  },
};

export default function AppDashboard() {
  const { auth, gameState, logs } = useBridge();
  const [activeTab, setActiveTab] = useState<"dashboard" | "settings">("dashboard");
  const [logsOpen, setLogsOpen] = useState(false);
  const isChampSelect = /sele/i.test(gameState.phase) && /campe/i.test(gameState.phase);

  const navItems = [
    { id: "dashboard", icon: LayoutDashboard, label: "Painel", desc: "workspace da partida" },
    { id: "settings", icon: Settings, label: "Configuracoes", desc: "ajustes do coach" },
  ];

  return (
    <div className="app-shell bg-[#050508] text-white selection:bg-toxic/30">
      <div className="app-backdrop" />
      <StatusBar />

      <div className="relative z-10 flex flex-1 overflow-hidden">
        <motion.aside
          initial="hidden"
          animate="visible"
          variants={sidebarVariants}
          className="m-4 mr-0 flex w-[290px] flex-col rounded-[30px] border border-white/8 bg-[rgba(13,15,20,0.82)] backdrop-blur-2xl"
        >
          <div className="flex-1 space-y-6 p-5 pt-6">
            <div className="app-surface rounded-[26px] px-4 py-4">
              <div className="mb-3 text-[10px] font-mono uppercase tracking-[0.18em] text-white/45">
                Sessao atual
              </div>
              <div className="text-lg font-semibold text-white">
                {auth?.authenticated ? auth.user?.display_name || "Conta ativa" : "Visitante"}
              </div>
              <div className="mt-1 text-[11px] leading-6 text-white/45">
                {gameState.summonerName || "Aguardando nome do invocador"}
              </div>
            </div>

            <nav className="space-y-4">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id as "dashboard" | "settings")}
                  className={`relative w-full overflow-hidden rounded-[26px] border p-4 text-left transition-all ${
                    activeTab === item.id
                      ? "border-white/15 bg-white/[0.08] text-white"
                      : "border-white/8 bg-white/[0.03] text-white/55 hover:bg-white/[0.06]"
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <item.icon
                      className={`h-4 w-4 ${activeTab === item.id ? "text-toxic" : "text-white/40"}`}
                    />
                    <div>
                      <p className="text-[11px] font-semibold">{item.label}</p>
                      <p className="text-[10px] text-white/40">{item.desc}</p>
                    </div>
                  </div>
                  {activeTab === item.id && (
                    <div className="absolute inset-y-3 left-0 w-1 rounded-r-full bg-toxic shadow-[0_0_15px_hsl(var(--toxic))]" />
                  )}
                </button>
              ))}
            </nav>
          </div>

          <div className="soft-divider bg-black/10 p-5">
            <div className="flex items-center gap-3">
              <div className="h-2 w-2 animate-pulse rounded-full bg-toxic shadow-[0_0_12px_rgba(173,255,47,0.7)]" />
              <span className="text-[10px] font-mono uppercase tracking-[0.18em] text-white/55">
                Bridge sincronizada
              </span>
            </div>
          </div>
        </motion.aside>

        <main className="flex min-w-0 flex-1 flex-col overflow-hidden px-4 pb-4 pt-0">
          <AnimatePresence mode="wait">
            {activeTab === "dashboard" ? (
              <motion.div
                key="dashboard"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-1 flex-col gap-4 overflow-hidden py-4"
              >
                {isChampSelect ? (
                  <div className="grid min-h-0 flex-1 grid-cols-12 gap-4">
                    <div className="col-span-12 flex min-h-0 flex-col gap-4 xl:col-span-8">
                      <div className="min-h-0 flex-[1.2]">
                        <HudPanel title="Modo tatico" icon={ShieldCheck} idSuffix="DRFT" className="h-full">
                          <div className="relative flex h-full min-h-0 flex-col overflow-hidden bg-[#050508]">
                            <ChampionBackground championName={gameState.championName} />
                            <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(173,255,47,0.12),_transparent_26%),linear-gradient(145deg,_rgba(5,5,8,0.35)_0%,_rgba(5,5,8,0.88)_72%)]" />

                            <div className="relative z-10 flex items-center justify-between gap-4 px-5 py-4">
                              <div className="max-w-xl">
                                <div className="text-[10px] font-mono uppercase tracking-[0.2em] text-toxic/80">
                                  Selecao de Campeoes
                                </div>
                                <h2 className="mt-2 text-2xl font-semibold tracking-[-0.05em] text-white">
                                  Prioridade total para leitura do draft e picks recomendados.
                                </h2>
                                <p className="mt-2 text-[11px] leading-6 text-white/50">
                                  O intel inimigo sobe para o centro da tela enquanto o restante do dashboard vira apoio tatico.
                                </p>
                              </div>
                              <div className="hidden rounded-[24px] border border-white/10 bg-black/20 px-4 py-3 text-right xl:block">
                                <div className="text-[9px] font-mono uppercase tracking-[0.16em] text-white/35">
                                  fase atual
                                </div>
                                <div className="mt-2 text-sm font-semibold text-white">{gameState.phase}</div>
                                <div className="mt-1 text-[10px] text-white/45">
                                  {gameState.championName || "Campeao ainda nao travado"}
                                </div>
                              </div>
                            </div>

                            <div className="relative z-10 min-h-0 flex-1 px-5 pb-5">
                              <MatchIntelPanel tacticalMode />
                            </div>
                          </div>
                        </HudPanel>
                      </div>

                      <div className="min-h-0 flex-[0.8]">
                        <HudPanel title="Estado da partida" icon={Activity} idSuffix="CORE" className="h-full">
                          <NeuralStatus />
                        </HudPanel>
                      </div>
                    </div>

                    <div className="col-span-12 flex min-h-0 flex-col gap-4 xl:col-span-4">
                      <div className="min-h-0 flex-1">
                        <HudPanel title="Leitura de selva" icon={Target} idSuffix="TAC" className="h-full">
                          <JungleIntelPanel />
                        </HudPanel>
                      </div>
                      <div className="min-h-0 flex-1">
                        <HudPanel title="Memoria da sessao" icon={Database} idSuffix="MEM" className="h-full">
                          <MemoryFeed />
                        </HudPanel>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="grid min-h-0 flex-1 grid-cols-12 gap-4">
                    <div className="col-span-12 flex h-full min-h-0 flex-col gap-4 xl:col-span-8">
                      <div className="min-h-0 flex-1">
                        <HudPanel title="Visao da partida" icon={Activity} idSuffix="CORE" className="h-full">
                          <div className="relative h-full w-full overflow-hidden bg-[#050508]">
                            <ChampionBackground championName={gameState.championName} />
                            <div className="pointer-events-none absolute inset-0 z-10 bg-[radial-gradient(circle_at_top_left,_rgba(255,255,255,0.08),_transparent_30%),linear-gradient(180deg,_rgba(5,5,8,0.05)_0%,_rgba(5,5,8,0.65)_100%)]" />

                            <div className="absolute right-5 top-5 z-20 w-[320px] max-w-[calc(100%-2.5rem)]">
                              <MatchIntelPanel />
                            </div>

                            <div className="absolute bottom-0 left-0 right-0 z-30">
                              <NeuralStatus />
                            </div>
                          </div>
                        </HudPanel>
                      </div>
                    </div>

                    <div className="col-span-12 flex min-h-0 flex-col gap-4 xl:col-span-4">
                      <div className="min-h-0 flex-1">
                        <HudPanel title="Memoria da sessao" icon={Database} idSuffix="MEM" className="h-full">
                          <MemoryFeed />
                        </HudPanel>
                      </div>
                      <div className="min-h-0 flex-1">
                        <HudPanel title="Leitura de selva" icon={Target} idSuffix="TAC" className="h-full">
                          <JungleIntelPanel />
                        </HudPanel>
                      </div>
                    </div>
                  </div>
                )}

                <button
                  type="button"
                  onClick={() => setLogsOpen(true)}
                  className="h-[220px] shrink-0 rounded-[28px] text-left transition-transform duration-200 hover:-translate-y-0.5"
                >
                  <HudPanel title="Message log" icon={Terminal} idSuffix="LOG" className="h-full">
                    <div className="flex h-full flex-col">
                      <div className="soft-divider flex items-center justify-between px-4 py-3">
                        <div className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-[0.18em] text-white/45">
                          <Logs className="h-3.5 w-3.5 text-toxic" />
                          clique para abrir todos os logs
                        </div>
                        <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-[9px] font-mono uppercase tracking-[0.16em] text-white/45">
                          {logs.length} eventos
                        </span>
                      </div>
                      <NeuralLogChannel limit={6} compact />
                    </div>
                  </HudPanel>
                </button>
              </motion.div>
            ) : (
              <motion.div
                key="settings"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="flex-1 overflow-hidden"
              >
                <SettingsPanel />
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </div>

      <AnimatePresence>
        {logsOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 z-[300] flex items-center justify-center bg-black/70 p-6 backdrop-blur-sm"
          >
            <motion.div
              initial={{ opacity: 0, y: 18, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 18, scale: 0.98 }}
              className="app-surface flex h-[80vh] w-full max-w-5xl flex-col overflow-hidden rounded-[32px]"
            >
              <div className="soft-divider flex items-center justify-between px-6 py-5">
                <div>
                  <div className="text-[10px] font-mono uppercase tracking-[0.2em] text-white/45">
                    historico completo
                  </div>
                  <div className="mt-1 text-2xl font-semibold tracking-[-0.05em] text-white">
                    Message log
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setLogsOpen(false)}
                  className="flex h-11 w-11 items-center justify-center rounded-full border border-white/10 bg-white/[0.04] text-white/65 transition-colors hover:bg-white hover:text-black"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
              <NeuralLogChannel />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
