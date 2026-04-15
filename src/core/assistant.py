import threading
import tempfile
import os
import pygame
import queue
import requests
import hashlib

class VoiceAssistant:
    def __init__(self, callback_log=None):
        self.callback_log = callback_log
        self.speech_queue = queue.Queue()
        
        # ElevenLabs Settings
        self.api_key = "sk_d346bcbe872f30ac835ba58881c56cc2348de040be9c860d"
        # Voz: Clone Customizado do Streamer Minerva
        self.voice_id = "hdQlfaVzhr2e2ag3UfX3" 
        
        # Inicializa o mixer num nível de sistema simples
        pygame.mixer.init()
        
        # Cria infra de Cache persistente
        self.cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        # Worker dedicado a falar em sequência (nunca corta falas)
        self.worker_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.worker_thread.start()

    def set_volume(self, value):
        vol = max(0.0, min(1.0, value / 100.0))
        pygame.mixer.music.set_volume(vol)

    def say(self, text, event_type="neutral"):
        if self.callback_log:
            self.callback_log(text, "urgent")
        self.speech_queue.put((text, event_type))

    def _speech_worker(self):
        import random
        while True:
            item = self.speech_queue.get()
            if item is None:
                break
                
            text, e_type = item
            collected_items = [(text, e_type)]
            
            # Buffer de aglomeração! Espera até 1.0s visando resgatar textos acoplados
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
            
            # Sistema de Pontes Naturais Semânticas (Bridge Words)
            if len(collected_items) > 1:
                final_text = collected_items[0][0]
                prev_type = collected_items[0][1]
                
                for i in range(1, len(collected_items)):
                    curr_text, curr_type = collected_items[i]
                    
                    if prev_type == "positive" and curr_type == "positive":
                        bridge = random.choice([
                            "... e pra melhorar, mano: ",
                            "... ah, e não para por aí, parceiro: ",
                            "... e quer mais maravilha? Toma: "
                        ])
                    elif prev_type == "negative" and curr_type == "negative":
                        bridge = random.choice([
                            "... pior do que isso caralho, ",
                            "... e quer mais desgraça? Toma: ",
                            "... pra foder logo de vez: "
                        ])
                    elif prev_type == "positive" and curr_type == "negative":
                        bridge = random.choice([
                            "... mas nem tudo são flores, deu merda lá: ",
                            "... foda que do outro lado o bagulho tá doido: ",
                            "... mas calma, olha a bad news: "
                        ])
                    elif prev_type == "negative" and curr_type == "positive":
                        bridge = random.choice([
                            "... mas pra não chorar de vez ó: ",
                            "... pelo menos tem uma notícia boa: ",
                            "... mas olha o lado positivo da coisa: "
                        ])
                    else: # neutral mixes
                        bridge = random.choice([
                            "... além disso, papo reto: ",
                            "... e tem mais essa fita ó: ",
                            "... detalhe: "
                        ])
                        
                    final_text += bridge + curr_text
                    prev_type = curr_type
            else:
                final_text = collected_items[0][0]
                
            # Geração de Hash para Cache Local
            text_hash = hashlib.md5(final_text.encode('utf-8')).hexdigest()
            cache_path = os.path.join(self.cache_dir, f"{text_hash}.mp3")
            
            try:
                # Checa se o áudio já foi gerado na história dessa base
                if not os.path.exists(cache_path):
                    # Requisição síncrona robusta para ElevenLabs
                    url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
                    headers = {
                        "Accept": "audio/mpeg",
                        "Content-Type": "application/json",
                        "xi-api-key": self.api_key
                    }
                    data = {
                        "text": final_text,
                        "model_id": "eleven_multilingual_v2", 
                        "voice_settings": {
                            "stability": 0.30,
                            "similarity_boost": 0.85,
                            "style": 0.40,
                            "use_speaker_boost": True
                        }
                    }
                    
                    resp = requests.post(url, json=data, headers=headers, timeout=15)
                    if resp.status_code == 200:
                        with open(cache_path, 'wb') as f:
                            for chunk in resp.iter_content(chunk_size=1024):
                                if chunk:
                                    f.write(chunk)
                    else:
                        print(f"[ElevenLabs API] Erro: {resp.text}")
                        # Finaliza task e pula pois falhou
                        for _ in collected_items:
                            self.speech_queue.task_done()
                        continue
                
                # Executa direto do Cache (latência ultra baixa!)
                pygame.mixer.music.load(cache_path)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                    
            except Exception as e:
                print(f"[Voz] Erro reproduzindo Áudio: {e}")
            finally:
                pygame.mixer.music.unload()
            
            # Confirma consumo pra tudo no buffer
            for _ in collected_items:
                self.speech_queue.task_done()

