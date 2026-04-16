import hashlib
import os
import queue
import threading

import pygame
import requests


class VoiceAssistant:
    DEFAULT_VOICE_ID = "hdQlfaVzhr2e2ag3UfX3"
    DEFAULT_MODEL_ID = "eleven_multilingual_v2"
    DEFAULT_STABILITY = 0.30
    DEFAULT_SIMILARITY_BOOST = 0.85
    DEFAULT_STYLE = 0.40
    DEFAULT_USE_SPEAKER_BOOST = True
    DEFAULT_TIMEOUT = 15

    def __init__(self, callback_log=None):
        self.callback_log = callback_log
        self.speech_queue = queue.Queue()
        self.enabled = True

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

        self.cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        self.worker_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.worker_thread.start()

    def set_volume(self, value):
        if not self.audio_ready:
            return
        vol = max(0.0, min(1.0, value / 100.0))
        pygame.mixer.music.set_volume(vol)

    def set_enabled(self, enabled):
        self.enabled = bool(enabled)

    def say(self, text, event_type="neutral", category=None):
        if self.callback_log:
            self.callback_log(text, "urgent", category)
        if not self.enabled:
            return
        self.speech_queue.put((text, event_type, category))

    def _speech_worker(self):
        import random

        while True:
            item = self.speech_queue.get()
            if item is None:
                break

            text, e_type, category = item
            collected_items = [(text, e_type, category)]

            while True:
                try:
                    next_item = self.speech_queue.get(timeout=1.0)
                    if next_item is None:
                        break
                    collected_items.append(next_item)
                    if len(collected_items) >= 3:
                        break
                except queue.Empty:
                    break

            if len(collected_items) > 1:
                final_text = collected_items[0][0]
                prev_type = collected_items[0][1]

                for i in range(1, len(collected_items)):
                    curr_text, curr_type, _ = collected_items[i]

                    if prev_type == "positive" and curr_type == "positive":
                        bridge = random.choice([
                            "... e pra melhorar, mano: ",
                            "... ah, e nao para por ai, parceiro: ",
                            "... e quer mais maravilha? Toma: ",
                        ])
                    elif prev_type == "negative" and curr_type == "negative":
                        bridge = random.choice([
                            "... pior do que isso caralho, ",
                            "... e quer mais desgraca? Toma: ",
                            "... pra foder logo de vez: ",
                        ])
                    elif prev_type == "positive" and curr_type == "negative":
                        bridge = random.choice([
                            "... mas nem tudo sao flores, deu merda la: ",
                            "... foda que do outro lado o bagulho ta doido: ",
                            "... mas calma, olha a bad news: ",
                        ])
                    elif prev_type == "negative" and curr_type == "positive":
                        bridge = random.choice([
                            "... mas pra nao chorar de vez o: ",
                            "... pelo menos tem uma noticia boa: ",
                            "... mas olha o lado positivo da coisa: ",
                        ])
                    else:
                        bridge = random.choice([
                            "... alem disso, papo reto: ",
                            "... e tem mais essa fita o: ",
                            "... detalhe: ",
                        ])

                    final_text += bridge + curr_text
                    prev_type = curr_type
            else:
                final_text = collected_items[0][0]

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
