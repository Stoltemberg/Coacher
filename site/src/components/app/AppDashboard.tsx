"use client";

import { useBridge } from "@/contexts/BridgeContext";
import NeuralStatus from "./NeuralStatus";
import NeuralLogChannel from "./NeuralLogChannel";
import JungleIntelPanel from "./JungleIntelPanel";
import MemoryFeed from "./MemoryFeed";
import MatchIntelPanel from "./MatchIntelPanel";
import NeuralBrain from "../animations/NeuralBrain";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Settings, LayoutDashboard, BrainCircuit, Activity } from "lucide-react";
import SettingsPanel from "@/components/app/SettingsPanel";
import ChampionBackground from "./ChampionBackground";

export default function AppDashboard() {
  const [activeTab, setActiveTab] = useState<"dashboard" | "settings">("dashboard");
  const { isReady, gameState } = useBridge();

  const navItems = [
    { id: "dashboard", icon: LayoutDashboard, label: "COMM CENTER" },
    { id: "settings", icon: Settings, label: "NEURAL CONFIG" },
  ];

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden selection:bg-toxic/30 relative">
      <NeuralBrain />
      
      {/* Top Header */}
      <NeuralStatus />

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar Nav */}
        <aside className="w-16 border-r border-border bg-black/60 flex flex-col items-center py-8 gap-8 z-20">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id as any)}
              className={`group relative p-3 transition-all ${
                activeTab === item.id ? 'text-toxic bg-white/5' : 'text-muted-foreground hover:text-white'
              }`}
            >
              <item.icon className="w-5 h-5" />
              <span className="absolute left-16 px-2 py-1 bg-violet-600 text-white text-[8px] font-black uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-50">
                {item.label}
              </span>
              {activeTab === item.id && (
                <motion.div 
                  layoutId="activeNav"
                  className="absolute left-0 top-0 bottom-0 w-1 bg-toxic shadow-[0_0_10px_#adff2f]"
                />
              )}
            </button>
          ))}
          
          <div className="mt-auto flex flex-col items-center gap-4 opacity-40">
            <BrainCircuit className="w-4 h-4" />
            <Activity className="w-4 h-4" />
          </div>
        </aside>

        {/* Dynamic Content Area */}
        <main className="flex-1 relative z-10 overflow-hidden">
          <AnimatePresence mode="wait">
            {activeTab === "dashboard" ? (
              <motion.div
                key="dashboard"
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 1.02 }}
                className="h-full p-6 grid grid-cols-1 md:grid-cols-12 grid-rows-6 gap-6"
              >
                {/* Visual Engine (Center) */}
                <div className="md:col-span-8 row-span-4 bg-black/20 brutalist-border relative group overflow-hidden">
                  <ChampionBackground championName={gameState.championName} />
                   <div className="absolute top-4 left-4 flex flex-col gap-1">
                      <span className="text-[10px] font-black tracking-widest opacity-30 uppercase italic">NEURAL_ENGINE_V4.8</span>
                      <div className="flex gap-1">
                        {[1, 2, 3, 4, 5].map(i => <div key={i} className="w-1 h-3 bg-toxic/20" />)}
                      </div>
                   </div>
                   
                   {/* Match Intel Overlay */}
                   <div className="absolute top-20 left-4 w-64 z-20">
                      <MatchIntelPanel />
                   </div>

                   <div className="absolute inset-0 flex items-center justify-center p-20 pointer-events-none group-hover:scale-105 transition-transform duration-1000">
                      <div className="w-full h-full border-[0.5px] border-white/5 rounded-full animate-spin-slow flex items-center justify-center">
                         <div className="w-3/4 h-3/4 border-[0.5px] border-toxic/10 rounded-full animate-reverse-spin flex items-center justify-center">
                            <div className="w-1/2 h-1/2 border border-violet-500/20 rounded-full flex items-center justify-center">
                               <span className="text-4xl font-black text-white/5 tracking-tighter">COACHER.</span>
                            </div>
                         </div>
                      </div>
                   </div>

                   {/* Live Phase Text */}
                   <div className="absolute bottom-6 left-6">
                      <h2 className="text-5xl font-black italic tracking-tighter text-white/10 uppercase mb-1">
                        {gameState.phase.split(' ').join('_')}
                      </h2>
                      <p className="text-[10px] font-mono tracking-[0.5em] text-toxic/40">LINK_STABLE // NO_THREATS_DETECTED</p>
                   </div>
                </div>

                {/* Right Panel: Memory Feed */}
                <div className="md:col-span-4 row-span-4">
                  <MemoryFeed />
                </div>

                {/* Bottom Left: Logs */}
                <div className="md:col-span-7 row-span-2">
                  <NeuralLogChannel />
                </div>

                {/* Bottom Right: Jungle Intel */}
                <div className="md:col-span-5 row-span-2">
                  <JungleIntelPanel />
                </div>
              </motion.div>
            ) : (
              <motion.div
                key="settings"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="h-full"
              >
                <SettingsPanel />
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </div>

      {/* Decorative Corner Bits */}
      <div className="fixed top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-white/10 pointer-events-none" />
      <div className="fixed top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-white/10 pointer-events-none" />
      <div className="fixed bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-white/10 pointer-events-none" />
      <div className="fixed bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-white/10 pointer-events-none" />
    </div>
  );
}
