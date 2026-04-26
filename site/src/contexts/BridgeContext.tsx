"use client";

import React, { createContext, useCallback, useContext, useEffect, useState } from "react";

import {
  AuthSnapshot,
  CoachCallSnapshot,
  CoachLogEntry,
  DraftRecommendationsSnapshot,
  JungleIntel,
  PerformanceSnapshot,
  PostGameSummary,
  PythonApi,
  SettingsSnapshot,
} from "@/types/bridge";
import { buildCoachCallSnapshot } from "@/components/app/coach-call";

interface BridgeContextType {
  auth: AuthSnapshot | null;
  settings: SettingsSnapshot | null;
  gameState: {
    phase: string;
    summonerName: string | null;
    championName: string | null;
  };
  jungleIntel: JungleIntel | null;
  performance: PerformanceSnapshot | null;
  draftRecommendations: DraftRecommendationsSnapshot | null;
  matchIntel: { name: string; champion: string; rank: string; winrate: string }[];
  summary: PostGameSummary | null;
  logs: CoachLogEntry[];
  isReady: boolean;
  api: PythonApi | null;
  updateSettings: (key: keyof SettingsSnapshot, value: unknown) => void;
  setCategoryEnabled: (category: string, state: boolean) => void;
}

const BridgeContext = createContext<BridgeContextType | undefined>(undefined);

