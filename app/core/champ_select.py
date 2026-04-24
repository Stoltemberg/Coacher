import threading

from core.coach_service import CoachService
from core.minerva_voice import MinervaVoice

class ChampSelectCoach:
    def __init__(
        self,
        assistant,
        voice=None,
        knowledge=None,
        coach_service=None,
        history_provider=None,
        counterpick_callback=None,
        draft_preferences_provider=None,
    ):
        self.assistant = assistant
        self.voice = voice or MinervaVoice()
        self.knowledge = knowledge
        self.coach_service = coach_service or CoachService(knowledge)
        self.history_provider = history_provider
        self.counterpick_callback = counterpick_callback
        self.draft_preferences_provider = draft_preferences_provider
        self.last_enemy_picks = set()
        self.champions_map = {} # ID -> Name
        self.my_champ = None
        self.advised_champion_id = None
        self.my_role = None
        self.history_call_sent = False
        self.last_my_hover = None
        self.last_hover_advice_id = None
        self.last_counter_signature = None
        
        # Categorias para análise tática
        self.high_cc_champs = ["Leona", "Nautilus", "Morgana", "Ashe", "Sejuani", "Lissandra", "Amumu", "Maokai", "Thresh"]
        self.assassins = ["Zed", "Talon", "Akali", "Katarina", "Evelynn", "Rengar", "Kha'Zix", "Leblanc", "Fizz", "Qiyana"]
        self.tanks = ["Malphite", "Ornn", "Sion", "Mundo", "Rammus", "Cho'Gath", "Zac"]

    def _schedule_say(self, delay, text, event_type="neutral"):
        threading.Timer(delay, lambda: self.assistant.say(text, event_type, category="draft")).start()

    def get_champion_name(self, champ_id):
        if self.knowledge:
            name = self.knowledge.get_champion_name(champ_id)
            if name != f"Campeão {champ_id}":
                return name
        return self.champions_map.get(champ_id, f"Campeão {champ_id}")

    def _get_local_champion_context(self, session_data, local_cell_id):
        hover_id = None
        role = None

        for player in session_data.get("myTeam", []):
            if player.get("cellId") != local_cell_id:
                continue

            champion_id = player.get("championId", 0) or 0
            intent_id = player.get("championPickIntent", 0) or 0
            hover_id = champion_id or intent_id or None
            role = (
                player.get("assignedPosition")
                or player.get("selectedPosition")
                or player.get("position")
                or None
            )
            break

        locked_id = None
        for action_group in session_data.get("actions", []):
            for action in action_group:
                if action.get("actorCellId") != local_cell_id:
                    continue
                if action.get("type") != "pick":
                    continue
                if not action.get("completed"):
                    continue

                champion_id = action.get("championId", 0) or 0
                if champion_id > 0:
                    locked_id = champion_id

        return hover_id, locked_id, role

    def _get_allied_context(self, session_data, local_cell_id):
        allies = []
        for player in session_data.get("myTeam", []):
            if player.get("cellId") == local_cell_id:
                continue

            champion_id = player.get("championId", 0) or 0
            if champion_id <= 0:
                continue

            allies.append(
                {
                    "champion": self.get_champion_name(champion_id),
                    "role": (
                        player.get("assignedPosition")
                        or player.get("selectedPosition")
                        or player.get("position")
                        or ""
                    ),
                }
            )
        return allies

    def process_session(self, session_data):
        if not session_data:
            return
            
        enemy_team = session_data.get("theirTeam", [])
        bans_data = session_data.get("bans") or {}
        bans = list(bans_data.get("myTeamBans", []) or []) + list(bans_data.get("theirTeamBans", []) or [])
        local_cell_id = session_data.get("localPlayerCellId")
        my_hover_champ_id, my_locked_champ_id, my_role = self._get_local_champion_context(session_data, local_cell_id)
        allies = self._get_allied_context(session_data, local_cell_id)
        self.my_role = my_role

        # Listas ativas
        current_enemy_names = []
        current_enemy_picks = set()

        for player in enemy_team:
            cid = player.get("championId", 0)
            if cid > 0:
                current_enemy_picks.add(cid)
                name = self.get_champion_name(cid)
                current_enemy_names.append(name)
                
        # Verificar se os inimigos travaram algum campeão novo (Apenas Dicas de Counter)
        new_picks = current_enemy_picks - self.last_enemy_picks
        for champ_id in new_picks:
            name = self.get_champion_name(champ_id)
            if name != f"Campeão {champ_id}":
                self.assistant.say(self.voice.draft_enemy_locked(name), category="draft")
                counter_tip = self.voice.draft_counter_tip(name)
                if counter_tip:
                    self._schedule_say(0.8, counter_tip)

        if current_enemy_names and not my_locked_champ_id:
            self._suggest_counter_picks(current_enemy_names, allies, bans)

        self.last_enemy_picks = current_enemy_picks

        # Guarda o hover para UI/estado local
        if my_hover_champ_id and my_hover_champ_id > 0:
            self.my_champ = self.get_champion_name(my_hover_champ_id)
            # Se for um novo hover, dar conselho proativo
            if my_hover_champ_id != self.last_hover_advice_id:
                self.last_hover_advice_id = my_hover_champ_id
                self._provide_champion_advice(self.my_champ, current_enemy_names, allies)
        else:
            self.my_champ = None

        if not my_locked_champ_id or my_locked_champ_id <= 0:
            return

        if self.advised_champion_id == my_locked_champ_id:
            return

        my_champ_name = self.get_champion_name(my_locked_champ_id)
        self.my_champ = my_champ_name
        self.advised_champion_id = my_locked_champ_id
        self.last_hover_advice_id = my_locked_champ_id # Sync locked as advice sent

        self.assistant.say(self.voice.draft_pick_confirmed(my_champ_name), category="draft")

        if self.history_provider and not self.history_call_sent:
            try:
                history = self.history_provider() or {}
            except Exception:
                history = {}
            adaptive = history.get("adaptive_profile") or {}
            if adaptive.get("primary_leak"):
                self._schedule_say(
                    1.0,
                    self.voice.history_draft_focus(
                        my_champ_name,
                        adaptive.get("primary_leak"),
                        adaptive.get("hot_phase", ""),
                    ),
                )
                self.history_call_sent = True
            elif adaptive.get("primary_fix"):
                self._schedule_say(
                    1.0,
                    self.voice.history_draft_strength(
                        my_champ_name,
                        adaptive.get("primary_fix"),
                    ),
                )
                self.history_call_sent = True

    def _provide_champion_advice(self, my_champ_name, current_enemy_names, allies):
        if self.coach_service:
            guidance = self.coach_service.build_draft_package(
                my_champ_name,
                current_enemy_names,
                allies=allies,
                role=self.my_role,
            )
            if guidance:
                self._schedule_say(
                    0.5,
                    self.voice.draft_comp_snapshot(
                        my_champ_name,
                        guidance.comp_style,
                        guidance.pressure_points,
                    ),
                )
                self._schedule_say(
                    1.5,
                    self.voice.draft_power_spike(
                        my_champ_name,
                        guidance.power_spikes,
                    ),
                )
                lane_plan = guidance.lane_plan
                first_reset_focus = guidance.first_reset_focus
                if lane_plan and first_reset_focus:
                    self._schedule_say(
                        2.5,
                        self.voice.draft_role_plan(my_champ_name, lane_plan, first_reset_focus),
                    )
                return

        # Heurística Tática Inimiga
        cc_count = sum(1 for c in current_enemy_names if c in self.high_cc_champs)
        assassin_count = sum(1 for c in current_enemy_names if c in self.assassins)
        tank_count = sum(1 for c in current_enemy_names if c in self.tanks)

        if cc_count >= 2:
            plan_key = "high_cc"
        elif assassin_count >= 2:
            plan_key = "assassins"
        elif tank_count >= 2:
            plan_key = "tanks"
        else:
            plan_key = "standard"

        self._schedule_say(0.8, self.voice.draft_comp_plan(plan_key, my_champ_name))

    def _suggest_counter_picks(self, current_enemy_names, allies, bans):
        if not self.coach_service or len(current_enemy_names) < 2:
            return

        preferences = self.draft_preferences_provider() if self.draft_preferences_provider else {}
        preferred_pool = preferences.get("preferred_champion_pool") or []
        prioritize_pool = bool(preferences.get("prioritize_pool_picks", True))

        package = self.coach_service.recommend_counter_picks(
            current_enemy_names,
            role=self.my_role,
            allies=allies,
            banned=bans,
            preferred_pool=preferred_pool,
            prioritize_pool=prioritize_pool,
            limit=3,
        )
        if not package or not package.recommendations:
            return

        signature = (
            tuple(sorted(current_enemy_names)),
            package.role,
            tuple(item.get("champion") for item in package.recommendations),
        )
        if signature == self.last_counter_signature:
            return

        self.last_counter_signature = signature
        self._schedule_say(
            1.0,
            self.voice.draft_counter_recommendations(package.role, package.recommendations),
        )
        if self.counterpick_callback:
            self.counterpick_callback(
                {
                    "role": package.role,
                    "enemy_preview": package.enemy_preview,
                    "recommendations": package.recommendations,
                }
            )

    def reset(self):
        self.last_enemy_picks.clear()
        self.my_champ = None
        self.advised_champion_id = None
        self.my_role = None
        self.history_call_sent = False
        self.last_my_hover = None
        self.last_hover_advice_id = None
        self.last_counter_signature = None
        if self.counterpick_callback:
            self.counterpick_callback(None)
