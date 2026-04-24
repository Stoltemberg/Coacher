"use client";

import type { ComponentType, FormEvent } from "react";
import { useState } from "react";
import { motion, AnimatePresence, Variants } from "framer-motion";
import { ArrowRight, Lock, Mail, Shield, UserRound } from "lucide-react";

import { useBridge } from "@/contexts/BridgeContext";

const containerVariants: Variants = {
  hidden: { opacity: 1, y: 0, scale: 1 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.8,
      ease: [0.16, 1, 0.3, 1],
      staggerChildren: 0.1,
      delayChildren: 0.3,
    },
  },
};

const itemVariants: Variants = {
  hidden: { opacity: 1, x: 0 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.6 },
  },
};

const lineVariants: Variants = {
  hidden: { width: "100%", opacity: 1 },
  visible: {
    width: "100%",
    opacity: 1,
    transition: { duration: 0.8 },
  },
};

interface FieldProps {
  icon: ComponentType<{ className?: string }>;
  label: string;
  placeholder: string;
  type?: string;
  value: string;
  onChange: (value: string) => void;
}

function Field({ icon: Icon, label, placeholder, type = "text", value, onChange }: FieldProps) {
  return (
    <motion.div variants={itemVariants} className="space-y-1">
      <label className="ml-1 text-[10px] font-black uppercase tracking-[0.2em] text-white/55">
        {label}
      </label>
      <div className="group relative">
        <Icon className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-toxic/30 transition-colors group-focus-within:text-toxic" />
        <input
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full rounded-2xl border border-white/10 bg-white/[0.03] p-4 pl-12 text-sm text-white outline-none transition-all placeholder:text-white/20 focus:border-toxic/40 focus:bg-white/[0.05]"
        />
      </div>
    </motion.div>
  );
}

