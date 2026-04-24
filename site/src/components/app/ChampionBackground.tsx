"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useMemo } from "react";

interface ChampionBackgroundProps {
  championName: string | null;
}

// Map of display names (from API) to DDragon internal IDs
const CHAMPION_ID_MAP: Record<string, string> = {
  "Wukong": "MonkeyKing",
  "LeBlanc": "Leblanc",
  "Cho'Gath": "Chogath",
  "Kai'Sa": "Kaisa",
  "Kha'Zix": "Khazix",
  "Vel'Koz": "Velkoz",
  "Bel'Veth": "Belveth",
  "Dr. Mundo": "DrMundo",
  "Miss Fortune": "MissFortune",
  "Master Yi": "MasterYi",
  "Tahm Kench": "TahmKench",
  "Lee Sin": "LeeSin",
  "Xin Zhao": "XinZhao",
  "Nunu & Willump": "Nunu",
  "Renata Glasc": "Renata",
  "Jarvan IV": "JarvanIV",
  "Aurelion Sol": "AurelionSol",
  "Rek'Sai": "Reksai"
};

export default function ChampionBackground({ championName }: ChampionBackgroundProps) {
  const imageUrl = useMemo(() => {
    if (!championName || championName === "Alguém") return null;
    
    // 1. Check mapping
    if (CHAMPION_ID_MAP[championName]) {
      return `https://ddragon.leagueoflegends.com/cdn/img/champion/splash/${CHAMPION_ID_MAP[championName]}_0.jpg`;
    }

    // 2. Generic normalization for others
    // Data Dragon is case-sensitive, usually starts with uppercase
    let normalized = championName
      .replace(/[^a-zA-Z]/g, "")
      .replace(/\s/g, "");
    
    // Capitalize first letter just in case
    if (normalized.length > 0) {
      normalized = normalized.charAt(0).toUpperCase() + normalized.slice(1);
    }
      
    return `https://ddragon.leagueoflegends.com/cdn/img/champion/splash/${normalized}_0.jpg`;
  }, [championName]);

  return (
    <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
      <AnimatePresence mode="wait">
        {imageUrl ? (
          <motion.div
            key={imageUrl}
            initial={{ opacity: 0, scale: 1.05 }}
            animate={{ opacity: 0.4, scale: 1 }} // Increased opacity from 0.25 to 0.4
            exit={{ opacity: 0 }}
            transition={{ duration: 1.2, ease: "easeOut" }}
            className="w-full h-full relative"
          >
            {/* The Image - Slightly more contrast and less grayscale than before for visibility */}
            <div 
              className="absolute inset-0 bg-cover bg-center grayscale-[0.6] contrast-[1.1]"
              style={{ backgroundImage: `url(${imageUrl})` }}
            />
            
            {/* Brutalist Overlays - Adjusted for better visibility */}
            <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-black opacity-40" />
            <div className="absolute inset-0 bg-black/20 backdrop-blur-[1px]" />
            
            {/* Industrial Scanline Effect */}
            <div className="absolute inset-0 opacity-[0.05] pointer-events-none bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_2px,3px_100%]" />
          </motion.div>
        ) : (
          <motion.div 
            key="empty"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="w-full h-full bg-transparent transition-colors duration-1000 flex items-center justify-center"
          >
            {/* Fallback Neural Grid Pattern */}
            <div className="absolute inset-0 opacity-[0.03] bg-[linear-gradient(to_right,#adff2f_1px,transparent_1px),linear-gradient(to_bottom,#adff2f_1px,transparent_1px)] bg-[size:40px_40px]" />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
