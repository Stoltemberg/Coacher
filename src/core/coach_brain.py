import time
import threading

from core.minerva_voice import MinervaVoice
from core.player_memory import PlayerMemory

class CoachBrain:
    def __init__(self, assistant, voice=None):
        self.assistant = assistant
        self.voice = voice or MinervaVoice()
        self.memory = PlayerMemory(intensity=self.voice.intensity)
        self.hardcore_enabled = True
        self.objectives_enabled = True
        self.coaching_active = False
        self.current_phase = "lobby"
        self.current_champion_name = None
        self.summary_callback = None
        self.memory_callback = None
        self.match_started = False
        self.match_finalized = False
        self.last_summary = None

        self.armor_ids = [3075, 3143, 3110, 6660, 3068, 6665, 3193, 3026]
        self.mr_ids = [3065, 4401, 3155, 3156, 3001, 3118]
        self.anti_heal_ids = [3123, 3033, 3165, 3916, 6609, 3076, 3075]

        self.category_cooldowns = {
            "macro": 90,
            "minimap": 75,
            "identity": 20,
            "assist": 10,
            "lane_matchup": 45,
            "farm_eval": 120,
            "vision_eval": 120,
            "item_advice": 45,
            "self_kill": 8,
            "self_death": 8,
            "ally_death": 6,
            "enemy_death": 6,
            "first_blood": 20,
            "multikill": 15,
            "dragon": 20,
            "baron": 20,
            "herald": 20,
            "horde": 20,
            "turret": 12,
            "inhibitor": 20,
        }

        self.reset()

        self.timer_thread = threading.Thread(target=self._minimap_timer, daemon=True)
        self.timer_thread.start()
        
        self.macro_thread = threading.Thread(target=self._macro_timer, daemon=True)
        self.macro_thread.start()

    def reset(self):
        self.match_started = False
        self.match_finalized = False
        self.last_summary = None
        self.active_player_name = None
        self.player_to_champ = {} 
        self.player_to_team = {}
        self.our_team = "ORDER"
        
        self.game_time = 0.0
        self.current_assists = -1
        self.last_farm_eval = 0
        self.lane_matchup_announced = False
        self.my_position = ""
        
        self.ally_drags = 0
        self.enemy_drags = 0

        self.last_item_check = 0
        self.advised_items = set()
        self.last_announced_at = {}
        self.current_champion_name = None

    def activate_match(self):
        self.coaching_active = True

    def deactivate_match(self):
        self.coaching_active = False

    def set_phase(self, phase):
        self.current_phase = (phase or "unknown").lower()

    def set_summary_callback(self, callback):
        self.summary_callback = callback

    def set_memory_callback(self, callback):
        self.memory_callback = callback

    def set_intensity(self, intensity):
        self.voice.set_intensity(intensity)
        self.memory.set_intensity(intensity)

    def start_match_memory(self):
        self.match_started = True
        self.match_finalized = False
        self.last_summary = None
        self.memory.set_intensity(self.voice.intensity)
        self.memory.start_match(
            player_name=self.active_player_name,
            champion_name=self.current_champion_name,
            role=self.my_position,
            context={"phase": self.current_phase},
        )

    def finalize_match(self, result="completed"):
        if self.match_finalized:
            return self.last_summary

        self.match_finalized = True

        self.memory.current_match.player_name = self.active_player_name or self.memory.current_match.player_name
        self.memory.current_match.champion_name = self.current_champion_name or self.memory.current_match.champion_name
        self.memory.current_match.role = self.my_position or self.memory.current_match.role
        summary = self.memory.end_match(result=result)
        self.last_summary = summary
        self.match_started = False
        if self.summary_callback:
            self.summary_callback(summary)
        return summary

    def _push_memory_entry(self, title, note, tone="normal"):
        if self.memory_callback:
            self.memory_callback(
                {
                    "title": title,
                    "note": note,
                    "tone": tone,
                }
            )

    def _announce(self, text, event_type="neutral", category=None):
        if category:
            now = time.monotonic()
            cooldown = self.category_cooldowns.get(category, 0)
            last_time = self.last_announced_at.get(category, 0)
            if now - last_time < cooldown:
                return
            self.last_announced_at[category] = now
        if text:
            if self.coaching_active and category:
                self.memory.record_event(
                    "call",
                    text,
                    phase=self.current_phase,
                    category=category,
                    severity=event_type,
                    importance=0.75 if event_type in {"positive", "negative"} else 0.55,
                    tags=[category, self.current_phase],
                )
            self.assistant.say(text, event_type, category=category)

    def _announce_objective(self, text, event_type="neutral", category=None):
        if self.objectives_enabled:
            self._announce(text, event_type, category=category)

    def map_pve_name(self, raw_killer):
        lk = raw_killer.lower()
        if "turret" in lk or "torder" in lk:
            return "uma Torre"
        if "minion" in lk:
            return "uma Tropa"
        if "sru_" in lk:
            return "os Monstros da Selva"
        return "o cenário"

    def _macro_timer(self):
        while True:
            time.sleep(200)
            if self.coaching_active and self.active_player_name:
                self._announce(self.voice.macro_reminder(), category="macro")

    def _minimap_timer(self):
        while True:
            time.sleep(150)
            if self.coaching_active and self.active_player_name:
                self._announce(self.voice.minimap_reminder(), category="minimap")

    def update_active_player(self, data):
        if "summonerName" in data and not self.active_player_name:
            raw_name = data["summonerName"]
            self.active_player_name = raw_name.split('#')[0].strip()
            self.memory.player_name = self.active_player_name
            self.memory.current_match.player_name = self.active_player_name
            self._announce(self.voice.player_identified(), category="identity")

    def update_game_stats(self, data):
        self.game_time = data.get("gameTime", 0.0)
        if self.coaching_active:
            if self.game_time < 840:
                self.current_phase = "lane"
            elif self.game_time < 1680:
                self.current_phase = "mid_game"
            else:
                self.current_phase = "late_game"

    def update_players(self, players_data):
        if not self.active_player_name:
            return

        for p in players_data:
            s_name = p.get("summonerName", "").split('#')[0].strip()
            champ = p.get("championName", "Alguém")
            p_team = p.get("team", "ORDER")
            
            self.player_to_champ[s_name] = champ
            self.player_to_team[s_name] = p_team
            
            if s_name == self.active_player_name:
                self.our_team = p_team
                self.my_position = p.get("position", "")
                self.current_champion_name = champ
                self.memory.champion_name = champ
                self.memory.role = self.my_position
                self.memory.current_match.player_name = self.active_player_name
                self.memory.current_match.champion_name = champ
                self.memory.current_match.role = self.my_position
                
                scores = p.get("scores", {})
                assists = scores.get("assists", 0)
                cs = scores.get("creepScore", 0)
                wards = scores.get("wardScore", 0.0)
                
                if self.current_assists == -1:
                    self.current_assists = assists
                elif assists > self.current_assists:
                    self.current_assists = assists
                    self._announce(self.voice.assist(), "positive", category="assist")

                minutes = self.game_time / 60.0
                
                # Matchup Call no primeiro minuto ou segundo
                if not self.lane_matchup_announced and self.game_time > 80 and self.my_position and self.my_position != "NONE":
                    for e in players_data:
                        if e.get("team") != self.our_team and e.get("position") == self.my_position:
                            enemy_nick = e.get("summonerName", "").split('#')[0].strip()
                            self._announce(self.voice.lane_matchup(enemy_nick), "neutral", category="lane_matchup")
                            self.lane_matchup_announced = True

                # Farm / Vision Evaluation a cada 5 Minutos (Apenas no Modo Hardcore)
                if self.hardcore_enabled and self.game_time > 300 and (self.game_time - self.last_farm_eval) > 300:
                    self.last_farm_eval = self.game_time
                    expected_cs = minutes * 6.5
                    
                    if cs < (expected_cs * 0.6):
                        self._announce(self.voice.low_farm(cs, minutes), "negative", category="farm_eval")
                        self.memory.record_evaluation(
                            "farm",
                            0.25,
                            note=f"Farm abaixo do ideal: {cs} CS aos {int(minutes)} minutos.",
                            phase=self.current_phase,
                            category="economy",
                            actual=cs,
                            expected=round(expected_cs, 1),
                            severity="negative",
                        )
                        self._push_memory_entry("Farm abaixo do ideal", f"{cs} CS aos {int(minutes)} min. O coach quer mais disciplina de wave.", "negative")
                    elif cs > expected_cs:
                        self._announce(self.voice.high_farm(cs, minutes), "positive", category="farm_eval")
                        self.memory.record_evaluation(
                            "farm",
                            0.82,
                            note=f"Farm forte: {cs} CS aos {int(minutes)} minutos.",
                            phase=self.current_phase,
                            category="economy",
                            actual=cs,
                            expected=round(expected_cs, 1),
                            severity="positive",
                        )
                        self._push_memory_entry("Farm consistente", f"{cs} CS aos {int(minutes)} min. Boa conversão de recurso.", "positive")
                    
                    # Vision Check pros avançados
                    if minutes >= 10 and wards < 5:
                        self._announce(self.voice.low_vision(wards), "negative", category="vision_eval")
                        self.memory.record_evaluation(
                            "vision",
                            0.22,
                            note=f"Visão fraca com {wards} de ward score aos {int(minutes)} minutos.",
                            phase=self.current_phase,
                            category="macro",
                            actual=wards,
                            target="Comprar controle e preparar entradas antes do rio.",
                            severity="negative",
                        )
                        self._push_memory_entry("Visão fraca", f"{wards} de visão até agora. O mapa ficou mais cego do que devia.", "negative")
        
        current_time = time.time()
        if current_time - self.last_item_check > 20: 
            self.last_item_check = current_time
            
            for p in players_data:
                s_name = p.get("summonerName", "").split('#')[0].strip()
                if p.get("team") != self.our_team:
                    items = [item.get("itemID", 0) for item in p.get("items", [])]
                    p_nick = p.get("summonerName", "").split('#')[0].strip()
                    
                    has_armor = any(i in self.armor_ids for i in items)
                    has_mr = any(i in self.mr_ids for i in items)
                    has_anti_heal = any(i in self.anti_heal_ids for i in items)
                    
                    if has_armor and "armor_pen" not in self.advised_items:
                        self._announce(self.voice.armor_warning(p_nick), "negative", category="item_advice")
                        self.memory.record_evaluation(
                            "itemization",
                            0.35,
                            note=f"Adaptação de build necessária contra armadura de {p_nick}.",
                            phase=self.current_phase,
                            category="economy",
                            target="Comprar penetração física no próximo reset.",
                            severity="negative",
                        )
                        self._push_memory_entry("Loja atrasada", f"{p_nick} já tem armadura pesada e a build precisa responder.", "negative")
                        self.advised_items.add("armor_pen")
                        return
                        
                    if has_mr and "magic_pen" not in self.advised_items:
                        self._announce(self.voice.magic_resist_warning(p_nick), "negative", category="item_advice")
                        self.memory.record_evaluation(
                            "itemization",
                            0.35,
                            note=f"Adaptação AP necessária contra resistência mágica de {p_nick}.",
                            phase=self.current_phase,
                            category="economy",
                            target="Preparar penetração mágica no próximo reset.",
                            severity="negative",
                        )
                        self._push_memory_entry("Resposta mágica atrasada", f"{p_nick} segurou tua curva de dano com MR.", "negative")
                        self.advised_items.add("magic_pen")
                        return

                    if has_anti_heal and "anti_heal" not in self.advised_items:
                        self._announce(self.voice.anti_heal_warning(p_nick), "negative", category="item_advice")
                        self.memory.record_evaluation(
                            "survivability",
                            0.4,
                            note=f"O inimigo {p_nick} comprou corta-cura e mudou as janelas de sustain.",
                            phase=self.current_phase,
                            category="recovery",
                            target="Respeitar trocas longas e revisar timing de entrada.",
                            severity="negative",
                        )
                        self._push_memory_entry("Sustain punido", f"{p_nick} comprou corta-cura. Troca longa ficou mais arriscada.", "negative")
                        self.advised_items.add("anti_heal")
                        return

    def process_event(self, event):
        name = event.get("EventName")
        
        if name == "ChampionKill":
            killer = event.get("KillerName", "").split('#')[0].strip()
            victim = event.get("VictimName", "").split('#')[0].strip()

            if killer == self.active_player_name:
                self._announce(self.voice.self_kill(victim), "positive", category="self_kill")
            elif victim == self.active_player_name:
                if not killer or killer not in self.player_to_champ:
                    self._announce(self.voice.self_death_pve(), "negative", category="self_death")
                else:
                    self._announce(self.voice.self_death_enemy(killer), "negative", category="self_death")
            elif killer and victim:
                is_victim_ally = self.player_to_team.get(victim) == self.our_team

                if killer not in self.player_to_champ:
                    pve = self.map_pve_name(killer)
                    if is_victim_ally:
                        self._announce(self.voice.ally_pve_death(victim, pve), "negative", category="ally_death")
                    else:
                        self._announce(self.voice.enemy_pve_death(victim, pve), "positive", category="enemy_death")
                else:
                    if is_victim_ally:
                        self._announce(self.voice.ally_death(victim, killer), "negative", category="ally_death")
                    else:
                        self._announce(self.voice.enemy_death(killer, victim), "positive", category="enemy_death")
                        
        elif name == "FirstBlood":
             self._announce(self.voice.first_blood(), "positive", category="first_blood")
                
        elif name == "Multikill":
            killer = event.get("KillerName", "").split('#')[0].strip()
            kill_streak = event.get("KillStreak", 2)
            
            if killer == self.active_player_name:
                self._announce(self.voice.self_multikill(kill_streak), "positive", category="multikill")
            elif kill_streak >= 2:
                self._announce(self.voice.enemy_multikill(killer, kill_streak), "negative", category="multikill")

        elif name == "DragonKill":
            if not self.objectives_enabled:
                return

            killer = event.get("KillerName", "").split('#')[0].strip()
            raw_dragon = event.get("DragonType", "Dragão").replace("Dragon", "")
            
            dragon_map = {
                "Fire": "Infernal", "Earth": "da Montanha", "Water": "do Oceano", 
                "Air": "das Nuvens", "Hextech": "Hextec", "Chemtech": "Quimtec", "Elder": "Ancião"
            }
            dragon_pt = dragon_map.get(raw_dragon, raw_dragon)
            
            team = self.player_to_team.get(killer, "UNKNOWN")
            is_ally = (team == self.our_team)
            
            if is_ally:
                self.ally_drags += 1
                drags = self.ally_drags
            else:
                self.enemy_drags += 1
                drags = self.enemy_drags
            
            if dragon_pt == "Ancião":
                self._announce_objective(self.voice.elder_dragon(is_ally), "positive" if is_ally else "negative", category="dragon")
            else:
                event_type = "positive" if is_ally else "negative"
                self._announce_objective(self.voice.dragon_control(dragon_pt, is_ally, drags, killer), event_type, category="dragon")
            
        elif name == "BaronKill":
             if not self.objectives_enabled:
                 return

             killer = event.get("KillerName", "").split('#')[0].strip()
             is_ally = self.player_to_team.get(killer) == self.our_team
             self._announce_objective(self.voice.baron_taken(killer, is_ally), "positive" if is_ally else "negative", category="baron")
              
        elif name == "HordeKill":
            if not self.objectives_enabled:
                return

            killer = event.get("KillerName", "").split('#')[0].strip()
            is_ally = self.player_to_team.get(killer) == self.our_team
            self._announce_objective(self.voice.horde_taken(killer, is_ally), "positive" if is_ally else "negative", category="horde")
            
        elif name == "HeraldKill":
            if not self.objectives_enabled:
                return

            killer = event.get("KillerName", "").split('#')[0].strip()
            is_ally = self.player_to_team.get(killer) == self.our_team
            self._announce_objective(self.voice.herald_taken(killer, is_ally), "positive" if is_ally else "negative", category="herald")
            
        elif name == "TurretKilled":
            killer = event.get("KillerName", "").split('#')[0].strip()
            
            if killer and "Turret" not in killer and "Minion" not in killer:
                is_ally = self.player_to_team.get(killer) == self.our_team
                self._announce(self.voice.turret_taken(killer, is_ally), "positive" if is_ally else "negative", category="turret")
            else:
                self._announce(self.voice.neutral_turret_taken(), "negative", category="turret")

        elif name == "InhibKilled":
            killer = event.get("KillerName", "").split('#')[0].strip()
            is_ally = self.player_to_team.get(killer) == self.our_team
            self._announce(self.voice.inhibitor_taken(killer, is_ally), "positive" if is_ally else "negative", category="inhibitor")
