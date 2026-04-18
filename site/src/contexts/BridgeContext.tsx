"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import {
  AuthSnapshot,
  SettingsSnapshot,
  JungleIntel,
  PostGameSummary,
  PythonApi
} from "@/types/bridge";

interface BridgeContextType {
  auth: AuthSnapshot | null;
  settings: SettingsSnapshot | null;
  gameState: {
    phase: string;
    summonerName: string | null;
    championName: string | null;
  };
  jungleIntel: JungleIntel | null;
  matchIntel: {name: string; champion: string; rank: string; winrate: string}[];
  summary: PostGameSummary | null;
  logs: { message: string; type: string; id: number }[];
  isReady: boolean;
  api: PythonApi | null;
}

const BridgeContext = createContext<BridgeContextType | undefined>(undefined);

export function BridgeProvider({ children }: { children: React.ReactNode }) {
  const [auth, setAuth] = useState<AuthSnapshot | null>(null);
  const [settings, setSettings] = useState<SettingsSnapshot | null>(null);
  const [gameState, setGameState] = useState({ 
    phase: "Lobby", 
    summonerName: null as string | null,
    championName: null as string | null 
  });
  const [jungleIntel, setJungleIntel] = useState<JungleIntel | null>(null);
  const [matchIntel, setMatchIntel] = useState<{name: string; champion: string; rank: string; winrate: string}[]>([]);
  const [summary, setSummary] = useState<PostGameSummary | null>(null);
  const [logs, setLogs] = useState<{ message: string; type: string; id: number }[]>([]);
  const [isReady, setIsReady] = useState(false);

  const addLog = useCallback((message: string, type: string = "normal") => {
    setLogs((prev) => [...prev.slice(-49), { message, type, id: Date.now() + Math.random() }]);
  }, []);

  useEffect(() => {
    // Bind global functions for Python to call
    window.addPreGameStat = (name, champion, rank, winrate) => {
      setMatchIntel(prev => {
        const existing = prev.findIndex(p => p.name === name);
        if (existing !== -1) {
          const next = [...prev];
          next[existing] = { name, champion, rank, winrate };
          return next;
        }
        return [...prev, { name, champion, rank, winrate }];
      });
    };
    window.hydrateAuthState = (snapshot) => {
      console.log("[Bridge] hydrateAuthState", snapshot);
      setAuth(snapshot);
    };

    window.updateGameState = (phase, summonerName, championName) => {
      console.log("[Bridge] updateGameState", phase, summonerName, championName);
      setGameState({ 
        phase, 
        summonerName: summonerName || null,
        championName: championName || null
      });
      
      if (phase === 'Lobby' || phase === 'Seleção de Campeões') {
        setMatchIntel([]);
      }
    };

    window.hydrateSettings = (snapshot) => {
      console.log("[Bridge] hydrateSettings", snapshot);
      setSettings(snapshot);
    };

    window.updateJungleIntel = (payload) => {
      setJungleIntel(payload);
    };

    window.updatePostGameSummary = (summary) => {
      setSummary(summary);
    };

    window.appendPostGameMemory = (entry) => {
      setSummary((prev) => {
        if (!prev) return null;
        return {
          ...prev,
          memory: [...prev.memory, entry]
        };
      });
    };

    window.addAILog = (message, type) => {
      addLog(message, type);
    };

    window.playTTSUpdate = (message, type, _category) => {
      addLog(message, type || "normal");
      // Could also trigger a visual highlight for the category here
    };

    window.setCoachTaxonomyFocus = (categoryId) => {
      // Handle UI focus shift
      console.log("[Bridge] setCoachTaxonomyFocus", categoryId);
    };

    // Check if pywebview is already ready
    const checkReady = () => {
      if (window.pywebview && window.pywebview.api) {
        setIsReady(true);
        window.pywebview.api.get_auth_snapshot().then(setAuth);
        window.pywebview.api.get_settings_snapshot().then(setSettings);
        window.pywebview.api.notify_ui_ready();
        addLog("Conexão estelar estabelecida com o núcleo Python.", "system");
      }
    };

    window.addEventListener("pywebviewready", checkReady);
    checkReady(); // Initial check

    return () => {
      window.removeEventListener("pywebviewready", checkReady);
    };
  }, [addLog]);

  const value = {
    auth,
    settings,
    gameState,
    jungleIntel,
    matchIntel,
    summary,
    logs,
    isReady,
    api: typeof window !== "undefined" ? window.pywebview?.api || null : null
  };

  return <BridgeContext.Provider value={value}>{children}</BridgeContext.Provider>;
}

export function useBridge() {
  const context = useContext(BridgeContext);
  if (context === undefined) {
    throw new Error("useBridge must be used within a BridgeProvider");
  }
  return context;
}
