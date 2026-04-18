"use client";

import { useBridge } from "@/contexts/BridgeContext";
import { Mic, Clock, BarChart3, Radio, Shield } from "lucide-react";

interface SliderProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  unit: string;
  apiFunc: string;
}

interface ToggleProps {
  label: string;
  checked: boolean;
  apiFunc: string;
  desc: string;
}

const Slider = ({ label, value, min, max, step, unit, apiFunc }: SliderProps) => {
  const { api } = useBridge();
  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">{label}</label>
        <span className="text-xs font-mono text-toxic bg-toxic/10 px-2 py-0.5 border border-toxic/20">
          {value}{unit}
        </span>
      </div>
      <input 
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => {
          const func = api?.[apiFunc as keyof typeof api] as any;
          if (func) func(Number(e.target.value));
        }}
        className="w-full h-1 bg-white/10 appearance-none cursor-pointer accent-toxic"
      />
    </div>
  );
};

const Toggle = ({ label, checked, apiFunc, desc }: ToggleProps) => {
  const { api } = useBridge();
  return (
    <div className="flex items-center justify-between p-4 bg-white/5 border border-border hover:border-violet-500/30 transition-colors group">
      <div className="space-y-1">
        <span className="text-[11px] font-black uppercase text-white group-hover:text-toxic transition-colors">{label}</span>
        <p className="text-[9px] text-muted-foreground uppercase tracking-wider">{desc}</p>
      </div>
      <button 
        onClick={() => {
          const func = api?.[apiFunc as keyof typeof api] as any;
          if (func) func(!checked);
        }}
        className={`w-12 h-6 flex items-center p-1 transition-colors ${checked ? 'bg-toxic' : 'bg-white/10'}`}
      >
        <div className={`w-4 h-4 bg-black transition-transform ${checked ? 'translate-x-6' : 'translate-x-0'}`} />
      </button>
    </div>
  );
};

