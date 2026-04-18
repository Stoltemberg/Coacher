"use client";

import { useBridge } from "@/contexts/BridgeContext";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mail, Lock, User, AtSign, Loader2, ArrowRight } from "lucide-react";

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
    } catch (err) {
      setError("FALHA NA CONEXÃO NEURAL");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-6 bg-background relative overflow-hidden">
      {/* Background elements */}
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-violet-500 to-transparent opacity-20" />
      <div className="absolute bottom-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-toxic to-transparent opacity-20" />

      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md z-10"
      >
        <div className="brutalist-border bg-black/60 backdrop-blur-xl p-10 space-y-8">
          <header className="text-center space-y-2">
            <h2 className="text-4xl font-black italic tracking-tighter uppercase whitespace-nowrap">
              {mode === 'login' ? 'Neural_Access' : 'Neural_Enrollment'}
            </h2>
            <p className="text-[10px] font-mono tracking-[0.4em] text-muted-foreground uppercase">
              {mode === 'login' ? 'INSIRA SUAS CREDENCIAIS DE ELITE' : 'INICIE SEU PROTOCOLO DE TREINAMENTO'}
            </p>
          </header>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
              {mode === "signup" && (
                <div className="relative group">
                  <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-focus-within:text-violet-400 transition-colors" />
                  <input
                    type="text"
                    placeholder="NOME_DE_USUÁRIO"
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    required
                    className="w-full h-14 bg-white/5 border border-border px-12 text-sm font-mono focus:border-violet-500 focus:bg-white/10 outline-none transition-all"
                  />
                </div>
              )}

              <div className="relative group">
                <AtSign className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-focus-within:text-violet-400 transition-colors" />
                <input
                  type="email"
                  placeholder="EMAIL_DE_CONTATO"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full h-14 bg-white/5 border border-border px-12 text-sm font-mono focus:border-violet-500 focus:bg-white/10 outline-none transition-all"
                />
              </div>

              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-focus-within:text-violet-400 transition-colors" />
                <input
                  type="password"
                  placeholder="CHAVE_DE_ACESSO"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full h-14 bg-white/5 border border-border px-12 text-sm font-mono focus:border-violet-500 focus:bg-white/10 outline-none transition-all"
                />
              </div>
            </div>

            <AnimatePresence>
              {(error || auth?.message) && (
                <motion.div 
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  className="p-3 bg-red-500/10 border border-red-500/30 text-red-500 text-[10px] font-black uppercase tracking-widest text-center"
                >
                  {error || auth?.message}
                </motion.div>
              )}
            </AnimatePresence>

            <button
              type="submit"
              disabled={loading}
              className="group relative w-full h-16 bg-white text-black font-black uppercase overflow-hidden hover:bg-toxic transition-colors"
            >
              {loading ? (
                  <Loader2 className="w-6 h-6 animate-spin mx-auto" />
              ) : (
                <div className="flex items-center justify-center gap-3">
                  <span>{mode === 'login' ? 'ENTRAR NO RIFT' : 'CRIAR CONTA'}</span>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </div>
              )}
            </button>
          </form>

          <footer className="text-center pt-4">
            <button
              onClick={() => setMode(mode === "login" ? "signup" : "login")}
              className="text-[10px] font-black uppercase text-muted-foreground hover:text-white transition-colors"
            >
              {mode === "login" ? "PRECISA DE UM NOVO PROTOCOLO?" : "JÁ POSSUI ACESSO NEURAL?"}
            </button>
          </footer>
        </div>

        {/* Decorative elements */}
        <div className="mt-8 flex justify-between items-center opacity-20 grayscale scale-75">
          <span className="text-[10px] font-mono whitespace-nowrap">COACHER_SECURE_V4.8</span>
          <div className="h-px bg-white flex-1 mx-4" />
          <span className="text-[10px] font-mono whitespace-nowrap">ENCRYPTION_ACTIVE</span>
        </div>
      </motion.div>
    </div>
  );
}