export function BridgeProvider({ children }: { children: React.ReactNode }) {
  const [auth, setAuth] = useState<AuthSnapshot | null>(null);
  const [settings, setSettings] = useState<SettingsSnapshot | null>(null);
  const [gameState, setGameState] = useState({
    phase: "Lobby",
    summonerName: null as string | null,
    championName: null as string | null,
  });
  const [jungleIntel, setJungleIntel] = useState<JungleIntel | null>(null);
  const [performance, setPerformance] = useState<PerformanceSnapshot | null>(null);
  const [draftRecommendations, setDraftRecommendations] = useState<DraftRecommendationsSnapshot | null>(null);
  const [matchIntel, setMatchIntel] = useState<
    { name: string; champion: string; rank: string; winrate: string }[]
  >([]);
  const [summary, setSummary] = useState<PostGameSummary | null>(null);
  const [logs, setLogs] = useState<CoachLogEntry[]>([]);
  const [isReady, setIsReady] = useState(false);

  const addLog = useCallback((message: string, type: string = "normal", category?: string | null, call?: CoachCallSnapshot) => {
    const structuredCall = buildCoachCallSnapshot(message, type, category, call);
    setLogs((prev) => [
      ...prev.slice(-49),
      { message, type, category: category ?? null, call: structuredCall, id: Date.now() + Math.random() },
    ]);
  }, []);

  useEffect(() => {
    window.addPreGameStat = (name, champion, rank, winrate) => {
      setMatchIntel((prev) => {
        const existing = prev.findIndex((player) => player.name === name);
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
        championName: championName || null,
      });

      if (phase === "Lobby" || phase.toLowerCase().includes("champ")) {
        setMatchIntel([]);
      }
      if (!phase.toLowerCase().includes("champ")) {
        setDraftRecommendations(null);
      }
    };

    window.hydrateSettings = (snapshot) => {
      console.log("[Bridge] hydrateSettings", snapshot);
      setSettings(snapshot);
    };

    window.updatePerformanceSnapshot = (snapshot) => {
      setPerformance(snapshot);
    };

    window.updateJungleIntel = (payload) => {
      setJungleIntel(payload);
    };

    window.updateDraftRecommendations = (payload) => {
      setDraftRecommendations(payload);
    };

    window.updatePostGameSummary = (nextSummary) => {
      setSummary(nextSummary);
    };

    window.appendPostGameMemory = (entry) => {
      setSummary((prev) => {
        if (!prev) return null;
        return {
          ...prev,
          memory: [...prev.memory, entry],
        };
      });
    };

    window.addAILog = (message, type, category, call) => {
      addLog(message, type, category, call);
    };

    window.playTTSUpdate = (message, type, category, call) => {
      addLog(message, type || "normal", category, call);
    };

    window.setCoachTaxonomyFocus = (categoryId) => {
      console.log("[Bridge] setCoachTaxonomyFocus", categoryId);
    };

    const checkReady = () => {
      console.log(
        "[Bridge] Checking if pywebview is ready...",
        !!window.pywebview,
        !!window.pywebview?.api
      );

      if (window.pywebview && window.pywebview.api) {
        console.log("[Bridge] Environment detected! Initializing...");
        setIsReady(true);
        window.pywebview.api.get_auth_snapshot().then((snapshot) => {
          console.log("[Bridge] Auth sync complete");
          setAuth(snapshot);
        });
        window.pywebview.api.get_settings_snapshot().then((snapshot) => {
          console.log("[Bridge] Settings sync complete");
          setSettings(snapshot);
        });
        window.pywebview.api.get_performance_snapshot().then((snapshot) => {
          setPerformance(snapshot);
        });
        window.pywebview.api.get_jungle_intel_snapshot().then((snapshot) => {
          setJungleIntel(snapshot);
        });
        window.pywebview.api.notify_ui_ready();
        addLog("Núcleo do Coacher online.", "system");
        addLog("Conexão local estabelecida com o app desktop.", "system");
        addLog("Sincronização de telemetria pendente. Aguardando LCU.", "normal");
      }
    };

    window.addEventListener("pywebviewready", checkReady);
    checkReady();

    return () => {
      window.removeEventListener("pywebviewready", checkReady);
    };
  }, [addLog]);

  const updateSettings = useCallback((key: keyof SettingsSnapshot, value: unknown) => {
    setSettings((prev) => {
      if (!prev) return null;
      return { ...prev, [key]: value };
    });

    if (window.pywebview && window.pywebview.api) {
      const api = window.pywebview.api;
      const apiMap: Partial<Record<keyof SettingsSnapshot, keyof PythonApi>> = {
        volume: "set_volume",
        voice_enabled: "toggle_voice",
        objectives_enabled: "toggle_objectives",
        hardcore_enabled: "toggle_hardcore",
        solo_focus: "toggle_solo_focus",
        macro_interval: "set_macro_interval",
        minimap_interval: "set_minimap_interval",
        economy_interval: "set_economy_interval",
        item_check_interval: "set_item_check_interval",
        farm_threshold: "set_farm_threshold",
        vision_threshold: "set_vision_threshold",
        voice_preset: "set_voice_preset",
        voice_personality: "set_voice_personality",
        primary_role: "set_primary_role",
        player_goal: "set_player_goal",
        playstyle_profile: "set_playstyle_profile",
      };

      if (key === "main_champions") {
        api.set_main_champions(value as string[]);
        api.get_performance_snapshot().then(setPerformance);
        return;
      }

      if (key === "preferred_champion_pool") {
        api.set_preferred_champion_pool(value as string[]);
        return;
      }

      if (key === "prioritize_pool_picks") {
        api.toggle_prioritize_pool_picks(Boolean(value));
        return;
      }

      const funcName = apiMap[key];
      if (funcName) {
        const handler = api[funcName] as unknown as ((payload: unknown) => void) | undefined;
        handler?.(value);
        if (key === "primary_role" || key === "player_goal" || key === "playstyle_profile") {
          api.get_performance_snapshot().then(setPerformance);
        }
      }
    }
  }, []);

  const setCategoryEnabled = useCallback((category: string, state: boolean) => {
    setSettings((prev) => {
      if (!prev) return null;
      return {
        ...prev,
        category_filters: {
          ...prev.category_filters,
          [category]: state,
        },
      };
    });

    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.set_category_enabled(category, state);
    }
  }, []);

  const value = {
    auth,
    settings,
    gameState,
    jungleIntel,
    performance,
    draftRecommendations,
    matchIntel,
    summary,
    logs,
    isReady,
    api: typeof window !== "undefined" ? window.pywebview?.api || null : null,
    updateSettings,
    setCategoryEnabled,
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
