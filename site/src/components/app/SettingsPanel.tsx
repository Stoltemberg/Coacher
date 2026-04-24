import { KeyboardEvent, useState } from "react";
import { motion, Variants } from "framer-motion";
import { useBridge } from "@/contexts/BridgeContext";
import { SettingsSnapshot } from "@/types/bridge";
import { BarChart3, Clock, Mic, Radio, Shield, Sparkles, Swords, X } from "lucide-react";

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { type: "spring", stiffness: 100, damping: 20 },
  },
};

interface SliderProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  unit: string;
  settingKey: keyof SettingsSnapshot;
}

interface ToggleProps {
  label: string;
  checked: boolean;
  settingKey: keyof SettingsSnapshot;
  desc: string;
}

function SectionHeading({
  icon: Icon,
  title,
  note,
}: {
  icon: typeof Mic;
  title: string;
  note: string;
}) {
  return (
    <div className="flex items-center gap-4">
      <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.04]">
        <Icon className="h-5 w-5 text-toxic" />
      </div>
      <div>
        <h3 className="text-xl font-black tracking-tight text-white">{title}</h3>
        <p className="mt-1 text-sm text-white/45">{note}</p>
      </div>
    </div>
  );
}

const Slider = ({ label, value, min, max, step, unit, settingKey }: SliderProps) => {
  const { updateSettings } = useBridge();
  return (
    <div className="space-y-3 rounded-3xl border border-white/8 bg-white/[0.03] p-4">
      <div className="flex items-center justify-between gap-4">
        <label className="text-[10px] font-black uppercase tracking-[0.2em] text-white/55">
          {label}
        </label>
        <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs font-mono text-toxic">
          {value}
          {unit}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => updateSettings(settingKey, Number(e.target.value))}
        className="h-1 w-full cursor-pointer appearance-none rounded-full bg-white/10 accent-toxic"
      />
    </div>
  );
};

const Toggle = ({ label, checked, settingKey, desc }: ToggleProps) => {
  const { updateSettings } = useBridge();
  return (
    <div className="group flex items-center justify-between rounded-3xl border border-white/8 bg-white/[0.04] p-4 transition-colors hover:border-white/15 hover:bg-white/[0.06]">
      <div className="space-y-1 pr-4">
        <span className="text-[11px] font-semibold text-white">{label}</span>
        <p className="text-[10px] uppercase tracking-[0.14em] text-white/38">{desc}</p>
      </div>
      <button
        onClick={() => updateSettings(settingKey, !checked)}
        className={`flex h-7 w-12 shrink-0 items-center rounded-full p-1 transition-colors ${checked ? "bg-toxic" : "bg-white/10"}`}
      >
        <div className={`h-5 w-5 rounded-full bg-black transition-transform ${checked ? "translate-x-5" : "translate-x-0"}`} />
      </button>
    </div>
  );
};

const normalizeChampionName = (value: string) =>
  value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-zA-Z0-9\s'-]/g, " ")
    .replace(/\s+/g, " ")
    .trim();