export default function SettingsPanel() {
  const { settings, api } = useBridge();

  if (!settings) return null;

  return (
    <div className="h-full flex flex-col p-10 max-w-5xl mx-auto overflow-y-auto scrollbar-hide gap-12">
      <header className="flex flex-col gap-2">
         <h1 className="text-5xl font-black italic tracking-tighter uppercase">Neural_Config</h1>
         <p className="text-xs font-mono tracking-[0.4em] text-muted-foreground">MODIFIQUE O NÚCLEO DE RESPOSTA DO COACHER</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
        {/* Voice Section */}
        <section className="space-y-8">
           <div className="flex items-center gap-4 text-violet-400">
              <Mic className="w-5 h-5" />
              <h3 className="text-lg font-black uppercase">Sintetizador & Feedback</h3>
           </div>
           
           <div className="space-y-6">
              <Slider 
                label="Volume Auditivo" 
                value={settings.volume} 
                min={0} max={100} step={1} unit="%" 
                apiFunc="set_volume" 
              />
              
              <div className="grid grid-cols-1 gap-3">
                <Toggle 
                  label="Coach Vocal" 
                  checked={settings.voice_enabled} 
                  apiFunc="toggle_voice"
                  desc="Feedback de voz em tempo real durante a partida"
                />
                <Toggle 
                  label="Foco em Solo Q" 
                  checked={settings.solo_focus} 
                  apiFunc="toggle_solo_focus"
                  desc="Prioriza dicas individuais sobre macro de equipe"
                />
              </div>
           </div>

            <div className="space-y-4">
               <span className="text-[10px] font-black uppercase text-muted-foreground">Personalidade Neural</span>
               <div className="grid grid-cols-3 gap-2">
                  {[
                    { id: 'standard', label: 'Equilibrada' },
                    { id: 'hardcore', label: 'Agressiva' },
                    { id: 'minimal', label: 'Minimalista' }
                  ].map(p => (
                    <button 
                     key={p.id}
                     onClick={() => api?.set_voice_preset(p.id)}
                     className={`p-3 text-[10px] font-black uppercase border transition-all ${
                       settings.voice_preset === p.id ? 'bg-toxic text-black border-toxic' : 'border-border text-muted-foreground hover:border-white/20'
                     }`}
                    >
                      {p.label}
                    </button>
                  ))}
               </div>
            </div>

            <div className="space-y-4">
               <span className="text-[10px] font-black uppercase text-muted-foreground">Engine de Voz</span>
               <div className="grid grid-cols-2 gap-2">
                  {[
                    { id: 'minerva', label: 'Minerva' },
                    { id: 'standard', label: 'Padrao TTS' }
                  ].map(v => (
                    <button 
                     key={v.id}
                     onClick={() => api?.set_voice_personality(v.id)}
                     className={`p-3 text-[10px] font-black uppercase border transition-all ${
                       settings.voice_personality === v.id ? 'bg-violet-500 text-white border-violet-500' : 'border-border text-muted-foreground hover:border-white/20'
                     }`}
                    >
                      {v.label}
                    </button>
                  ))}
               </div>
            </div>
        </section>

        {/* Intervals Section */}
        <section className="space-y-8">
           <div className="flex items-center gap-4 text-toxic">
              <Clock className="w-5 h-5" />
              <h3 className="text-lg font-black uppercase">Frequência de Escaneamento</h3>
           </div>

           <div className="grid grid-cols-1 gap-6">
              <Slider 
                label="Intervalo Macro" 
                value={settings.macro_interval} 
                min={10} max={120} step={5} unit="s" 
                apiFunc="set_macro_interval" 
              />
              <Slider 
                label="Varredura de Minimapa" 
                value={settings.minimap_interval} 
                min={2} max={30} step={1} unit="s" 
                apiFunc="set_minimap_interval" 
              />
              <Slider 
                label="Check de Economia" 
                value={settings.economy_interval} 
                min={30} max={300} step={30} unit="s" 
                apiFunc="set_economy_interval" 
              />
           </div>
        </section>

        {/* Thresholds Section */}
        <section className="space-y-8">
           <div className="flex items-center gap-4 text-amber-500">
              <BarChart3 className="w-5 h-5" />
              <h3 className="text-lg font-black uppercase">Gatilhos de Alerta</h3>
           </div>

           <div className="grid grid-cols-1 gap-6">
              <Slider 
                label="Limite de Visão Critica" 
                value={settings.vision_threshold} 
                min={0} max={100} step={5} unit="%" 
                apiFunc="set_vision_threshold" 
              />
              <Slider 
                label="Déficit de Farm" 
                value={settings.farm_threshold} 
                min={50} max={100} step={5} unit="%" 
                apiFunc="set_farm_threshold" 
              />
           </div>
        </section>

        {/* Presets Section */}
        <section className="space-y-8">
           <div className="flex items-center gap-4 text-red-500">
              <Shield className="w-5 h-5" />
              <h3 className="text-lg font-black uppercase">Modos de Segurança</h3>
           </div>

           <div className="grid grid-cols-1 gap-3">
              <Toggle 
                label="Modo Hardcore" 
                checked={settings.hardcore_enabled} 
                apiFunc="toggle_hardcore"
                desc="Apenas alertas críticos de vida ou morte"
              />
              <Toggle 
                label="Análise de Objetivos" 
                checked={settings.objectives_enabled} 
                apiFunc="toggle_objectives"
                desc="Timers automáticos e calls de Barão/Dragão"
              />
           </div>
        </section>
      </div>

      <footer className="mt-12 mb-20 p-6 border border-toxic/20 bg-toxic/5 flex flex-col md:flex-row justify-between items-center gap-6">
         <div className="flex items-center gap-4">
            <Radio className="w-6 h-6 text-toxic animate-pulse" />
            <div>
               <p className="text-sm font-black uppercase text-white">Sincronização em Tempo Real</p>
               <p className="text-[10px] text-muted-foreground uppercase">Toda alteração é aplicada instantaneamente ao kernel Python</p>
            </div>
         </div>
         <button 
          onClick={() => window.location.reload()}
          className="px-8 py-3 bg-white/5 border border-border text-[10px] font-black uppercase tracking-widest hover:bg-white/10 transition-all"
         >
           Reiniciar Interface
         </button>
      </footer>
    </div>
  );
}
