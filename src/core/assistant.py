import hashlib
import base64
import asyncio
import re
import os
import queue
import subprocess
import threading
import time
import unicodedata
from collections import deque

import pygame
import requests
from core.app_paths import writable_data_path

try:
    import edge_tts
except Exception:  # pragma: no cover - optional dependency at runtime
    edge_tts = None


class VoiceAssistant:
    DEFAULT_VOICE_ID = "hdQlfaVzhr2e2ag3UfX3"
    DEFAULT_MODEL_ID = "eleven_multilingual_v2"
    DEFAULT_STABILITY = 0.30
    DEFAULT_SIMILARITY_BOOST = 0.85
    DEFAULT_STYLE = 0.40
    DEFAULT_USE_SPEAKER_BOOST = True
    DEFAULT_TIMEOUT = 15
    DEFAULT_MAX_QUEUE_SIZE = 5
    DEFAULT_MAX_BATCH_SIZE = 2
    DEFAULT_STALE_SECONDS = 8
    DEFAULT_STANDARD_VOICE = "pt-BR-FranciscaNeural"
    DEFAULT_STANDARD_RATE = "+0%"
    DEFAULT_STANDARD_PITCH = "+0Hz"

    def __init__(self, callback_log=None):
        self.callback_log = callback_log
        self.speech_queue = queue.Queue()
        self.enabled = True
        self.volume = 80
        self.voice_personality = self._env("COACHER_VOICE_PERSONALITY", "minerva").lower()
        self.standard_voice_name = self._env("COACHER_STANDARD_VOICE", self.DEFAULT_STANDARD_VOICE)
        self.standard_voice_rate = self._env("COACHER_STANDARD_VOICE_RATE", self.DEFAULT_STANDARD_RATE)
        self.standard_voice_pitch = self._env("COACHER_STANDARD_VOICE_PITCH", self.DEFAULT_STANDARD_PITCH)

        self.api_key = self._env("ELEVENLABS_API_KEY")
        self.voice_id = self._env("ELEVENLABS_VOICE_ID", self.DEFAULT_VOICE_ID)
        self.model_id = self._env("ELEVENLABS_MODEL_ID", self.DEFAULT_MODEL_ID)
        self.timeout = self._env_float("ELEVENLABS_TIMEOUT", self.DEFAULT_TIMEOUT)
        self.voice_settings = {
            "stability": self._env_float("ELEVENLABS_STABILITY", self.DEFAULT_STABILITY),
            "similarity_boost": self._env_float(
                "ELEVENLABS_SIMILARITY_BOOST", self.DEFAULT_SIMILARITY_BOOST
            ),
            "style": self._env_float("ELEVENLABS_STYLE", self.DEFAULT_STYLE),
            "use_speaker_boost": self._env_bool(
                "ELEVENLABS_USE_SPEAKER_BOOST", self.DEFAULT_USE_SPEAKER_BOOST
            ),
        }
        self.tts_ready = bool(self.api_key and self.voice_id)
        self.audio_ready = self._init_audio()
        self._warned_missing_tts_config = False
        self._warned_audio_init = False
        self._warned_tts_budget = False
        self._warned_standard_tts = False
        self.tts_mode = self._env("COACHER_TTS_MODE", "smart").lower()
        self.tts_session_char_budget = int(self._env_float("COACHER_TTS_SESSION_CHAR_BUDGET", 0))
        self.tts_session_chars_used = 0
        self.allowed_tts_categories = set()
        self._recent_texts = {}
        self._last_spoken_by_category = {}
        self.max_queue_size = int(self._env_float("COACHER_TTS_MAX_QUEUE_SIZE", self.DEFAULT_MAX_QUEUE_SIZE))
        self.max_batch_size = int(self._env_float("COACHER_TTS_MAX_BATCH_SIZE", self.DEFAULT_MAX_BATCH_SIZE))
        self.stale_seconds = float(self._env_float("COACHER_TTS_STALE_SECONDS", self.DEFAULT_STALE_SECONDS))
        self.category_tts_cooldowns = {
            "macro": 180,
            "minimap": 180,
            "draft": 45,
            "lane_matchup": 60,
            "build_plan": 90,
            "item_advice": 75,
        }

        self.cache_dir = str(writable_data_path("cache"))
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        self.worker_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.worker_thread.start()

    def set_volume(self, value):
        self.volume = max(0, min(100, int(value)))
        if not self.audio_ready:
            return
        vol = max(0.0, min(1.0, self.volume / 100.0))
        pygame.mixer.music.set_volume(vol)

    def set_enabled(self, enabled):
        self.enabled = bool(enabled)

    def set_tts_mode(self, mode):
        normalized = str(mode or "smart").strip().lower()
        if normalized not in {"smart", "minimal", "off"}:
            normalized = "smart"
        self.tts_mode = normalized

    def set_voice_personality(self, personality):
        normalized = str(personality or "minerva").strip().lower()
        if normalized not in {"minerva", "standard"}:
            normalized = "minerva"
        self.voice_personality = normalized

    def set_allowed_categories(self, categories=None):
        if not categories:
            self.allowed_tts_categories = set()
            return
        self.allowed_tts_categories = {
            str(category).strip().lower()
            for category in categories
            if str(category or "").strip()
        }

    def say(self, text, event_type="neutral", category=None):
        display_text = self._prepare_display_text(text)
        if self.callback_log:
            self.callback_log(display_text, event_type, category)
        if not self.enabled:
            return
        spoken_text = self._prepare_tts_text(display_text)
        if not self._should_enqueue_tts(spoken_text, event_type, category):
            return
        payload = {
            "text": spoken_text,
            "event_type": event_type,
            "category": category,
            "priority": self._message_priority(event_type, category),
            "created_at": time.monotonic(),
        }
        self._maybe_trim_queue(payload["priority"])
        if self.speech_queue.qsize() >= self.max_queue_size and payload["priority"] < 3:
            return
        self.speech_queue.put(payload)

    def _should_enqueue_tts(self, text, event_type, category):
        normalized_text = (text or "").strip()
        if not normalized_text:
            return False

        now = time.monotonic()
        last_seen = self._recent_texts.get(normalized_text)
        if last_seen and now - last_seen < 90:
            return False

        category_key = (category or "").strip().lower()
        if self.allowed_tts_categories and category_key and category_key not in self.allowed_tts_categories:
            return False

        cooldown = self.category_tts_cooldowns.get(category_key)
        if cooldown:
            last_category_time = self._last_spoken_by_category.get(category_key, 0.0)
            if now - last_category_time < cooldown:
                return False

        if self.tts_mode == "off":
            return False

        if self.tts_mode == "minimal":
            important_categories = {
                "item_advice",
                "self_death",
                "self_kill",
                "multikill",
                "dragon",
                "baron",
                "herald",
                "horde",
                "inhibitor",
                "turret",
            }
            if event_type not in {"negative", "positive"} and category_key not in important_categories:
                return False

        if self.tts_mode == "smart":
            spoken_categories = {
                "lane_matchup",
                "build_plan",
                "item_advice",
                "self_death",
                "self_kill",
                "multikill",
                "dragon",
                "baron",
                "herald",
                "horde",
                "inhibitor",
                "turret",
                "recovery",
            }
            if event_type == "neutral" and category_key not in spoken_categories:
                return False

        self._recent_texts[normalized_text] = now
        if category_key:
            self._last_spoken_by_category[category_key] = now
        return True

    def _message_priority(self, event_type, category):
        event_key = str(event_type or "").strip().lower()
        category_key = str(category or "").strip().lower()
        if event_key in {"urgent", "negative"}:
            return 4
        if category_key in {"dragon", "baron", "herald", "horde", "inhibitor", "adaptive_feedback"}:
            return 4
        if event_key == "positive":
            return 3
        if category_key in {"self_kill", "self_death", "item_advice", "build_plan", "lane_matchup"}:
            return 3
        if category_key in {"macro", "minimap", "assist"}:
            return 1
        return 2

    def _maybe_trim_queue(self, incoming_priority):
        with self.speech_queue.mutex:
            original = list(self.speech_queue.queue)
            if not original:
                return

            now = time.monotonic()
            kept = deque()
            removed = 0
            for item in original:
                created_at = float(item.get("created_at", now))
                priority = int(item.get("priority", 0))
                is_stale = (now - created_at) > self.stale_seconds
                should_drop = is_stale or (
                    len(original) >= self.max_queue_size and priority < incoming_priority and priority <= 2
                )
                if should_drop:
                    removed += 1
                    continue
                kept.append(item)

            if removed:
                self.speech_queue.queue.clear()
                self.speech_queue.queue.extend(kept)
                self.speech_queue.unfinished_tasks = max(0, self.speech_queue.unfinished_tasks - removed)

    def _prepare_tts_text(self, text):
        normalized = self._prepare_display_text(text)
        if not normalized:
            return ""

        normalized = unicodedata.normalize("NFC", normalized)
        normalized = normalized.replace("\n", " ").replace("\r", " ").replace("\t", " ")
        normalized = normalized.replace("·", ", ").replace("•", ", ").replace("—", ", ").replace("–", ", ")
        normalized = normalized.replace("...", ", ")
        normalized = normalized.replace("..", ", ")
        normalized = re.sub(r"[;:]+", ", ", normalized)
        normalized = re.sub(r"[|/\\]+", ", ", normalized)
        normalized = re.sub(r"[\(\)\[\]\{\}\"“”'`]+", "", normalized)
        normalized = re.sub(r"[!?]{2,}", "!", normalized)
        normalized = re.sub(r"\.{2,}", ".", normalized)
        normalized = re.sub(r",\s*,+", ", ", normalized)
        normalized = re.sub(r"([!?])\s*,", r"\1", normalized)
        normalized = re.sub(r"\s*([,.!?])\s*", r"\1 ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip(" ,.")
        return normalized


    def _prepare_display_text(self, text):
        normalized = self._repair_common_mojibake(str(text or "").strip())
        if not normalized:
            return ""

        normalized = unicodedata.normalize("NFC", normalized)
        normalized = self._restore_common_pt_br_accents(normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    def _repair_common_mojibake(self, text):
        replacements = {
            "Ã¡": "á",
            "Ã ": "à",
            "Ã¢": "â",
            "Ã£": "ã",
            "Ã©": "é",
            "Ãª": "ê",
            "Ã­": "í",
            "Ã³": "ó",
            "Ã´": "ô",
            "Ãµ": "õ",
            "Ãº": "ú",
            "Ã§": "ç",
            "Ã": "Á",
            "Ã‰": "É",
            "Ã": "Í",
            "Ã“": "Ó",
            "Ãš": "Ú",
            "Ã‡": "Ç",
            "Â·": ",",
            "Â": "",
        }
        fixed = text
        for broken, repaired in replacements.items():
            fixed = fixed.replace(broken, repaired)
        return fixed

    def _restore_common_pt_br_accents(self, text):
        word_map = {
            "area": "\u00e1rea",
            "ate": "at\u00e9",
            "audio": "\u00e1udio",
            "barao": "bar\u00e3o",
            "cabeca": "cabe\u00e7a",
            "campeoes": "campe\u00f5es",
            "cenario": "cen\u00e1rio",
            "comeca": "come\u00e7a",
            "comecar": "come\u00e7ar",
            "comeco": "come\u00e7o",
            "comecou": "come\u00e7ou",
            "condicao": "condi\u00e7\u00e3o",
            "confianca": "confian\u00e7a",
            "contencao": "conten\u00e7\u00e3o",
            "correcao": "corre\u00e7\u00e3o",
            "critico": "cr\u00edtico",
            "criticos": "cr\u00edticos",
            "decisao": "decis\u00e3o",
            "dragao": "drag\u00e3o",
            "enrolacao": "enrola\u00e7\u00e3o",
            "entao": "ent\u00e3o",
            "espaco": "espa\u00e7o",
            "execucao": "execu\u00e7\u00e3o",
            "familias": "fam\u00edlias",
            "funcao": "fun\u00e7\u00e3o",
            "historico": "hist\u00f3rico",
            "informacao": "informa\u00e7\u00e3o",
            "ja": "j\u00e1",
            "malicia": "mal\u00edcia",
            "memoria": "mem\u00f3ria",
            "nao": "n\u00e3o",
            "numero": "n\u00famero",
            "patetica": "pat\u00e9tica",
            "patetico": "pat\u00e9tico",
            "posicao": "posi\u00e7\u00e3o",
            "posicoes": "posi\u00e7\u00f5es",
            "preguica": "pregui\u00e7a",
            "proxima": "pr\u00f3xima",
            "proximo": "pr\u00f3ximo",
            "proximos": "pr\u00f3ximos",
            "recuperacao": "recupera\u00e7\u00e3o",
            "regiao": "regi\u00e3o",
            "relogio": "rel\u00f3gio",
            "rotacao": "rota\u00e7\u00e3o",
            "sequencia": "sequ\u00eancia",
            "so": "s\u00f3",
            "tambem": "tamb\u00e9m",
            "ta": "t\u00e1",
            "ultimas": "\u00faltimas",
            "ultimo": "\u00faltimo",
            "ultimos": "\u00faltimos",
            "util": "\u00fatil",
            "voce": "voc\u00ea",
            "voces": "voc\u00eas",
            "visao": "vis\u00e3o",
            "vitoria": "vit\u00f3ria",
        }

        def replace_token(match):
            token = match.group(0)
            replacement = word_map.get(token.lower())
            if not replacement:
                return token
            if token.isupper():
                return replacement.upper()
            if token[:1].isupper():
                return replacement.capitalize()
            return replacement

        return re.sub(r"\b[\w?-?]+\b", replace_token, text, flags=re.UNICODE)

    def _speech_worker(self):
        while True:
            item = self.speech_queue.get()
            if item is None:
                break

            collected_items = [item]

            while True:
                try:
                    next_item = self.speech_queue.get(timeout=0.15)
                    if next_item is None:
                        break
                    collected_items.append(next_item)
                    if len(collected_items) >= self.max_batch_size:
                        break
                except queue.Empty:
                    break

            if len(collected_items) > 1:
                final_text = collected_items[0]["text"]
                for next_payload in collected_items[1:]:
                    connector = " Alem disso, "
                    if next_payload["event_type"] in {"negative", "urgent"}:
                        connector = " E presta atencao nisto, "
                    elif next_payload["event_type"] == "positive":
                        connector = " E tem mais uma boa, "
                    final_text += connector + next_payload["text"]
            else:
                final_text = collected_items[0]["text"]

            if self.voice_personality == "standard":
                try:
                    if not self._speak_with_standard_voice(final_text) and not self._warned_standard_tts:
                        print("[Voz] TTS padrao indisponivel nesta maquina.")
                        self._warned_standard_tts = True
                except Exception as e:
                    if not self._warned_standard_tts:
                        print(f"[Voz] Erro no TTS padrao: {e}")
                        self._warned_standard_tts = True
                finally:
                    for _ in collected_items:
                        self.speech_queue.task_done()
                continue

            if not self.tts_ready:
                if not self._warned_missing_tts_config:
                    print(
                        "[Voz] TTS desativado: defina ELEVENLABS_API_KEY no ambiente para reativar a fala."
                    )
                    self._warned_missing_tts_config = True
                for _ in collected_items:
                    self.speech_queue.task_done()
                continue

            if not self.audio_ready:
                if not self._warned_audio_init:
                    print("[Voz] TTS em espera: pygame.mixer nao inicializou nesta maquina.")
                    self._warned_audio_init = True
                for _ in collected_items:
                    self.speech_queue.task_done()
                continue

            text_hash = hashlib.md5(final_text.encode("utf-8")).hexdigest()
            cache_path = os.path.join(self.cache_dir, f"{text_hash}.mp3")

            try:
                if not os.path.exists(cache_path):
                    if (
                        self.tts_session_char_budget > 0
                        and (self.tts_session_chars_used + len(final_text)) > self.tts_session_char_budget
                    ):
                        if not self._warned_tts_budget:
                            print("[Voz] Orcamento de TTS da sessao atingido. O audio segue desligado para economizar creditos.")
                            self._warned_tts_budget = True
                        for _ in collected_items:
                            self.speech_queue.task_done()
                        continue

                    url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
                    headers = {
                        "Accept": "audio/mpeg",
                        "Content-Type": "application/json",
                        "xi-api-key": self.api_key,
                    }
                    data = {
                        "text": final_text,
                        "model_id": self.model_id,
                        "voice_settings": self.voice_settings,
                    }

                    resp = requests.post(url, json=data, headers=headers, timeout=self.timeout)
                    if resp.status_code == 200:
                        with open(cache_path, "wb") as f:
                            for chunk in resp.iter_content(chunk_size=1024):
                                if chunk:
                                    f.write(chunk)
                        self.tts_session_chars_used += len(final_text)
                    else:
                        print(f"[ElevenLabs API] Erro: {resp.text}")
                        for _ in collected_items:
                            self.speech_queue.task_done()
                        continue

                pygame.mixer.music.load(cache_path)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)

            except Exception as e:
                print(f"[Voz] Erro reproduzindo Audio: {e}")
            finally:
                try:
                    pygame.mixer.music.unload()
                except Exception:
                    pass

            for _ in collected_items:
                self.speech_queue.task_done()

    def _speak_with_system_voice(self, text):
        normalized = self._prepare_display_text(text)
        if not normalized:
            return True

        payload = base64.b64encode(normalized.encode("utf-8")).decode("ascii")
        script = (
            "Add-Type -AssemblyName System.Speech;"
            f"$text=[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('{payload}'));"
            "$speaker=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
            f"$speaker.Volume={int(self.volume)};"
            "$speaker.Rate=0;"
            "$speaker.Speak($text);"
            "$speaker.Dispose();"
        )
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            capture_output=True,
            text=True,
            timeout=self.timeout + 10,
            check=False,
        )
        return completed.returncode == 0

    def _speak_with_standard_voice(self, text):
        if edge_tts is not None and self.audio_ready:
            if self._speak_with_edge_tts(text):
                return True
        return self._speak_with_system_voice(text)

    def _speak_with_edge_tts(self, text):
        normalized = self._prepare_display_text(text)
        if not normalized:
            return True

        cache_key = hashlib.md5(
            f"standard::{self.standard_voice_name}::{self.standard_voice_rate}::{self.standard_voice_pitch}::{normalized}".encode("utf-8")
        ).hexdigest()
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.mp3")

        try:
            if not os.path.exists(cache_path):
                asyncio.run(self._generate_edge_tts_audio(normalized, cache_path))

            pygame.mixer.music.load(cache_path)
            pygame.mixer.music.set_volume(max(0.0, min(1.0, self.volume / 100.0)))
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            return True
        except Exception:
            return False
        finally:
            try:
                pygame.mixer.music.unload()
            except Exception:
                pass

    async def _generate_edge_tts_audio(self, text, cache_path):
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.standard_voice_name,
            rate=self.standard_voice_rate,
            pitch=self.standard_voice_pitch,
        )
        await communicate.save(cache_path)

    def _init_audio(self):
        try:
            pygame.mixer.init()
            return True
        except Exception as exc:
            print(f"[Voz] pygame.mixer indisponivel: {exc}")
            return False

    def _env(self, name, default=None):
        value = os.getenv(name)
        if value is None:
            return default
        value = value.strip()
        return value if value else default

    def _env_float(self, name, default):
        value = self._env(name)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            return default

    def _env_bool(self, name, default):
        value = self._env(name)
        if value is None:
            return default
        normalized = value.lower()
        if normalized in {"1", "true", "yes", "y", "on"}:
            return True
        if normalized in {"0", "false", "no", "n", "off"}:
            return False
        return default