export default function SettingsPanel() {
  const { settings, updateSettings, setCategoryEnabled } = useBridge();
  const [poolInput, setPoolInput] = useState("");

  if (!settings) return null;

  const preferredPool = settings.preferred_champion_pool ?? [];

  const commitPoolEntry = () => {
    const normalized = normalizeChampionName(poolInput);
    if (!normalized) return;

    const exists = preferredPool.some(
      (champion) => champion.localeCompare(normalized, undefined, { sensitivity: "accent" }) === 0
    );
    if (exists) {
      setPoolInput("");
      return;
    }

    updateSettings("preferred_champion_pool", [...preferredPool, normalized]);
    setPoolInput("");
  };

  const handlePoolInputKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter" || event.key === ",") {
      event.preventDefault();
      commitPoolEntry();
    }
  };

  const removeChampionFromPool = (championToRemove: string) => {
    updateSettings(
      "preferred_champion_pool",
      preferredPool.filter((champion) => champion !== championToRemove)
    );
  };

  const presetOptions =
    settings.voice_catalog?.presets ?? [
      { id: "standard", label: "Equilibrado", description: "" },
      { id: "hardcore", label: "Agressivo", description: "" },
      { id: "minimal", label: "Minimal", description: "" },
    ];

  const personalityOptions =
    settings.voice_catalog?.personalities ?? [
      {
        id: "standard",
        label: "Padrao",
        engine: "edge_tts",
        tier: "free",
        description: "Voz neural local.",
        provider: "Local",
      },
      {
        id: "minerva",
        label: "Minerva",
        engine: "elevenlabs",
        tier: "premium",
        description: "Voz premium.",
        provider: "ElevenLabs",
      },
    ];

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      className="custom-scrollbar h-full w-full overflow-y-auto bg-transparent px-6 pb-12 pt-2"
    >
      <header className="app-surface mb-6 rounded-[32px] px-8 py-7">
        <div className="max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-[10px] font-mono uppercase tracking-[0.24em] text-toxic/80">
            <Sparkles className="h-3.5 w-3.5" />
            painel de configuracoes
          </div>
          <h1 className="text-4xl font-black tracking-[-0.06em] text-white">
            Ajusta o coach do teu jeito.
          </h1>
          <p className="max-w-2xl text-sm leading-7 text-white/52">
            Menos vazio, mais controle: voz, ritmo de leitura, filtros e a base para novas personalidades no futuro.
          </p>
        </div>
      </header>

      <div className="grid grid-cols-1 gap-6 2xl:grid-cols-[1.08fr_0.92fr]">
        <motion.section variants={itemVariants} className="app-surface space-y-6 rounded-[32px] p-7">
          <SectionHeading
            icon={Mic}
            title="Voz e personalidade"
            note="Escolhe o motor de voz e a intensidade da entrega durante a partida."
          />

          <div className="grid gap-4 xl:grid-cols-[0.92fr_1.08fr]">
            <Slider
              label="Volume auditivo"
              value={settings.volume}
              min={0}
              max={100}
              step={1}
              unit="%"
              settingKey="volume"
            />

            <div className="grid gap-4 md:grid-cols-2">
              <Toggle
                label="Coach vocal"
                checked={settings.voice_enabled}
                settingKey="voice_enabled"
                desc="audio ativo"
              />
              <Toggle
                label="Foco em Solo Q"
                checked={settings.solo_focus}
                settingKey="solo_focus"
                desc="prioridade no teu jogo"
              />
            </div>
          </div>

          <div className="grid gap-5 xl:grid-cols-2">
            <div className="space-y-3">
              <span className="text-[10px] font-black uppercase tracking-[0.2em] text-white/55">
                Modo de fala
              </span>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-3 xl:grid-cols-1">
                {presetOptions.map((preset) => (
                  <button
                    key={preset.id}
                    onClick={() => updateSettings("voice_preset", preset.id)}
                    className={`rounded-3xl border p-4 text-left transition-all ${
                      settings.voice_preset === preset.id
                        ? "border-white/20 bg-white text-black"
                        : "border-white/8 bg-white/[0.04] text-white/60 hover:bg-white/[0.08]"
                    }`}
                  >
                    <div className="text-[11px] font-semibold">{preset.label}</div>
                    {preset.description ? (
                      <div className="mt-1 text-[10px] leading-5 opacity-70">{preset.description}</div>
                    ) : null}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-3">
              <span className="text-[10px] font-black uppercase tracking-[0.2em] text-white/55">
                Escolha de voz
              </span>
              <div className="grid gap-3">
                {personalityOptions.map((voice) => (
                  <button
                    key={voice.id}
                    onClick={() => updateSettings("voice_personality", voice.id)}
                    className={`rounded-3xl border p-4 text-left transition-all ${
                      settings.voice_personality === voice.id
                        ? "border-toxic/40 bg-toxic/10"
                        : "border-white/8 bg-white/[0.04] hover:border-white/15 hover:bg-white/[0.06]"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="text-[11px] font-semibold text-white">{voice.label}</div>
                        <div className="mt-1 text-[10px] leading-5 text-white/42">
                          {voice.description}
                        </div>
                      </div>
                      <span className="rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-1 text-[9px] font-mono uppercase tracking-[0.14em] text-white/45">
                        {voice.provider}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </motion.section>

        <motion.section variants={itemVariants} className="app-surface space-y-6 rounded-[32px] p-7">
          <SectionHeading
            icon={Swords}
            title="Pool preferida"
            note="Mantem uma shortlist de campeoes e, se quiser, puxa esses picks para o topo."
          />

          <div className="grid gap-4 xl:grid-cols-[1.15fr_0.85fr]">
            <div className="space-y-3 rounded-3xl border border-white/8 bg-white/[0.03] p-4">
              <div className="flex items-center justify-between gap-3">
                <label className="text-[10px] font-black uppercase tracking-[0.2em] text-white/55">
                  Campeoes da pool
                </label>
                <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-[9px] font-mono uppercase tracking-[0.14em] text-white/45">
                  {preferredPool.length} salvo{preferredPool.length === 1 ? "" : "s"}
                </span>
              </div>

              <div className="flex flex-wrap gap-2">
                {preferredPool.length > 0 ? (
                  preferredPool.map((champion) => (
                    <button
                      key={champion}
                      type="button"
                      onClick={() => removeChampionFromPool(champion)}
                      className="inline-flex items-center gap-2 rounded-full border border-toxic/20 bg-toxic/10 px-3 py-1.5 text-[11px] font-semibold text-white transition-colors hover:border-toxic/40 hover:bg-toxic/15"
                    >
                      {champion}
                      <X className="h-3 w-3 text-white/55" />
                    </button>
                  ))
                ) : (
                  <p className="text-[11px] leading-6 text-white/42">
                    Adiciona alguns campeoes para criar tua shortlist de picks.
                  </p>
                )}
              </div>

              <div className="flex flex-col gap-3 sm:flex-row">
                <input
                  type="text"
                  value={poolInput}
                  onChange={(event) => setPoolInput(event.target.value)}
                  onKeyDown={handlePoolInputKeyDown}
                  placeholder="Ex.: Ahri, Jinx, Lee Sin"
                  className="h-12 flex-1 rounded-2xl border border-white/10 bg-black/20 px-4 text-sm text-white outline-none transition-colors placeholder:text-white/22 focus:border-toxic/50"
                />
                <button
                  type="button"
                  onClick={commitPoolEntry}
                  className="h-12 rounded-2xl border border-white/10 bg-white/[0.06] px-5 text-[10px] font-black uppercase tracking-[0.18em] text-white transition-all hover:border-white/20 hover:bg-white hover:text-black"
                >
                  Adicionar
                </button>
              </div>

              <p className="text-[10px] uppercase tracking-[0.14em] text-white/30">
                Enter ou virgula adiciona o nome. Clique num chip para remover.
              </p>
            </div>

            <Toggle
              label="Priorizar picks da tua pool"
              checked={settings.prioritize_pool_picks}
              settingKey="prioritize_pool_picks"
              desc="ordena sugestoes pelo teu conforto"
            />
          </div>
        </motion.section>

        <motion.section variants={itemVariants} className="app-surface space-y-6 rounded-[32px] p-7">
          <SectionHeading
            icon={Clock}
            title="Ritmo de leitura"
            note="Controla a frequencia de analise do coach durante a partida."
          />

          <div className="grid gap-4 md:grid-cols-2">
            <Slider
              label="Intervalo macro"
              value={settings.macro_interval}
              min={10}
              max={120}
              step={5}
              unit="s"
              settingKey="macro_interval"
            />
            <Slider
              label="Varredura de minimapa"
              value={settings.minimap_interval}
              min={2}
              max={30}
              step={1}
              unit="s"
              settingKey="minimap_interval"
            />
            <Slider
              label="Escaneamento de economia"
              value={settings.economy_interval}
              min={30}
              max={300}
              step={10}
              unit="s"
              settingKey="economy_interval"
            />
            <Slider
              label="Checagem de itens"
              value={settings.item_check_interval}
              min={60}
              max={600}
              step={30}
              unit="s"
              settingKey="item_check_interval"
            />
          </div>
        </motion.section>

        <motion.section variants={itemVariants} className="app-surface space-y-6 rounded-[32px] p-7">
          <SectionHeading
            icon={BarChart3}
            title="Limiares de decisao"
            note="Define em que ponto o coach considera farm e visao abaixo do ideal."
          />
          <div className="grid gap-4 md:grid-cols-2">
            <Slider
              label="Meta de farm por minuto"
              value={settings.farm_threshold}
              min={5}
              max={12}
              step={0.5}
              unit=" cs/m"
              settingKey="farm_threshold"
            />
            <Slider
              label="Media de visao"
              value={settings.vision_threshold}
              min={0.5}
              max={3}
              step={0.1}
              unit=" pts/m"
              settingKey="vision_threshold"
            />
          </div>
        </motion.section>

        <motion.section variants={itemVariants} className="app-surface space-y-6 rounded-[32px] p-7">
          <SectionHeading
            icon={Shield}
            title="Controles de seguranca"
            note="Camadas que alteram intensidade geral e foco em objetivos."
          />
          <div className="grid gap-4 md:grid-cols-2">
            <Toggle
              label="Modo Hardcore"
              checked={settings.hardcore_enabled}
              settingKey="hardcore_enabled"
              desc="pressao maxima"
            />
            <Toggle
              label="Analise de objetivos"
              checked={settings.objectives_enabled}
              settingKey="objectives_enabled"
              desc="foco em objetivos globais"
            />
          </div>
        </motion.section>

        <motion.section variants={itemVariants} className="app-surface space-y-6 rounded-[32px] p-7 2xl:col-span-2">
          <SectionHeading
            icon={Radio}
            title="Filtros por topico"
            note="Escolhe quais categorias do coach podem aparecer durante a partida."
          />
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {settings.category_filters &&
              Object.entries(settings.category_filters).map(([cat, enabled]) => {
                const labels: Record<string, string> = {
                  draft: "Fase de pick/ban",
                  lane: "Controle de rota",
                  macro: "Decisoes de macro",
                  objective: "Objetivos globais",
                  economy: "Gestao de economia",
                  recovery: "Recuperacao de jogo",
                };
                return (
                  <div
                    key={cat}
                    className="group flex items-center justify-between rounded-3xl border border-white/8 bg-white/[0.04] p-4 transition-colors hover:border-white/15 hover:bg-white/[0.06]"
                  >
                    <div className="space-y-0.5 pr-4">
                      <span className="text-[11px] font-semibold text-white">{labels[cat] || cat}</span>
                      <div className="text-[9px] font-mono uppercase tracking-[0.14em] text-white/30">
                        ID: {cat.toUpperCase()}
                      </div>
                    </div>
                    <button
                      onClick={() => setCategoryEnabled(cat, !enabled)}
                      className={`flex h-6 w-11 shrink-0 items-center rounded-full p-1 transition-colors ${
                        enabled ? "bg-toxic shadow-[0_0_10px_rgba(34,197,94,0.3)]" : "bg-white/10"
                      }`}
                    >
                      <div className={`h-4 w-4 rounded-full bg-black transition-transform ${enabled ? "translate-x-5" : "translate-x-0"}`} />
                    </button>
                  </div>
                );
              })}
          </div>
        </motion.section>
      </div>

      <footer className="app-surface mt-6 flex flex-col items-center justify-between gap-5 rounded-[32px] p-6 md:flex-row">
        <div className="flex items-center gap-5">
          <Radio className="h-7 w-7 animate-pulse text-toxic" />
          <div>
            <p className="text-base font-black uppercase leading-tight text-white">
              Sincronizacao em tempo real
            </p>
            <p className="text-[10px] font-mono uppercase tracking-[0.18em] text-white/38">
              Toda alteracao e aplicada no app Python imediatamente.
            </p>
          </div>
        </div>
        <button
          onClick={() => window.location.reload()}
          className="rounded-full border border-white/10 bg-white/[0.04] px-10 py-3 text-[10px] font-black uppercase tracking-[0.24em] text-white transition-all hover:bg-white hover:text-black"
        >
          Reiniciar interface
        </button>
      </footer>
    </motion.div>
  );
}
