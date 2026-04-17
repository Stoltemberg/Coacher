"use client";

import { useState } from "react";
import { MessageSquare, AlertTriangle, ShieldCheck } from "lucide-react";
import clsx from "clsx";

const responses = {
  standard: "Você perdeu a catapulta. Fique atento à precisão do mouse e ao tempo da rota.",
  hardcore: "Até um Yone cego teria acertado essa catapulta. Se você não acordar, eu corto o microfone. VERGONHOSO.",
};

export default function PersonalityDemo() {
  const [mode, setMode] = useState<"standard" | "hardcore">("standard");

  return (
    <section className="py-32 px-6 bg-white/[0.02] border-y border-border">
      <div className="max-w-4xl mx-auto text-center">
        <h2 className="text-4xl md:text-6xl mb-8 uppercase font-black">Interação Dinâmica.</h2>
        <p className="text-muted-foreground mb-16 font-mono uppercase tracking-widest text-sm">
          O MOTOR MINERVA_VOICE OFERECE DIFERENTES PERFIS DE FEEDBACK PARA CADA ESTILO DE ATLETA.
        </p>

        <div className="flex justify-center gap-4 mb-12">
          <button
            onClick={() => setMode("standard")}
            className={clsx(
              "px-8 py-4 font-bold border transition-all",
              mode === "standard" ? "bg-white text-black border-white" : "border-border text-muted-foreground"
            )}
          >
            PADRÃO
          </button>
          <button
            onClick={() => setMode("hardcore")}
            className={clsx(
              "px-8 py-4 font-bold border transition-all",
              mode === "hardcore" ? "bg-accent text-white border-accent" : "border-border text-muted-foreground"
            )}
          >
            HARDCORE
          </button>
        </div>

        <div className="relative p-12 brutalist-border bg-black min-h-[300px] flex flex-col items-center justify-center overflow-hidden">
          <div className="absolute top-4 left-4 flex gap-2">
            <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
            <div className="w-2 h-2 rounded-full bg-zinc-800" />
            <div className="w-2 h-2 rounded-full bg-zinc-800" />
          </div>

          <div className="flex flex-col items-center gap-8 max-w-lg">
            {mode === "standard" ? (
              <ShieldCheck className="w-12 h-12 text-blue-400" />
            ) : (
              <AlertTriangle className="w-12 h-12 text-toxic" />
            )}

            <p className={clsx(
              "text-2xl font-bold leading-tight uppercase transition-all duration-500",
              mode === "hardcore" ? "text-toxic scale-110" : "text-white"
            )}>
              &quot;{responses[mode]}&quot;
            </p>

            <div className="flex items-center gap-2 text-muted-foreground text-[10px] font-mono tracking-widest uppercase">
              <MessageSquare className="w-3 h-3" />
              AI_COACH_FEEDBACK_{mode === "standard" ? "PADRAO" : "HARDCORE"}
            </div>
          </div>

          {/* Glitch effect for hardcore */}
          {mode === "hardcore" && (
            <div className="absolute inset-0 pointer-events-none border-2 border-toxic/20 animate-pulse opacity-50" />
          )}
        </div>
      </div>
    </section>
  );
}