export default function AuthUI() {
  const { api } = useBridge();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isShaking, setIsShaking] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!email || !password || (!isLogin && !displayName.trim())) {
      setError(
        isLogin
          ? "Preencha email e senha para entrar."
          : "Preencha nome, email e senha para criar a conta."
      );
      return;
    }

    try {
      setError("");
      if (isLogin) {
        await api?.login_user(email.trim(), password);
      } else {
        await api?.register_user(email.trim(), password, displayName.trim());
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Nao foi possivel autenticar agora.";
      setError(message);
      setIsShaking(true);
      setTimeout(() => setIsShaking(false), 400);
    }
  };

  return (
    <div className="fixed inset-0 flex h-screen w-screen items-center justify-center overflow-hidden bg-[#050508] p-6">
      <div className="app-backdrop absolute inset-0 z-0" />

      <motion.div
        initial="hidden"
        animate="visible"
        variants={containerVariants}
        className={`app-surface relative z-10 grid w-full max-w-6xl overflow-hidden rounded-[32px] lg:grid-cols-[1.1fr_0.9fr] ${isShaking ? "animate-shake" : ""}`}
      >
        <div className="relative overflow-hidden px-8 py-10 lg:px-12 lg:py-14">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(173,255,47,0.08),_transparent_34%),radial-gradient(circle_at_bottom_right,_rgba(139,92,246,0.1),_transparent_34%)]" />
          <div className="relative z-10 flex h-full flex-col justify-between">
            <div className="space-y-8">
              <motion.div variants={itemVariants} className="inline-flex items-center gap-3 rounded-full border border-white/10 bg-white/[0.04] px-4 py-2">
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white text-sm font-black text-black">
                  C
                </div>
                <div>
                  <div className="text-[10px] font-black uppercase tracking-[0.28em] text-white">
                    COACHER
                  </div>
                  <div className="text-[10px] text-white/45">Desktop coach system</div>
                </div>
              </motion.div>

              <div className="space-y-5">
                <motion.p variants={itemVariants} className="text-[11px] font-mono uppercase tracking-[0.32em] text-toxic/70">
                  League performance workspace
                </motion.p>
                <motion.h1 variants={itemVariants} className="max-w-md text-5xl font-black tracking-[-0.06em] text-white md:text-6xl">
                  Entra e volta para a fila com o mesmo ambiente da plataforma.
                </motion.h1>
                <motion.p variants={itemVariants} className="max-w-xl text-base leading-7 text-white/55">
                  O coach desktop herda a mesma assinatura visual do site: superficies escuras, luz controlada e foco total na leitura da partida.
                </motion.p>
              </div>
            </div>

            <motion.div variants={itemVariants} className="grid gap-4 pt-10 sm:grid-cols-3">
              {[
                ["Sessao segura", "Login persistente por usuario"],
                ["Telemetria viva", "LCU, memoria e configuracoes"],
                ["Mesmo produto", "Site e app com a mesma identidade"],
              ].map(([title, note]) => (
                <div key={title} className="rounded-3xl border border-white/10 bg-white/[0.04] p-4">
                  <div className="mb-2 text-[11px] font-semibold text-white">{title}</div>
                  <div className="text-[11px] leading-6 text-white/45">{note}</div>
                </div>
              ))}
            </motion.div>
          </div>
        </div>

        <div className="relative px-8 py-10 lg:px-12 lg:py-14">
          <div className="absolute inset-0 bg-black/20" />
          <div className="relative z-10">
            <header className="mb-8 space-y-4">
              <motion.div variants={itemVariants} className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-toxic/20 bg-toxic/10">
                  <Shield className="h-5 w-5 text-toxic" />
                </div>
                <div>
                  <h1 className="text-3xl font-black tracking-tight text-white">
                    {isLogin ? "Entrar no Coacher" : "Criar acesso"}
                  </h1>
                  <p className="mt-1 text-sm text-white/45">
                    {isLogin
                      ? "Usa tua conta para liberar o coach nesta maquina."
                      : "Cria tua conta para salvar memoria, configuracoes e historico."}
                  </p>
                </div>
              </motion.div>
              <motion.div variants={lineVariants} className="h-px w-full bg-gradient-to-r from-white/20 to-transparent" />
            </header>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-4">
                {!isLogin && (
                  <Field
                    icon={UserRound}
                    label="Nome de exibicao"
                    placeholder="Como voce quer aparecer no app"
                    value={displayName}
                    onChange={setDisplayName}
                  />
                )}

                <Field
                  icon={Mail}
                  label="Email"
                  placeholder="voce@exemplo.com"
                  type="email"
                  value={email}
                  onChange={setEmail}
                />

                <Field
                  icon={Lock}
                  label="Senha"
                  placeholder="Sua senha"
                  type="password"
                  value={password}
                  onChange={setPassword}
                />
              </div>

              <AnimatePresence>
                {error && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="rounded-2xl border border-red-500/20 bg-red-500/10 p-4 text-center text-[11px] font-medium text-red-300"
                  >
                    {error}
                  </motion.div>
                )}
              </AnimatePresence>

              <motion.button
                variants={itemVariants}
                type="submit"
                className="group relative w-full overflow-hidden rounded-full bg-white px-6 py-5 transition-all duration-300 hover:bg-toxic"
              >
                <div className="relative z-10 flex items-center justify-center gap-3 text-xs font-black uppercase tracking-widest text-black">
                  <span>{isLogin ? "Entrar" : "Criar conta"}</span>
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </div>
              </motion.button>

              <motion.div variants={itemVariants} className="flex justify-center">
                <button
                  onClick={() => setIsLogin(!isLogin)}
                  className="border-b border-transparent pb-1 text-[10px] font-mono uppercase tracking-[0.24em] text-white/45 transition-colors hover:border-white/20 hover:text-white"
                >
                  {isLogin ? "Criar conta nova" : "Voltar para login"}
                </button>
              </motion.div>
            </form>

            <div className="mt-8 rounded-3xl border border-white/10 bg-white/[0.04] p-4 text-[11px] leading-6 text-white/45">
              O login libera o app Python, inicia a conexao com o cliente do League e carrega tuas preferencias salvas.
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
