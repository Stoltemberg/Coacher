"use client";

import { motion, useScroll, useVelocity, useTransform, useSpring, useReducedMotion } from "framer-motion";
import { useEffect, useState } from "react";

export default function LiquidContent({ children }: { children: React.ReactNode }) {
  const { scrollYProgress } = useScroll();
  const scrollVelocity = useVelocity(scrollYProgress);
  const shouldReduceMotion = useReducedMotion();
  
  // Transform velocity into distortion scale
  // Faster scroll = more distortion
  const distortionScale = useTransform(
    scrollVelocity,
    [-1, -0.1, 0, 0.1, 1],
    [30, 5, 0, 5, 30]
  );

  // Smooth out the scale
  const smoothScale = useSpring(distortionScale, {
    damping: 30,
    stiffness: 200
  });

  const [isMobile, setIsMobile] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    const frame = requestAnimationFrame(() => setIsMounted(true));
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
    };
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("resize", checkMobile);
    };
  }, []);

  if (!isMounted) return <>{children}</>;

  if (isMobile) {
    return <div className="relative overflow-x-hidden">{children}</div>;
  }

  return (
    <>
      {/* Displacement Filter Definition */}
      <svg className="hidden">
        <defs>
          <filter id="liquid-distort">
            <feTurbulence 
              type="fractalNoise" 
              baseFrequency="0.01 0.1" 
              numOctaves="1" 
              result="noise" 
            />
            <motion.feDisplacementMap 
              in="SourceGraphic" 
              in2="noise" 
              scale={shouldReduceMotion ? 0 : smoothScale} 
              xChannelSelector="R" 
              yChannelSelector="G" 
            />
          </filter>
        </defs>
      </svg>

      <motion.div 
        style={{ filter: "url(#liquid-distort)" }}
        className="will-change-transform"
      >
        {children}
      </motion.div>
    </>
  );
}
