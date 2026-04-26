"use client";

import { useMemo, useState } from "react";
import { motion } from "framer-motion";

import { useBridge } from "@/contexts/BridgeContext";
import SettingsPanel from "./SettingsPanel";
import LeftSidebar from "./LeftSidebar";
import TopNavbar from "./TopNavbar";
import RightSidebar from "./RightSidebar";
import PhaseTabs from "./PhaseTabs";
import LiveCommandCenter from "./LiveCommandCenter";
import DraftWorkspace from "./DraftWorkspace";
import PostgameReview from "./PostgameReview";
import ProgressionDashboard from "./ProgressionDashboard";
import { classifyDashboardView, type DashboardView } from "./dashboard-phase";

export default function AppDashboard() {
  const { gameState, draftRecommendations, summary } = useBridge();

  const phaseDrivenView = useMemo(
    () =>
      classifyDashboardView({
        phase: gameState.phase,
        hasDraft: Boolean(draftRecommendations),
        hasSummary: Boolean(summary),
      }),
    [draftRecommendations, gameState.phase, summary],
  );

  const [activeView, setActiveView] = useState<DashboardView>(phaseDrivenView);
  const effectiveView =
    activeView === "settings" || activeView === "progress" ? activeView : phaseDrivenView;

  const centerView = (() => {
    switch (effectiveView) {
      case "draft":
        return <DraftWorkspace />;
      case "postgame":
        return <PostgameReview />;
      case "progress":
        return <ProgressionDashboard />;
      case "settings":
        return <SettingsPanel />;
      case "live":
      default:
        return <LiveCommandCenter />;
    }
  })();

  return (
    <div className="app-shell overflow-hidden bg-[#050508] p-4 font-sans text-white selection:bg-[#ADFF2F]/30">
      <motion.div
        className="flex flex-1 gap-4 overflow-hidden"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.35 }}
      >
        <motion.div
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ type: "spring", stiffness: 110, damping: 20 }}
          className="h-full"
        >
          <LeftSidebar activeTab={effectiveView} setActiveTab={(tab) => setActiveView(tab as DashboardView)} />
        </motion.div>

        <motion.div
          initial={{ scale: 0.985, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: "spring", stiffness: 110, damping: 22, delay: 0.05 }}
          className="relative flex flex-1 flex-col overflow-hidden rounded-[24px] border border-white/5 bg-[#0A0A0C] shadow-[0_0_50px_rgba(0,0,0,0.5)]"
        >
          <TopNavbar activeView={effectiveView} />
          <PhaseTabs activeView={effectiveView} onChange={setActiveView} />

          <div className="custom-scrollbar flex-1 overflow-y-auto p-4">
            <div className={`grid items-start gap-4 ${effectiveView === "settings" ? "grid-cols-1" : "grid-cols-[minmax(0,1fr)_300px]"}`}>
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ type: "spring", stiffness: 110, damping: 22, delay: 0.12 }}
              >
                {centerView}
              </motion.div>

              {effectiveView !== "settings" ? (
                <motion.div
                  initial={{ y: 20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ type: "spring", stiffness: 110, damping: 22, delay: 0.16 }}
                >
                  <RightSidebar activeView={effectiveView} />
                </motion.div>
              ) : null}
            </div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}
