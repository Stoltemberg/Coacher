import { Target, Zap, Waves, BrainCircuit, Activity, ShieldAlert } from "lucide-react";
import { motion } from "framer-motion";

const features = [
  {
    title: "Dominância no Draft",
    desc: "Análise de pick/ban em tempo real usando dados de 8.000.000 de partidas.",
    icon: <Target className="w-8 h-8 text-accent" />,
    className: "md:col-span-2 md:row-span-1",
  },
  {
    title: "Coaching em Tempo Real",
    desc: "Feedback por voz durante o jogo. Posicionamento, trocas e macro.",
    icon: <Zap className="w-8 h-8 text-toxic" />,
    className: "md:col-span-1 md:row-span-1",
  },
  {
    title: "Pulso Econômico",
    desc: "Rastreia o 'gold rubber-banding' inimigo e picos de poder de itens.",
    icon: <Activity className="w-8 h-8 text-muted-foreground" />,
    className: "md:col-span-1 md:row-span-1",
  },
  {
    title: "Memória Persistente",
    desc: "O Coacher armazena cada interação para construir um perfil de evolução constante do jogador.",
    icon: <BrainCircuit className="w-8 h-8 text-white" />,
    className: "md:col-span-2 md:row-span-2 bg-accent/10 border-accent/20",
  },
  {
    title: "Objetivos de Mapa",
    desc: "Timers preditivos de dragão/barão baseados em fragmentos de visão.",
    icon: <Waves className="w-8 h-8 text-accent" />,
    className: "md:col-span-1 md:row-span-1",
  },
  {
    title: "Escudo de Pânico",
    desc: "Estratégias de recuperação in-game para quando você estiver 0/5 aos 10 minutos.",
    icon: <ShieldAlert className="w-8 h-8 text-red-500" />,
    className: "md:col-span-1 md:row-span-1",
  },
];

export default function BentoFeatures() {
  return (
    <section className="py-32 px-6 overflow-hidden">
      <div className="max-w-7xl mx-auto">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="flex flex-col md:flex-row justify-between items-start md:items-end mb-16 gap-8"
        >
          <h2 className="text-4xl md:text-6xl max-w-xl font-black uppercase">Construído para a Elite.</h2>
          <p className="text-muted-foreground font-mono text-sm max-w-sm uppercase tracking-widest">
            [01] A MAIS AVANÇADA SUÍTE DE ANÁLISE JÁ CONSTRUÍDA PARA O RIFT.
          </p>
        </motion.div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {features.map((f, i) => (
            <motion.div 
              key={i} 
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: i * 0.1 }}
              viewport={{ once: true, margin: "-100px" }}
              className={`p-8 brutalist-border bg-muted/30 flex flex-col justify-between gap-12 ${f.className}`}
            >
              <div className="flex justify-between items-start">
                {f.icon}
                <span className="text-[10px] font-mono text-muted-foreground">00{i+1}</span>
              </div>
              <div>
                <h3 className="text-2xl mb-2">{f.title}</h3>
                <p className="text-sm text-muted-foreground">{f.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
