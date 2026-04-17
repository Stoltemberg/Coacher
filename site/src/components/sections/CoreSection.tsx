"use client";

import Image from "next/image";
import { useEffect, useRef } from "react";
import anime from "animejs";

export default function CoreSection() {
  const imgRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!imgRef.current) return;

    // Gentle float animation for the core
    anime({
      targets: imgRef.current,
      translateY: [-10, 10],
      rotateZ: [-2, 2],
      duration: 3000,
      direction: "alternate",
      loop: true,
      easing: "easeInOutSine",
    });
  }, []);

  return (
    <section className="py-32 px-6 overflow-hidden">
      <div className="max-w-7xl mx-auto grid md:grid-cols-2 gap-16 items-center">
        <div ref={imgRef} className="relative aspect-square max-w-md mx-auto">
          <div className="absolute inset-0 bg-accent/20 blur-[100px] rounded-full" />
          <Image 
            src="/minerva_brain.png" 
            alt="Minerva AI Core" 
            fill 
            sizes="(max-width: 768px) 100vw, 500px"
            className="object-contain drop-shadow-[0_0_50px_rgba(139,92,246,0.5)]"
          />
        </div>
        
        <div className="space-y-8">
          <div className="inline-block py-1 px-3 border border-accent/30 bg-accent/5 text-accent text-xs font-mono uppercase tracking-widest">
            // ANALYTICS_CORE_ACTIVE
          </div>
          <h2 className="text-5xl md:text-7xl">Performance Pura.</h2>
          <p className="text-xl text-muted-foreground leading-relaxed">
            O Coacher é um ecossistema de dados persistentes que analisa sua mecânica, 
            identifica padrões de eficiência e otimiza sua tomada de decisão com precisão sub-milimétrica.
          </p>
          
          <ul className="space-y-4 font-mono text-sm">
            <li className="flex items-center gap-3 italic">
              <span className="w-2 h-2 bg-accent rounded-full" />
              VOZ MINERVA_ENGINE v4 [INTERAÇÃO HUMANA]
            </li>
            <li className="flex items-center gap-3">
              <span className="w-2 h-2 bg-border rounded-full" />
              INTEGRAÇÃO LCU DE BAIXA LATÊNCIA
            </li>
            <li className="flex items-center gap-3">
              <span className="w-2 h-2 bg-border rounded-full" />
              RECONHECIMENTO DE PADRÕES COGNITIVOS
            </li>
          </ul>
        </div>
      </div>
    </section>
  );
}
