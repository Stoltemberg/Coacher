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
        self.champions_map = {}  # ID -> Name
        self.my_champ = None
        self.advised_champion_id = None
        self.my_role = None
        self.history_call_sent = False
        self.last_my_hover = None
        self.last_hover_advice_id = None
        self.last_counter_signature = None
        self.last_ban_signature = None
        self.last_locked_signature = None
        self.locked_pick_announced = False
        self.pending_timers = []

        # Categorias para analise tatica
        self.high_cc_champs = ["Leona", "Nautilus", "Morgana", "Ashe", "Sejuani", "Lissandra", "Amumu", "Maokai", "Thresh"]
        self.assassins = ["Zed", "Talon", "Akali", "Katarina", "Evelynn", "Rengar", "Kha'Zix", "Leblanc", "Fizz", "Qiyana"]
        self.tanks = ["Malphite", "Ornn", "Sion", "Mundo", "Rammus", "Cho'Gath", "Zac"]

    def _schedule_say(self, delay, text, event_type="neutral"):
        if not text:
            return
        timer_ref = {"timer": None}

        def _run():
            try:
                self.assistant.say(text, event_type, category="draft")
            finally:
                timer = timer_ref["timer"]
                if timer in self.pending_timers:
                    self.pending_timers.remove(timer)

        timer = threading.Timer(delay, _run)
        timer_ref["timer"] = timer
        self.pending_timers.append(timer)
        timer.start()

    def _cancel_pending_draft_calls(self):
        for timer in list(self.pending_timers):
            try:
                timer.cancel()
            except Exception:
                pass
        self.pending_timers.clear()

    def _schedule_draft_pair(
        self,
        primary_text,
        secondary_text=None,
        *,
        primary_delay=0.5,
        secondary_delay=1.6,
    ):
        self._cancel_pending_draft_calls()
        self._schedule_say(primary_delay, primary_text)
        if secondary_text:
            self._schedule_say(secondary_delay, secondary_text)

    def _draft_should_use_secondary(
        self,
        phase,
        *,
        enemy_count=0,
        has_current_pick=False,
    ):
        phase_key = str(phase or "").strip().lower()
        if phase_key == "ban":
            return False
        if phase_key == "pick":
            if has_current_pick:
                return False
            return enemy_count <= 3
        if phase_key == "locked":
            return enemy_count <= 3
        if phase_key == "hover":
            return enemy_count <= 2
        return enemy_count <= 3

    def _select_locked_primary_call(self, my_champ_name, package):
        role_key = self._normalize_role(self.my_role)
        matchup = package.matchup or {}
        guidance = package.guidance or {}
        enemy_anchor = package.enemy_anchor
        verdict = str(matchup.get("verdict") or "").strip().lower()
        danger_text = str(matchup.get("danger") or "").strip()
        lane_fail_condition = str(matchup.get("lane_fail_condition") or "").strip()
        lane_win_condition = str(matchup.get("lane_win_condition") or "").strip()
        synergy_summary = str(guidance.get("synergy_summary") or "").strip()
        reset_adjustment = str(guidance.get("reset_adjustment") or "").strip()
        first_item_plan = str(guidance.get("first_item_plan") or "").strip()
        map_plan_summary = str(guidance.get("map_plan_summary") or "").strip()
        fight_plan_summary = str(guidance.get("fight_plan_summary") or "").strip()
        severe_danger = verdict in {"perigoso", "all-in ou nada", "explosivo"}
        moderate_danger = verdict in {"delicado"} or bool(lane_fail_condition) or bool(danger_text)

        if role_key in {"bottom", "support"} and (synergy_summary or fight_plan_summary) and not severe_danger:
            return (
                "duo",
                self.voice.draft_locked_duo_focus(
                    my_champ_name,
                    enemy_anchor,
                    matchup,
                    guidance,
                ),
            )
        if role_key == "jungle" and (map_plan_summary or fight_plan_summary) and not severe_danger:
            return (
                "map",
                self.voice.draft_locked_map_focus(
                    my_champ_name,
                    enemy_anchor,
                    matchup,
                    guidance,
                ),
            )
        if severe_danger or (moderate_danger and role_key not in {"bottom", "support", "jungle"}):
            return (
                "danger",
                self.voice.draft_locked_danger_focus(
                    my_champ_name,
                    enemy_anchor,
                    matchup,
                    guidance,
                ),
            )
        if synergy_summary:
            return (
                "synergy",
                self.voice.draft_locked_synergy_focus(
                    my_champ_name,
                    enemy_anchor,
                    matchup,
                    guidance,
                ),
            )
        if lane_win_condition:
            return (
                "win",
                self.voice.draft_locked_win_focus(
                    my_champ_name,
                    enemy_anchor,
                    matchup,
                    guidance,
                ),
            )
        if reset_adjustment or first_item_plan:
            return (
                "reset",
                self.voice.draft_locked_reset_focus(
                    my_champ_name,
                    enemy_anchor,
                    matchup,
                    guidance,
                ),
            )
        return (
            "matchup",
            self.voice.draft_locked_matchup_plan(
                my_champ_name,
                enemy_anchor,
                matchup,
                guidance,
            ),
        )

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

    def _get_enemy_context(self, session_data):
        enemies = []
        for player in session_data.get("theirTeam", []):
            champion_id = player.get("championId", 0) or 0
            if champion_id <= 0:
                continue
            enemies.append(
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
        return enemies

    def _get_local_action_phase(self, session_data, local_cell_id):
        for action_group in session_data.get("actions", []):
            for action in action_group:
                if action.get("actorCellId") != local_cell_id:
                    continue
                if action.get("completed"):
                    continue
                action_type = str(action.get("type") or "").strip().lower()
                if action_type in {"ban", "pick"}:
                    return action_type
        return "pick"

    def _get_draft_window_context(self, session_data, local_cell_id, role, action_phase):
        phase_key = str(action_phase or "").strip().lower()
        current_group = None
        local_action = None
        same_phase_groups = []
        for action_group in session_data.get("actions", []):
            group_phase = None
            for action in action_group:
                action_type = str(action.get("type") or "").strip().lower()
                if action_type in {"ban", "pick"}:
                    group_phase = action_type
                    break
            if group_phase == phase_key:
                same_phase_groups.append(action_group)
            for action in action_group:
                if action.get("actorCellId") != local_cell_id:
                    continue
                if action.get("completed"):
                    continue
                action_type = str(action.get("type") or "").strip().lower()
                if action_type == phase_key:
                    current_group = action_group
                    local_action = action
                    break
            if current_group:
                break

        if not current_group or not local_action:
            return {
                "phase": phase_key or "pick",
                "enemy_actions_after": 0,
                "enemy_actions_before": 0,
                "draft_open": False,
                "response_risk": "low",
                "rotation_stage": "unknown",
            }

        my_team_cells = {
            player.get("cellId")
            for player in session_data.get("myTeam", [])
            if player.get("cellId") is not None
        }
        enemy_team_cells = {
            player.get("cellId")
            for player in session_data.get("theirTeam", [])
            if player.get("cellId") is not None
        }
        local_index = current_group.index(local_action)
        enemy_before = 0
        enemy_after = 0
        for idx, action in enumerate(current_group):
            if action.get("completed"):
                continue
            if action.get("actorCellId") in my_team_cells:
                continue
            if idx < local_index:
                enemy_before += 1
            elif idx > local_index:
                enemy_after += 1

        ally_indices = [
            idx
            for idx, action in enumerate(current_group)
            if action.get("actorCellId") in my_team_cells
        ]
        try:
            ally_slot_index = ally_indices.index(local_index)
        except ValueError:
            ally_slot_index = 0
        if len(ally_indices) <= 1:
            ally_slot_timing = "solo"
        elif ally_slot_index <= 0:
            ally_slot_timing = "early"
        elif ally_slot_index >= len(ally_indices) - 1:
            ally_slot_timing = "late"
        else:
            ally_slot_timing = "mid"

        if my_team_cells and enemy_team_cells:
            team_side = "blue" if min(my_team_cells) < min(enemy_team_cells) else "red"
        else:
            team_side = "blue" if int(local_cell_id or 0) < 5 else "red"

        role_key = self._normalize_role(role)
        if phase_key == "pick":
            if role_key in {"top", "mid", "middle"}:
                response_risk = "high" if enemy_after > 0 else "low"
            elif role_key in {"bottom", "support"}:
                response_risk = "high" if enemy_after >= 2 else ("medium" if enemy_after == 1 else "low")
            else:
                response_risk = "medium" if enemy_after > 0 else "low"
        else:
            response_risk = "medium" if enemy_after > 0 else "low"

        ally_locked_count = sum(
            1
            for player in session_data.get("myTeam", [])
            if (player.get("championId", 0) or 0) > 0
        )
        enemy_locked_count = sum(
            1
            for player in session_data.get("theirTeam", [])
            if (player.get("championId", 0) or 0) > 0
        )
        if enemy_locked_count > ally_locked_count:
            info_edge = "answering"
        elif ally_locked_count > enemy_locked_count:
            info_edge = "exposed"
        else:
            info_edge = "even"

        if enemy_before == 0 and enemy_after > 0:
            selection_posture = "blind"
        elif enemy_before > 0 and enemy_after > 0:
            selection_posture = "contest"
        elif enemy_before > 0 and enemy_after == 0:
            selection_posture = "answer"
        else:
            selection_posture = "neutral"

        try:
            rotation_index = same_phase_groups.index(current_group)
        except ValueError:
            rotation_index = 0
        if rotation_index <= 0:
            rotation_stage = "first"
        elif rotation_index == 1:
            rotation_stage = "second"
        else:
            rotation_stage = "late"

        revealed_roles = {
            self._normalize_role(
                player.get("assignedPosition")
                or player.get("selectedPosition")
                or player.get("position")
                or ""
            )
            for player in session_data.get("theirTeam", [])
            if (player.get("championId", 0) or 0) > 0
        }
        if role_key in {"bottom", "support"}:
            lane_roles = {"bottom", "support"}
        elif role_key in {"mid", "middle"}:
            lane_roles = {"mid"}
        elif role_key:
            lane_roles = {role_key}
        else:
            lane_roles = set()
        revealed_lane_roles = revealed_roles & lane_roles
        if not lane_roles or not revealed_lane_roles:
            lane_state = "hidden"
        elif revealed_lane_roles == lane_roles:
            lane_state = "full"
        else:
            lane_state = "partial"

        if not revealed_lane_roles:
            lane_response_state = "blind"
        elif revealed_lane_roles == lane_roles and enemy_after == 0:
            lane_response_state = "answered"
        else:
            lane_response_state = "semi"

        return {
            "phase": phase_key or "pick",
            "team_side": team_side,
            "enemy_actions_after": enemy_after,
            "enemy_actions_before": enemy_before,
            "ally_slot_timing": ally_slot_timing,
            "draft_open": enemy_after > 0,
            "response_risk": response_risk,
            "lane_state": lane_state,
            "lane_response_state": lane_response_state,
            "revealed_lane_roles": sorted(revealed_lane_roles),
            "selection_posture": selection_posture,
            "rotation_stage": rotation_stage,
            "ally_locked_count": ally_locked_count,
            "enemy_locked_count": enemy_locked_count,
            "info_edge": info_edge,
        }

    def _normalize_role(self, role):
        if self.coach_service and self.coach_service.knowledge:
            return self.coach_service.knowledge._normalize_role(role or "")
        return str(role or "").strip().lower()

    def _get_enemy_lane_anchor(self, session_data, role):
        role_key = self._normalize_role(role)
        for player in session_data.get("theirTeam", []):
            candidate_role = (
                player.get("assignedPosition")
                or player.get("selectedPosition")
                or player.get("position")
                or ""
            )
            champion_id = player.get("championId", 0) or 0
            if champion_id <= 0:
                continue
            if self._normalize_role(candidate_role) == role_key:
                return self.get_champion_name(champion_id)

        for player in session_data.get("theirTeam", []):
            champion_id = player.get("championId", 0) or 0
            if champion_id > 0:
                return self.get_champion_name(champion_id)
        return None

    def process_session(self, session_data):
        if not session_data:
            return

        enemy_team = session_data.get("theirTeam", [])
        bans_data = session_data.get("bans") or {}
        bans = list(bans_data.get("myTeamBans", []) or []) + list(bans_data.get("theirTeamBans", []) or [])
        local_cell_id = session_data.get("localPlayerCellId")
        my_hover_champ_id, my_locked_champ_id, my_role = self._get_local_champion_context(session_data, local_cell_id)
        action_phase = self._get_local_action_phase(session_data, local_cell_id)
        draft_window = self._get_draft_window_context(session_data, local_cell_id, my_role, action_phase)
        allies = self._get_allied_context(session_data, local_cell_id)
        revealed_enemies = self._get_enemy_context(session_data)
        self.my_role = my_role

        current_enemy_names = []
        current_enemy_picks = set()
        for player in enemy_team:
            cid = player.get("championId", 0)
            if cid > 0:
                current_enemy_picks.add(cid)
                current_enemy_names.append(self.get_champion_name(cid))

        if my_locked_champ_id and my_locked_champ_id > 0:
            self.last_enemy_picks = current_enemy_picks
            self._process_locked_pick(session_data, my_locked_champ_id, current_enemy_names, allies, revealed_enemies)
            return

        new_picks = current_enemy_picks - self.last_enemy_picks
        for champ_id in new_picks:
            name = self.get_champion_name(champ_id)
            if name != f"Campeão {champ_id}":
                self.assistant.say(self.voice.draft_enemy_locked(name), category="draft")
                counter_tip = self.voice.draft_counter_tip(name)
                if counter_tip:
                    self._schedule_say(0.8, counter_tip)

        current_pick_name = self.get_champion_name(my_hover_champ_id) if my_hover_champ_id and my_hover_champ_id > 0 else None
        enemy_anchor = self._get_enemy_lane_anchor(session_data, self.my_role)
        if current_enemy_names:
            if action_phase == "ban":
                self._suggest_bans(current_enemy_names, bans, current_pick_name, stage="ban", revealed_enemies=revealed_enemies, draft_window=draft_window)
            else:
                self._suggest_counter_picks(
                    current_enemy_names,
                    allies,
                    bans,
                    current_pick_name,
                    stage="pick",
                    enemy_anchor=enemy_anchor,
                    revealed_enemies=revealed_enemies,
                    draft_window=draft_window,
                )

        self.last_enemy_picks = current_enemy_picks

        if my_hover_champ_id and my_hover_champ_id > 0:
            self.my_champ = self.get_champion_name(my_hover_champ_id)
            if my_hover_champ_id != self.last_hover_advice_id:
                self.last_hover_advice_id = my_hover_champ_id
                self._provide_champion_advice(self.my_champ, current_enemy_names, allies, phase=action_phase)
        else:
            self.my_champ = None

    def _process_locked_pick(self, session_data, my_locked_champ_id, current_enemy_names, allies, revealed_enemies):
        my_champ_name = self.get_champion_name(my_locked_champ_id)
        self.my_champ = my_champ_name
        self.advised_champion_id = my_locked_champ_id
        self.last_hover_advice_id = my_locked_champ_id

        if not self.locked_pick_announced:
            self.assistant.say(self.voice.draft_pick_confirmed(my_champ_name), category="draft")
            self.locked_pick_announced = True

        history_text = None
        if self.history_provider and not self.history_call_sent:
            try:
                history = self.history_provider() or {}
            except Exception:
                history = {}
            adaptive = history.get("adaptive_profile") or {}
            if adaptive.get("primary_leak"):
                history_text = self.voice.history_draft_focus(
                    my_champ_name,
                    adaptive.get("primary_leak"),
                    adaptive.get("hot_phase", ""),
                )
                self.history_call_sent = True
            elif adaptive.get("primary_fix"):
                history_text = self.voice.history_draft_strength(
                    my_champ_name,
                    adaptive.get("primary_fix"),
                )
                self.history_call_sent = True

        enemy_anchor = self._get_enemy_lane_anchor(session_data, self.my_role)
        self._provide_locked_pick_advice(my_champ_name, current_enemy_names, allies, enemy_anchor, history_text=history_text)
        self.last_enemy_picks = set(self.last_enemy_picks)

    def _provide_champion_advice(self, my_champ_name, current_enemy_names, allies, phase="hover"):
        if self.coach_service:
            guidance = self.coach_service.build_draft_package(
                my_champ_name,
                current_enemy_names,
                allies=allies,
                role=self.my_role,
            )
            if guidance:
                primary_text = self.voice.draft_comp_snapshot(
                    my_champ_name,
                    guidance.comp_style,
                    guidance.pressure_points,
                )
                secondary_text = None
                if self._draft_should_use_secondary(phase, enemy_count=len(current_enemy_names)):
                    secondary_text = self.voice.draft_power_spike(
                        my_champ_name,
                        guidance.power_spikes,
                    )
                lane_plan = guidance.lane_plan
                first_reset_focus = guidance.first_reset_focus
                if lane_plan and first_reset_focus:
                    primary_text = self.voice.draft_role_plan(my_champ_name, lane_plan, first_reset_focus)
                self._schedule_draft_pair(primary_text, secondary_text)
                return

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

        self._schedule_draft_pair(self.voice.draft_comp_plan(plan_key, my_champ_name), None, primary_delay=0.8)

    def _provide_locked_pick_advice(self, my_champ_name, current_enemy_names, allies, enemy_anchor, history_text=None):
        if not self.coach_service or not current_enemy_names:
            return

        package = self.coach_service.build_locked_draft_plan(
            my_champ_name,
            current_enemy_names,
            role=self.my_role,
            enemy_anchor=enemy_anchor,
            allies=allies,
        )
        if not package:
            return

        signature = (
            my_champ_name,
            package.enemy_anchor,
            tuple(sorted(current_enemy_names)),
            tuple(package.guidance.get("build_focus", [])[:2]),
        )
        if signature == self.last_locked_signature:
            return

        self.last_locked_signature = signature
        locked_focus, primary_text = self._select_locked_primary_call(my_champ_name, package)
        secondary_text = None
        allow_secondary = self._draft_should_use_secondary("locked", enemy_count=len(current_enemy_names))
        if locked_focus == "map" and self._normalize_role(self.my_role) == "jungle":
            allow_secondary = False
        if locked_focus == "duo" and self._normalize_role(self.my_role) in {"bottom", "support"}:
            allow_secondary = False
        if locked_focus == "matchup" and self._normalize_role(self.my_role) in {"top", "mid", "middle"}:
            allow_secondary = False
        if locked_focus == "danger" and self._normalize_role(self.my_role) in {"top", "mid", "middle", "jungle"}:
            allow_secondary = False
        if locked_focus in {"win", "synergy"}:
            allow_secondary = False
        if history_text and allow_secondary:
            secondary_text = history_text
        elif package.guidance.get("build_focus") and allow_secondary:
            secondary_text = self.voice.draft_build_focus(my_champ_name, package.guidance.get("build_focus", []))
        self._schedule_draft_pair(primary_text, secondary_text, primary_delay=0.6, secondary_delay=1.9)

        if self.counterpick_callback:
            self.counterpick_callback(
                {
                    "stage": "locked",
                    "role": package.role,
                    "enemy_preview": current_enemy_names,
                    "recommendations": [],
                    "best_ban": None,
                    "ban_recommendations": [],
                    "locked_plan": {
                        "champion": my_champ_name,
                        "locked_focus": locked_focus,
                        "enemy_anchor": package.enemy_anchor,
                        "verdict": package.matchup.get("verdict", ""),
                        "plan": package.matchup.get("plan", ""),
                        "danger": package.matchup.get("danger", ""),
                        "lane_plan": package.matchup.get("lane_plan", ""),
                        "lane_windows": list(package.matchup.get("lane_windows", []) or package.guidance.get("lane_windows", [])[:3]),
                        "lane_win_condition": package.matchup.get("lane_win_condition", ""),
                        "lane_fail_condition": package.matchup.get("lane_fail_condition", ""),
                        "recommended_setup": package.matchup.get("recommended_setup", ""),
                        "opening_plan": package.guidance.get("opening_plan", ""),
                        "first_reset_focus": package.guidance.get("first_reset_focus", ""),
                        "reset_adjustment": package.guidance.get("reset_adjustment", ""),
                        "map_plan_summary": package.guidance.get("map_plan_summary", ""),
                        "fight_plan_summary": package.guidance.get("fight_plan_summary", ""),
                        "team_plan_summary": package.guidance.get("team_plan_summary", ""),
                        "synergy_summary": package.guidance.get("synergy_summary", ""),
                        "first_item_plan": package.matchup.get("first_item_plan", "") or package.guidance.get("first_item_plan", ""),
                        "power_spikes": list(package.guidance.get("power_spikes", [])[:2]),
                        "build_focus": list(package.guidance.get("build_focus", [])[:3]),
                    },
                }
            )

    def _select_pick_primary_call(self, role_label, recommendation):
        pick = recommendation or {}
        role_key = self._normalize_role(role_label)
        window = str(pick.get("window") or "").strip().lower()
        context = str(pick.get("context") or "").strip().lower()
        focus = str(pick.get("focus") or "").strip().lower()
        if role_key in {"bottom", "support"} and (window in {"adc-revealed", "support-revealed", "duo-answered"} or context == "duo-forming"):
            return self.voice.draft_pick_duo_focus(role_label, recommendation)
        if role_key == "jungle" and window in {"map-blind", "map-semi", "map-answered"}:
            return self.voice.draft_pick_map_focus(role_label, recommendation)
        if role_key in {"top", "mid", "middle"} and window in {"answer-slot", "lane-answered", "lane-shaped"} and focus != "comfort-pick":
            return self.voice.draft_pick_answer_focus(role_label, recommendation)
        return self.voice.draft_best_pick(role_label, recommendation)

    def _select_ban_primary_call(self, role_label, recommendation, current_pick_name=None):
        ban = recommendation or {}
        role_key = self._normalize_role(role_label)
        window = str(ban.get("window") or "").strip().lower()
        context = str(ban.get("context") or "").strip().lower()
        if role_key in {"bottom", "support"} and (window in {"adc-revealed", "support-revealed", "duo-answered"} or context == "duo-forming"):
            return self.voice.draft_ban_duo_focus(role_label, recommendation, current_pick_name)
        if role_key == "jungle" and window in {"map-blind", "map-semi", "map-answered"}:
            return self.voice.draft_ban_map_focus(role_label, recommendation, current_pick_name)
        if role_key in {"top", "mid", "middle"} and window in {"answer-slot", "lane-answered", "lane-protect"}:
            return self.voice.draft_ban_answer_focus(role_label, recommendation, current_pick_name)
        return self.voice.draft_best_ban(role_label, recommendation, current_pick_name)

    def _suggest_counter_picks(self, current_enemy_names, allies, bans, current_pick_name=None, stage="pick", enemy_anchor=None, revealed_enemies=None, draft_window=None):
        if not self.coach_service or len(current_enemy_names) < 2:
            return

        preferences = self.draft_preferences_provider() if self.draft_preferences_provider else {}
        preferred_pool = preferences.get("preferred_champion_pool") or []
        main_champions = preferences.get("main_champions") or []
        prioritize_pool = bool(preferences.get("prioritize_pool_picks", True))

        package = self.coach_service.recommend_counter_picks(
            current_enemy_names,
            role=self.my_role,
            enemy_anchor=enemy_anchor,
            allies=allies,
            revealed_enemies=revealed_enemies,
            draft_window=draft_window,
            banned=bans,
            main_champions=main_champions,
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
        primary_text = self._select_pick_primary_call(package.role, package.recommendations[0])
        secondary_text = None
        if len(package.recommendations) > 1 and self._draft_should_use_secondary(
            "pick",
            enemy_count=len(current_enemy_names),
            has_current_pick=bool(current_pick_name),
        ):
            secondary_text = self.voice.draft_counter_recommendations(package.role, package.recommendations)
        self._schedule_draft_pair(primary_text, secondary_text, primary_delay=0.8, secondary_delay=1.9)

        ban_payload = self._build_ban_payload(current_enemy_names, bans, current_pick_name, stage=stage, draft_window=draft_window)
        if self.counterpick_callback:
            self.counterpick_callback(
                {
                    "stage": stage,
                    "role": package.role,
                    "enemy_preview": package.enemy_preview,
                    "recommendations": package.recommendations,
                    **ban_payload,
                    "locked_plan": None,
                }
            )

    def _build_ban_payload(self, current_enemy_names, bans, current_pick_name=None, stage="ban", draft_window=None):
        preferences = self.draft_preferences_provider() if self.draft_preferences_provider else {}
        package = self.coach_service.recommend_bans(
            current_enemy_names,
            role=self.my_role,
            stage=stage,
            current_pick=current_pick_name,
            draft_window=draft_window,
            main_champions=preferences.get("main_champions") or [],
            preferred_pool=preferences.get("preferred_champion_pool") or [],
            banned=bans,
            limit=3,
        ) if self.coach_service else None
        if not package or not package.recommendations:
            return {"best_ban": None, "ban_recommendations": []}
        return {
            "best_ban": package.recommendations[0],
            "ban_recommendations": package.recommendations,
        }

    def _suggest_bans(self, current_enemy_names, bans, current_pick_name=None, stage="ban", revealed_enemies=None, draft_window=None):
        if not self.coach_service:
            return

        preferences = self.draft_preferences_provider() if self.draft_preferences_provider else {}
        package = self.coach_service.recommend_bans(
            current_enemy_names,
            role=self.my_role,
            stage=stage,
            current_pick=current_pick_name,
            revealed_enemies=revealed_enemies,
            draft_window=draft_window,
            main_champions=preferences.get("main_champions") or [],
            preferred_pool=preferences.get("preferred_champion_pool") or [],
            banned=bans,
            limit=3,
        )
        if not package or not package.recommendations:
            return

        signature = (
            tuple(sorted(current_enemy_names)),
            package.role,
            current_pick_name or "",
            tuple(item.get("champion") for item in package.recommendations),
        )
        if signature == self.last_ban_signature:
            return

        self.last_ban_signature = signature
        self._schedule_draft_pair(
            self._select_ban_primary_call(package.role, package.recommendations[0], current_pick_name),
            None,
            primary_delay=0.5,
        )
        if self.counterpick_callback:
            self.counterpick_callback(
                {
                    "stage": stage,
                    "role": package.role,
                    "enemy_preview": current_enemy_names,
                    "recommendations": [],
                    "best_ban": package.recommendations[0],
                    "ban_recommendations": package.recommendations,
                    "locked_plan": None,
                }
            )

    def reset(self):
        for timer in list(self.pending_timers):
            try:
                timer.cancel()
            except Exception:
                pass
        self.pending_timers.clear()
        self.last_enemy_picks.clear()
        self.my_champ = None
        self.advised_champion_id = None
        self.my_role = None
        self.history_call_sent = False
        self.last_my_hover = None
        self.last_hover_advice_id = None
        self.last_counter_signature = None
        self.last_ban_signature = None
        self.last_locked_signature = None
        self.locked_pick_announced = False
        if self.counterpick_callback:
            self.counterpick_callback(None)
