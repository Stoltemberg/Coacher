import time
import threading

from core.adaptive_tracker import AdaptiveTracker, resolve_adaptive_topic
from core.coach_state import CoachSettings, MatchState, map_call_category
from core.coach_analyzer import build_enemy_team_names, find_lane_enemy
from core.coach_service import CoachService
from core.jungle_tracker import JungleTracker
from core.match_analyzer import determine_phase
from core.minerva_voice import MinervaVoice
from core.player_memory import PlayerMemory

class CoachBrain:
    def __init__(self, assistant, voice=None, knowledge=None, coach_service=None):
        self.assistant = assistant
        self.voice = voice or MinervaVoice()
        self.knowledge = knowledge
        self.coach_service = coach_service or CoachService(knowledge)
        self.memory = PlayerMemory(intensity=self.voice.intensity)
        self.settings = CoachSettings(
            voice_enabled=True,
            objectives_enabled=True,
            intensity=self.voice.intensity,
            voice_preset="hardcore" if self.voice.intensity == "hardcore" else "standard",
        )
        self.state = MatchState()
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
        self.jungle_tracker = JungleTracker()
        self.last_jungle_snapshot = None
        self.adaptive_tracker = AdaptiveTracker()
        self.history_profile = {}
        self.coach_mode = "draft"
        self.mode_callback = None

        self.armor_ids = [3075, 3143, 3110, 6660, 3068, 6665, 3193, 3026]
        self.mr_ids = [3065, 4401, 3155, 3156, 3001, 3118]
        self.anti_heal_ids = [3123, 3033, 3165, 3916, 6609, 3076, 3075]

        self.category_cooldowns = {
            "macro": self.settings.macro_interval,
            "minimap": self.settings.minimap_interval,
            "identity": 20,
            "assist": 10,
            "lane_matchup": 45,
            "build_plan": 90,
            "power_spike": 120,
            "opening_plan": 90,
            "mid_game_job": 180,
            "jungle_intel": 50,
            "farm_eval": self.settings.economy_interval,
            "vision_eval": self.settings.economy_interval,
            "item_advice": self.settings.item_check_interval,
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
            "adaptive_feedback": 70,
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
        self.player_to_role = {}
        self.our_team = "ORDER"
        
        self.game_time = 0.0
        self.current_assists = -1
        self.last_farm_eval = 0
        self.lane_matchup_announced = False
        self.detailed_matchup_announced = False
        self.early_build_plan_announced = False
        self.opening_plan_announced = False
        self.mid_game_job_announced = False
        self.my_position = ""
        
        self.ally_drags = 0
        self.enemy_drags = 0

        self.last_item_check = 0
        self.advised_items = set()
        self.last_announced_at = {}
        self.current_champion_name = None
        self.jungle_tracker.reset()
        self.last_jungle_snapshot = None
        self.adaptive_tracker.reset()
        self.history_profile = {}
        self.history_focus_announced = False
        self.coach_mode = "draft"
        self._sync_state()

    def _sync_state(self):
        self.state = MatchState(
            coaching_active=self.coaching_active,
            current_phase=self.current_phase,
            coach_mode=self.coach_mode,
            active_player_name=self.active_player_name,
            current_champion_name=self.current_champion_name,
            our_team=self.our_team,
            my_position=self.my_position,
            game_time=self.game_time,
            current_assists=self.current_assists,
            last_farm_eval=self.last_farm_eval,
            lane_matchup_announced=self.lane_matchup_announced,
            detailed_matchup_announced=self.detailed_matchup_announced,
            early_build_plan_announced=self.early_build_plan_announced,
            opening_plan_announced=self.opening_plan_announced,
            mid_game_job_announced=self.mid_game_job_announced,
            ally_drags=self.ally_drags,
            enemy_drags=self.enemy_drags,
            match_started=self.match_started,
            match_finalized=self.match_finalized,
            last_summary=self.last_summary,
            last_item_check=self.last_item_check,
            player_to_champ=dict(self.player_to_champ),
            player_to_team=dict(self.player_to_team),
            player_to_role=dict(self.player_to_role),
            advised_items=set(self.advised_items),
            last_announced_at=dict(self.last_announced_at),
        )

    def activate_match(self):
        self.coaching_active = True
        self._refresh_coach_mode()
        self._sync_state()

    def deactivate_match(self):
        self.coaching_active = False
        self._refresh_coach_mode()
        self._sync_state()

    def set_phase(self, phase):
        self.current_phase = (phase or "unknown").lower()
        self._refresh_coach_mode()
        self._sync_state()

    def set_summary_callback(self, callback):
        self.summary_callback = callback

    def set_memory_callback(self, callback):
        self.memory_callback = callback

    def set_mode_callback(self, callback):
        self.mode_callback = callback

    def set_intensity(self, intensity):
        self.settings.intensity = intensity
        self.hardcore_enabled = intensity == "hardcore"
        self.voice.set_intensity(intensity)
        self.memory.set_intensity(intensity)

    def set_voice_preset(self, preset):
        self.settings.set_preset(preset)
        self.set_intensity(self.settings.intensity)

    def set_category_enabled(self, category, enabled):
        bucket = map_call_category(category) or str(category or "").strip().lower()
        if bucket:
            self.settings.category_filters[bucket] = bool(enabled)

    def get_settings_snapshot(self):
        return {
            "voice_preset": self.settings.voice_preset,
            "intensity": self.settings.intensity,
            "category_filters": dict(self.settings.category_filters),
            "objectives_enabled": self.objectives_enabled,
            "hardcore_enabled": self.hardcore_enabled,
            "coach_mode": self.coach_mode,
        }

    def _determine_coach_mode(self):
        phase = (self.current_phase or "").lower()
        if phase in {"lobby", "champ_select", "champselect"}:
            return "draft"

        tracker_snapshot = self.adaptive_tracker.snapshot()
        hot_negative = {
            topic
            for topic, trend in tracker_snapshot.items()
            if trend.get("negative_streak", 0) >= 2 or trend.get("recovery_pending")
        }

        if phase == "lane":
            if hot_negative & {"fight_discipline", "lane_control"}:
                return "recovery"
            if self.history_profile.get("primary_leak") in {"farm", "itemization"}:
                return "economy"
            return "lane"

        if phase in {"mid_game", "late_game"}:
            if hot_negative & {"objective_setup", "vision"}:
                return "macro"
            if hot_negative & {"fight_discipline", "itemization"}:
                return "recovery"
            if self.history_profile.get("primary_leak") in {"farm", "itemization"}:
                return "economy"
            return "macro"

        return "lane"

    def _refresh_coach_mode(self):
        next_mode = self._determine_coach_mode()
        if next_mode == self.coach_mode:
            return
        self.coach_mode = next_mode
        self._sync_state()
        if self.mode_callback:
            self.mode_callback(self.get_settings_snapshot())

    def start_match_memory(self):
        self.match_started = True
        self.match_finalized = False
        self.last_summary = None
        self.memory.set_intensity(self.voice.intensity)
        history_snapshot = self.memory.build_history_snapshot(limit_matches=8)
        self.history_profile = history_snapshot.get("adaptive_profile") or {}
        self._refresh_coach_mode()
        self.memory.start_match(
            player_name=self.active_player_name,
            champion_name=self.current_champion_name,
            role=self.my_position,
            context={
                "phase": self.current_phase,
                "history_adaptive_profile": dict(self.history_profile),
            },
        )
        self._sync_state()

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
        self._sync_state()
        return summary

    def _push_memory_entry(self, title, note, tone="normal", meta=None):
        if self.memory_callback:
            self.memory_callback(
                {
                    "title": title,
                    "note": note,
                    "tone": tone,
                    "meta": meta or "",
                }
            )

    def _history_call_overrides(self, category, event_type, importance=None, metadata=None):
        topic = resolve_adaptive_topic(category, event_type, metadata)
        base_importance = importance if importance is not None else (0.75 if event_type in {"positive", "negative"} else 0.55)
        next_event_type = event_type
        next_importance = base_importance
        next_metadata = {"game_time": self.game_time, **(metadata or {})}
        cooldown_scale = 1.0

        if topic and topic == self.history_profile.get("primary_leak"):
            next_metadata.setdefault("history_focus", "primary_leak")
            next_metadata.setdefault("adaptive_topic", topic)
            next_importance = min(1.0, next_importance + 0.12)
            cooldown_scale = 0.78
            if event_type == "neutral":
                next_event_type = "warning"
        elif topic and topic == self.history_profile.get("primary_fix"):
            next_metadata.setdefault("history_focus", "primary_fix")
            next_metadata.setdefault("adaptive_topic", topic)
            next_importance = min(1.0, next_importance + 0.08)
            cooldown_scale = 0.88
            if event_type == "neutral":
                next_event_type = "positive"

        bucket = map_call_category(category) or ""
        if self.coach_mode == "recovery":
            if bucket == "recovery" or topic in {"fight_discipline", "lane_control"}:
                next_importance = min(1.0, next_importance + 0.08)
                cooldown_scale *= 0.8
                next_metadata.setdefault("mode_focus", "recovery")
                if next_event_type == "neutral":
                    next_event_type = "warning"
            elif bucket == "lane" and next_event_type == "neutral":
                cooldown_scale *= 1.1
        elif self.coach_mode == "macro":
            if bucket in {"macro", "objective"} or topic in {"objective_setup", "vision"}:
                next_importance = min(1.0, next_importance + 0.08)
                cooldown_scale *= 0.82
                next_metadata.setdefault("mode_focus", "macro")
        elif self.coach_mode == "economy":
            if bucket == "economy" or topic in {"farm", "itemization"}:
                next_importance = min(1.0, next_importance + 0.08)
                cooldown_scale *= 0.82
                next_metadata.setdefault("mode_focus", "economy")
        elif self.coach_mode == "lane":
            if bucket == "lane" or topic == "lane_control":
                next_importance = min(1.0, next_importance + 0.06)
                cooldown_scale *= 0.9
                next_metadata.setdefault("mode_focus", "lane")

        return next_event_type, next_importance, next_metadata, cooldown_scale

    def _mode_allows_call(self, category, event_type, importance, metadata=None):
        if event_type in {"negative", "positive", "urgent", "warning"}:
            return True
        if importance is not None and importance >= 0.78:
            return True

        bucket = map_call_category(category) or ""
        if not bucket:
            return True

        if self.coach_mode == "recovery":
            return bucket in {"recovery", "objective"} or category == "adaptive_feedback"
        if self.coach_mode == "macro":
            return bucket in {"macro", "objective", "recovery"}
        if self.coach_mode == "economy":
            return bucket in {"economy", "objective", "recovery"}
        if self.coach_mode == "lane":
            return bucket in {"lane", "objective", "recovery", "economy"}
        return True

    def _announce(self, text, event_type="neutral", category=None, importance=None, metadata=None):
        if category and not self.settings.is_category_enabled(category):
            return
        effective_event_type, effective_importance, effective_metadata, cooldown_scale = self._history_call_overrides(
            category,
            event_type,
            importance=importance,
            metadata=metadata,
        )
        if not self._mode_allows_call(category, effective_event_type, effective_importance, effective_metadata):
            return
        if category:
            now = time.monotonic()
            # Dynamic cooldown lookup for core settings
            cooldown_val = self.category_cooldowns.get(category, 0)
            if category == "macro": cooldown_val = self.settings.macro_interval
            elif category == "minimap": cooldown_val = self.settings.minimap_interval
            elif category in {"farm_eval", "vision_eval"}: cooldown_val = self.settings.economy_interval
            elif category == "item_advice": cooldown_val = self.settings.item_check_interval
            
            cooldown = cooldown_val * cooldown_scale
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
                    severity=effective_event_type,
                    importance=effective_importance,
                    tags=[category, self.current_phase],
                    metadata=effective_metadata,
                )
            self.assistant.say(text, effective_event_type, category=category)

    def _announce_objective(self, text, event_type="neutral", category=None, importance=None, metadata=None):
        if self.objectives_enabled:
            self._announce(text, event_type, category=category, importance=importance, metadata=metadata)

    def _process_adaptive_signal(self, category, severity, metadata=None):
        if not self.coaching_active or category == "adaptive_feedback":
            return

        cue = self.adaptive_tracker.ingest(
            category=category,
            severity=severity,
            game_time=(metadata or {}).get("game_time", self.game_time),
            metadata=metadata,
        )
        if not cue:
            return
        self._refresh_coach_mode()

        cue_metadata = {
            "game_time": cue.game_time,
            "adaptive_topic": cue.topic,
            "adaptive_mode": cue.mode,
        }
        if cue.metadata:
            cue_metadata.update(cue.metadata)

        topic_label = self.voice._adaptive_topic_label(cue.topic)
        if cue.mode == "recovery":
            text = self.voice.adaptive_recovery(cue.topic, cue.streak)
            title = "Correcao detectada"
            note = f"O coach percebeu melhora em {topic_label} depois de repeticao ruim."
            tone = "positive"
            event_type = "positive"
        else:
            text = self.voice.adaptive_repetition(cue.topic, cue.streak)
            title = "Padrao ruim repetido"
            note = f"O mesmo problema em {topic_label} apareceu de novo e puxou cobranca adaptativa."
            tone = "negative"
            event_type = "negative"

        self._announce(
            text,
            event_type,
            category="adaptive_feedback",
            importance=0.83 if cue.mode == "recovery" else 0.9,
            metadata=cue_metadata,
        )
        self._push_memory_entry(title, note, tone, meta=topic_label)

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
            # Sleep based on setting, with a safety floor of 5s
            interval = max(5, self.settings.macro_interval)
            time.sleep(interval)
            if self.coaching_active and self.active_player_name:
                self._announce(self.voice.macro_reminder(), category="macro")

    def _minimap_timer(self):
        while True:
            # Sleep based on setting, with a safety floor of 5s
            interval = max(5, self.settings.minimap_interval)
            time.sleep(interval)
            if self.coaching_active and self.active_player_name:
                self._announce(self.voice.minimap_reminder(), category="minimap")

    def update_active_player(self, data):
        if "summonerName" in data and not self.active_player_name:
            raw_name = data["summonerName"]
            self.active_player_name = raw_name.split('#')[0].strip()
            self.memory.player_name = self.active_player_name
            self.memory.current_match.player_name = self.active_player_name
            self._announce(self.voice.player_identified(), category="identity")
            self._sync_state()

    def _get_counter_item_suggestion(self, need_type):
        """Sugere um item especifico baseado no campeao do jogador e na necessidade."""
        if not self.current_champion_name or not self.knowledge:
            return None
        
        champ = self.knowledge.get_champion(self.current_champion_name)
        if not champ:
            return None
            
        tags = set(champ.tags or [])
        archetype = getattr(champ, "archetype", "")
        
        is_ap = "Mage" in tags or archetype in {"control_mage", "burst_mage", "enchanter"}
        is_tank = "Tank" in tags or archetype == "tank"
        is_marksman = "Marksman" in tags or archetype == "marksman"
        
        # Se for um assassino ou lutador, tentamos deduzir se e AD ou AP (simplificado)
        if archetype == "assassin" and self.current_champion_name in {"Akali", "Katarina", "Evelynn", "Fizz", "Diana"}:
            is_ap = True
            
        if need_type == "armor_pen":
            if is_ap: return None # Mago nao faz pen fisica
            if is_marksman: return "Lembrancas do Lorde Dominik"
            return "Rencor de Serylda"
            
        if need_type == "magic_pen":
            if not is_ap: return None # AD nao faz pen magica (geralmente)
            return "Cajado do Vazio"
            
        if need_type == "anti_heal":
            if is_tank: return "Vestimenta de Espinhos"
            if is_ap: return "Orbe do Esquecimento"
            return "Chamado do Carrasco"
            
        return None

    def _update_match_data(self, data):
        self.game_time = data.get("gameTime", 0.0)
        if self.coaching_active:
            self.current_phase = determine_phase(self.game_time)
        self._sync_state()

    def update_game_stats(self, data):
        self.game_time = data.get("gameTime", 0.0)
        if self.coaching_active:
            self.current_phase = determine_phase(self.game_time)
        self._sync_state()

    def update_players(self, players_data):
        if not self.active_player_name:
            return

        active_player = None

        for p in players_data:
            s_name = p.get("summonerName", "").split('#')[0].strip()
            champ = p.get("championName", "Alguém")
            p_team = p.get("team", "ORDER")
            p_role = p.get("position", "")

            self.player_to_champ[s_name] = champ
            self.player_to_team[s_name] = p_team
            self.player_to_role[s_name] = p_role

            if s_name == self.active_player_name:
                active_player = p

        if not active_player:
            return

        self.our_team = active_player.get("team", self.our_team)
        self.my_position = active_player.get("position", "")
        self.current_champion_name = active_player.get("championName", "Alguém")
        self.memory.champion_name = self.current_champion_name
        self.memory.role = self.my_position
        self.memory.current_match.player_name = self.active_player_name
        self.memory.current_match.champion_name = self.current_champion_name
        self.memory.current_match.role = self.my_position

        scores = active_player.get("scores", {})
        assists = scores.get("assists", 0)
        cs = scores.get("creepScore", 0)
        wards = scores.get("wardScore", 0.0)
        minutes = self.game_time / 60.0
        lane_enemy = find_lane_enemy(players_data, self.our_team, self.my_position)
        scoped_enemy_names = build_enemy_team_names(self.player_to_team, self.player_to_champ, self.our_team)
        live_package = None
        if self.current_champion_name:
            live_package = self.coach_service.build_live_package(
                self.current_champion_name,
                self.player_to_team,
                self.player_to_champ,
                our_team=self.our_team,
                role=self.my_position,
            )

        if self.current_assists == -1:
            self.current_assists = assists
        elif assists > self.current_assists:
            self.current_assists = assists
            self._announce(self.voice.assist(), "positive", category="assist")

        if (
            not self.opening_plan_announced
            and live_package
            and live_package.opening_plan
            and 25 <= self.game_time <= 95
        ):
            self._announce(
                self.voice.opening_plan(self.current_champion_name, live_package.opening_plan),
                "neutral",
                category="opening_plan",
            )
            self.opening_plan_announced = True

        if (
            not self.history_focus_announced
            and self.history_profile
            and 35 <= self.game_time <= 110
        ):
            primary_leak = self.history_profile.get("primary_leak")
            if primary_leak:
                self._announce(
                    self.voice.history_early_focus(
                        primary_leak,
                        self.history_profile.get("hot_phase", ""),
                    ),
                    "neutral",
                    category="adaptive_feedback",
                    importance=0.8,
                    metadata={
                        "game_time": self.game_time,
                        "adaptive_topic": primary_leak,
                        "adaptive_mode": "carry_over",
                    },
                )
                self.history_focus_announced = True

        if not self.lane_matchup_announced and self.game_time > 80 and lane_enemy:
            enemy_nick = lane_enemy.get("summonerName", "").split('#')[0].strip()
            self._announce(self.voice.lane_matchup(enemy_nick), "neutral", category="lane_matchup")
            self.lane_matchup_announced = True

        if (
            not self.detailed_matchup_announced
            and lane_enemy
            and self.current_champion_name
            and self.game_time > 95
        ):
            enemy_nick = lane_enemy.get("summonerName", "").split('#')[0].strip()
            enemy_champ = lane_enemy.get("championName", "Alguém")
            insight = self.coach_service.build_lane_matchup_package(
                self.current_champion_name,
                enemy_champ,
                role=self.my_position,
            )
            if insight:
                matchup_text = self.voice.lane_matchup_knowledge(
                    self.current_champion_name,
                    enemy_champ,
                    insight,
                )
            else:
                matchup_text = self.voice.lane_matchup_detail(
                    self.current_champion_name,
                    enemy_champ,
                    enemy_nick,
                )
            self._announce(matchup_text, "neutral", category="lane_matchup")
            self.detailed_matchup_announced = True

        if (
            not self.early_build_plan_announced
            and live_package
            and len(self.player_to_team) >= 5
            and 45 <= self.game_time <= 240
        ):
            build_tip = None
            spike_tip = None
            if live_package.build_focus:
                build_tip = self.voice.early_build_focus(self.current_champion_name, live_package.build_focus)
            if live_package.power_spikes:
                spike_tip = self.voice.power_spike_call(self.current_champion_name, live_package.power_spikes)
            if not build_tip:
                build_tip = self.voice.comp_build_adjustment(self.current_champion_name, scoped_enemy_names)
            if build_tip:
                self._announce(build_tip, "neutral", category="build_plan")
                self.early_build_plan_announced = True
            if spike_tip:
                self._announce(spike_tip, "neutral", category="power_spike")

        if (
            not self.mid_game_job_announced
            and live_package
            and self.game_time >= 720
            and live_package.mid_game_job
        ):
            self._announce(
                self.voice.mid_game_job(
                    self.current_champion_name,
                    live_package.mid_game_job,
                    live_package.situational_items,
                ),
                "neutral",
                category="mid_game_job",
            )
            self.mid_game_job_announced = True

        if self.game_time > 300 and (self.game_time - self.last_farm_eval) > self.settings.economy_interval:
            self.last_farm_eval = self.game_time
            for signal in self.coach_service.economy_signals(
                game_time=self.game_time,
                creep_score=cs,
                ward_score=wards,
                hardcore_enabled=self.hardcore_enabled,
                farm_threshold=self.settings.farm_threshold,
                vision_threshold=self.settings.vision_threshold,
            ):
                if signal.metric == "farm" and signal.severity == "negative":
                    self._announce(self.voice.low_farm(cs, minutes), "negative", category="farm_eval")
                    self._push_memory_entry("Farm abaixo do ideal", f"{cs} CS aos {int(minutes)} min. O coach quer mais disciplina de wave.", "negative")
                elif signal.metric == "farm" and signal.severity == "positive":
                    self._announce(self.voice.high_farm(cs, minutes), "positive", category="farm_eval")
                    self._push_memory_entry("Farm consistente", f"{cs} CS aos {int(minutes)} min. Boa conversão de recurso.", "positive")
                elif signal.metric == "vision":
                    self._announce(self.voice.low_vision(wards), "negative", category="vision_eval")
                    self._push_memory_entry("Visão fraca", f"{wards} de visão até agora. O mapa ficou mais cego do que devia.", "negative")

                self.memory.record_evaluation(
                    signal.metric,
                    signal.score,
                    note=signal.note,
                    phase=self.current_phase,
                    category=signal.category,
                    actual=signal.actual,
                    expected=signal.expected,
                    target=signal.target,
                    severity=signal.severity,
                    metadata={"game_time": self.game_time},
                )
                self._process_adaptive_signal(
                    signal.category,
                    signal.severity,
                    {"game_time": self.game_time, "metric": signal.metric},
                )

        self.jungle_tracker.ingest_roster(
            players_data,
            self.our_team,
            self.active_player_name,
            self.game_time,
            self.player_to_role,
            self.player_to_team,
            self.player_to_champ,
        )
        self._sync_state()
        
        current_time = time.time()
        if current_time - self.last_item_check > self.settings.item_check_interval: 
 
            self.last_item_check = current_time
            
            for p in players_data:
                s_name = p.get("summonerName", "").split('#')[0].strip()
                if p.get("team") != self.our_team:
                    items = [item.get("itemID", 0) for item in p.get("items", [])]
                    p_nick = p.get("summonerName", "").split('#')[0].strip()

                    if self.knowledge:
                        item_flags = self.coach_service.classify_enemy_itemization(items)
                        has_armor = bool(item_flags.get("armor"))
                        has_mr = bool(item_flags.get("magic_resist"))
                        has_anti_heal = bool(item_flags.get("anti_heal"))
                    else:
                        has_armor = any(i in self.armor_ids for i in items)
                        has_mr = any(i in self.mr_ids for i in items)
                        has_anti_heal = any(i in self.anti_heal_ids for i in items)
                    
                    if has_armor and "armor_pen" not in self.advised_items:
                        item_sug = self._get_counter_item_suggestion("armor_pen")
                        # Se eu sou AP, ignorar aviso de armor pen
                        if item_sug or not self.knowledge:
                            self._announce(self.voice.armor_warning(p_nick, item_sug), "negative", category="item_advice")
                            self.memory.record_evaluation(
                                "itemization",
                                0.35,
                                note=f"Adaptação de build necessária contra armadura de {p_nick}. Sugestão: {item_sug or 'Penetração'}.",
                                phase=self.current_phase,
                                category="economy",
                                target=f"Comprar {item_sug or 'penetração física'} no próximo reset.",
                                severity="negative",
                                metadata={"game_time": self.game_time},
                            )
                            self._push_memory_entry("Loja atrasada", f"{p_nick} já tem armadura pesada. Considere {item_sug or 'penetração'}.", "negative")
                            self._process_adaptive_signal(
                                "item_advice",
                                "negative",
                                {"game_time": self.game_time, "metric": "itemization", "priority": "high", "subject": p_nick},
                            )
                            self.advised_items.add("armor_pen")
                            return
                        
                    if has_mr and "magic_pen" not in self.advised_items:
                        item_sug = self._get_counter_item_suggestion("magic_pen")
                        # Se eu sou AD puro, talvez ignorar aviso de magic pen
                        if item_sug or not self.knowledge:
                            self._announce(self.voice.magic_resist_warning(p_nick, item_sug), "negative", category="item_advice")
                            self.memory.record_evaluation(
                                "itemization",
                                0.35,
                                note=f"Adaptação AP necessária contra resistência mágica de {p_nick}. Sugestão: {item_sug or 'Penetração'}.",
                                phase=self.current_phase,
                                category="economy",
                                target=f"Preparar {item_sug or 'penetração mágica'} no próximo reset.",
                                severity="negative",
                                metadata={"game_time": self.game_time},
                            )
                            self._push_memory_entry("Resposta mágica atrasada", f"{p_nick} fechou MR. {item_sug or 'Ajuste a build'}.", "negative")
                            self._process_adaptive_signal(
                                "item_advice",
                                "negative",
                                {"game_time": self.game_time, "metric": "itemization", "priority": "high", "subject": p_nick},
                            )
                            self.advised_items.add("magic_pen")
                            return

                    if has_anti_heal and "anti_heal" not in self.advised_items:
                        item_sug = self._get_counter_item_suggestion("anti_heal")
                        self._announce(self.voice.anti_heal_warning(p_nick, item_sug), "negative", category="item_advice")
                        self.memory.record_evaluation(
                            "survivability",
                            0.4,
                            note=f"O inimigo {p_nick} comprou corta-cura e mudou as janelas de sustain.",
                            phase=self.current_phase,
                            category="recovery",
                            target="Respeitar trocas longas e revisar timing de entrada.",
                            severity="negative",
                            metadata={"game_time": self.game_time},
                        )
                        self._push_memory_entry("Sustain punido", f"{p_nick} comprou corta-cura. Troca longa ficou mais arriscada.", "negative")
                        self._process_adaptive_signal(
                            "item_advice",
                            "negative",
                            {"game_time": self.game_time, "metric": "itemization", "priority": "medium", "subject": p_nick},
                        )
                        self.advised_items.add("anti_heal")
                        return

    def get_jungle_intel_snapshot(self):
        return self.jungle_tracker.snapshot()

    def _maybe_announce_jungle_intel(self, previous_snapshot, current_snapshot):
        if not current_snapshot or current_snapshot == previous_snapshot:
            return

        previous_first_gank = (previous_snapshot or {}).get("first_gank")
        current_first_gank = current_snapshot.get("first_gank")
        if current_first_gank and current_first_gank != previous_first_gank:
            lane = current_first_gank.get("lane", "rio")
            jungler = current_snapshot.get("enemy_jungler_name") or "o jungler inimigo"
            if current_first_gank.get("target_team") == "ally":
                self._announce(
                    self.voice.jungle_gank_warning(jungler, lane),
                    "negative",
                    category="jungle_intel",
                )
                return

        previous_objectives = (previous_snapshot or {}).get("objective_presence", {})
        current_objectives = current_snapshot.get("objective_presence", {})
        for objective_name, total in current_objectives.items():
            if total > previous_objectives.get(objective_name, 0):
                jungler = current_snapshot.get("enemy_jungler_name") or "o jungler inimigo"
                self._announce(
                    self.voice.jungle_objective_shadow(jungler, objective_name),
                    "neutral",
                    category="jungle_intel",
                )
                return

    def process_event(self, event):
        name = event.get("EventName")
        previous_jungle_snapshot = self.jungle_tracker.snapshot()
        if name in {"ChampionKill", "DragonKill", "HeraldKill", "BaronKill", "HordeKill"}:
            self.jungle_tracker.ingest_event(
                event,
                self.game_time,
                self.player_to_role,
                self.player_to_team,
                self.player_to_champ,
            )
            self._maybe_announce_jungle_intel(previous_jungle_snapshot, self.jungle_tracker.snapshot())
        analysis = self.coach_service.analyze_event(
            event,
            active_player_name=self.active_player_name,
            player_to_team=self.player_to_team,
            player_to_champ=self.player_to_champ,
            our_team=self.our_team,
            voice=self.voice,
            ally_drags=self.ally_drags,
            enemy_drags=self.enemy_drags,
            map_pve_name=self.map_pve_name,
            solo_focus=self.settings.solo_focus,
        )

        if analysis.stat_updates:
            self.ally_drags = analysis.stat_updates.get("ally_drags", self.ally_drags)
            self.enemy_drags = analysis.stat_updates.get("enemy_drags", self.enemy_drags)

        for call in analysis.calls:
            if call.objective_only:
                self._announce_objective(
                    call.text,
                    call.event_type,
                    category=call.category,
                    importance=call.importance,
                    metadata=call.metadata,
                )
            else:
                self._announce(
                    call.text,
                    call.event_type,
                    category=call.category,
                    importance=call.importance,
                    metadata=call.metadata,
                )
            if (not call.objective_only or self.objectives_enabled) and self.settings.is_category_enabled(call.category):
                self._process_adaptive_signal(
                    call.category,
                    call.event_type,
                    {"game_time": self.game_time, **(call.metadata or {})},
                )
            if call.memory_entry:
                self._push_memory_entry(
                    call.memory_entry.get("title", "Leitura de evento"),
                    call.memory_entry.get("note", call.text),
                    call.memory_entry.get("tone", "normal"),
                    meta=call.metadata.get("impact", "") if call.metadata else "",
                )
        self._sync_state()
