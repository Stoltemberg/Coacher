"use client";

import { useBridge } from "@/contexts/BridgeContext";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Lock, User, AtSign, Loader2, ArrowRight } from "lucide-react";

export default function AuthUI() {
  const { auth, api } = useBridge();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!api) return;
    
    setLoading(true);
    setError(null);

    try {
      if (mode === "signup") {
        await api.register_user(email, password, displayName);
      } else {
        await api.login_user(email, password);
      }
    } catch {
      setError("FALHA NA CONEXÃO NEURAL");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 w-full h-full flex items-center justify-center p-6 bg-[#050505] text-white selection:bg-violet-500/30 overflow-hidden">
      {/* Dynamic Background */}
      <div className="absolute inset-0 z-0">
        <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-violet-600/10 rounded-full blur-[120px] animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-toxic/5 rounded-full blur-[120px] animate-pulse delay-700" />
        <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-[0.03]" />
      </div>

      {/* Scratched Overlay Effect */}
      <div className="absolute inset-0 z-1 pointer-events-none opacity-20">
        <div className="absolute top-0 left-[20%] w-px h-full bg-gradient-to-b from-transparent via-white/10 to-transparent" />
        <div className="absolute top-0 left-[80%] w-px h-full bg-gradient-to-b from-transparent via-white/10 to-transparent" />
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="w-full max-sm z-10 mx-auto"
      >
        {/* Main Glassmorphism Card */}
        <div className="relative group brutalist-border bg-black/90 backdrop-blur-3xl p-8 space-y-8 border-white/5 shadow-[0_0_50px_-12px_rgba(139,92,246,0.3)]">
          {/* Neural Pulse Corners */}
          <div className="absolute -top-px -left-px w-8 h-8 border-t border-l border-toxic/60" />
          <div className="absolute -bottom-px -right-px w-8 h-8 border-b border-r border-violet-500/60" />
          
          <header className="text-center space-y-3">
            <h2 className="text-3xl font-black italic tracking-tighter leading-none text-white lg:text-4xl">
              {mode === 'login' ? 'NEURAL_LINK' : 'INITIAL_SYNC'}
            </h2>
            <div className="flex items-center justify-center gap-2">
              <div className="h-px w-4 bg-toxic/30" />
              <p className="text-[9px] font-mono tracking-[0.3em] text-muted-foreground uppercase">
                {mode === 'login' ? 'AUTENTICAÇÃO_NÍVEL_1' : 'REGISTRO_DE_SUMMONER'}
              </p>
              <div className="h-px w-4 bg-toxic/30" />
            </div>
          </header>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-3">
              <AnimatePresence mode="wait">
                {mode === "signup" && (
                  <motion.div 
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="relative group overflow-hidden"
                  >
                    <User className="absolute left-4 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground group-focus-within:text-toxic transition-colors" />
                    <input
                      type="text"
                      placeholder="IDENTIDADE_VISUAL"
                      value={displayName}
                      onChange={(e) => setDisplayName(e.target.value)}
                      required
                      className="w-full h-12 bg-white/5 border border-white/10 px-10 text-[11px] font-mono text-white placeholder:text-muted-foreground/30 focus:border-toxic/50 focus:bg-white/10 outline-none transition-all"
                    />
                  </motion.div>
                )}
              </AnimatePresence>

              <div className="relative group">
                <AtSign className="absolute left-4 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground group-focus-within:text-violet-400 transition-colors" />
                <input
                  type="email"
                  placeholder="CANAL_DE_DADOS (EMAIL)"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full h-12 bg-white/5 border border-white/10 px-10 text-[11px] font-mono text-white placeholder:text-muted-foreground/30 focus:border-violet-500/50 focus:bg-white/10 outline-none transition-all"
                />
              </div>

              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground group-focus-within:text-violet-400 transition-colors" />
                <input
                  type="password"
                  placeholder="CHAVE_CRIPTOGRAFICA"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full h-12 bg-white/5 border border-white/10 px-10 text-[11px] font-mono text-white placeholder:text-muted-foreground/30 focus:border-violet-500/50 focus:bg-white/10 outline-none transition-all"
                />
              </div>
            </div>

            <AnimatePresence>
              {(error || auth?.message) && (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="p-3 bg-red-500/5 border border-red-500/20 text-red-400 text-[9px] font-bold uppercase tracking-widest text-center"
                >
                  {error || auth?.message}
                </motion.div>
              )}
            </AnimatePresence>

            <button
              type="submit"
              disabled={loading}
              className="group relative w-full h-14 bg-white text-black font-black text-xs uppercase overflow-hidden hover:bg-[#adff2f] transition-all duration-300 active:scale-[0.97]"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:animate-shimmer" />
              {loading ? (
                  <Loader2 className="w-5 h-5 animate-spin mx-auto" />
              ) : (
                <div className="flex items-center justify-center gap-2">
                  <span>{mode === 'login' ? 'INICIAR_PROCESSO' : 'FINALIZAR_SYNC'}</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </div>
              )}
            </button>
          </form>

          <footer className="text-center">
            <button
              onClick={() => setMode(mode === "login" ? "signup" : "login")}
              className="text-[9px] font-mono text-muted-foreground hover:text-white transition-colors uppercase tracking-widest"
            >
              {mode === "login" ? "REGISTRAR_NOVO_NÓ" : "VOLTAR_AO_LOGIN"}
            </button>
          </footer>
        </div>

        {/* Footer info panel */}
        <div className="mt-8 px-2 flex justify-between items-center opacity-25">
          <div className="flex items-center gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-toxic animate-pulse" />
            <span className="text-[8px] font-mono uppercase tracking-tighter">SECURE_TUNNEL_ESTABLISHED</span>
          </div>
          <span className="text-[8px] font-mono uppercase tracking-tighter">BUILD_V4.2.0RC</span>
        </div>
      </motion.div>
    </div>
  );
}
