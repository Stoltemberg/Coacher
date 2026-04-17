import json
import os
import threading
from typing import Any

import requests
from core.app_paths import writable_data_path


class SupabaseAuthService:
    def __init__(self, supabase_url: str | None, anon_key: str | None, storage_path: str | None = None):
        self.supabase_url = (supabase_url or "").rstrip("/")
        self.anon_key = anon_key or ""
        self.storage_path = storage_path or str(writable_data_path("auth_session.json"))
        self._lock = threading.Lock()
        self._session: dict[str, Any] | None = None
        self._user: dict[str, Any] | None = None
        self._message = ""

        storage_dir = os.path.dirname(self.storage_path)
        if storage_dir:
            os.makedirs(storage_dir, exist_ok=True)

        self.load_session()

    def is_configured(self) -> bool:
        return bool(self.supabase_url and self.anon_key)

    def _headers(self, access_token: str | None = None) -> dict[str, str]:
        headers = {
            "apikey": self.anon_key,
            "Content-Type": "application/json",
        }
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        return headers

    def _request(self, method: str, path: str, *, payload: dict[str, Any] | None = None, access_token: str | None = None):
        url = f"{self.supabase_url}{path}"
        response = requests.request(
            method,
            url,
            headers=self._headers(access_token=access_token),
            json=payload,
            timeout=15,
        )
        try:
            data = response.json()
        except ValueError:
            data = {}
        return response, data

    def _persist_session(self):
        if not self._session:
            if os.path.exists(self.storage_path):
                os.remove(self.storage_path)
            return

        with open(self.storage_path, "w", encoding="utf-8") as handle:
            json.dump(self._session, handle, ensure_ascii=False, indent=2)

    def _clear_session(self, message: str = ""):
        self._session = None
        self._user = None
        self._message = message
        self._persist_session()

    def _extract_user(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        if not isinstance(payload, dict):
            return None
        user = payload.get("user") if isinstance(payload.get("user"), dict) else payload
        if not isinstance(user, dict):
            return None
        metadata = user.get("user_metadata") or {}
        display_name = metadata.get("display_name") or metadata.get("name") or user.get("email", "")
        return {
            "id": user.get("id"),
            "email": user.get("email"),
            "display_name": display_name,
            "email_confirmed_at": user.get("email_confirmed_at"),
        }

    def _apply_auth_payload(self, payload: dict[str, Any], *, fallback_message: str):
        session = payload.get("session") if isinstance(payload.get("session"), dict) else None
        if session is None and payload.get("access_token"):
            session = {
                "access_token": payload.get("access_token"),
                "refresh_token": payload.get("refresh_token"),
                "expires_at": payload.get("expires_at"),
            }
        user = self._extract_user(payload)

        if session and user:
            self._session = {
                "access_token": session.get("access_token"),
                "refresh_token": session.get("refresh_token"),
                "expires_at": session.get("expires_at"),
                "user": user,
            }
            self._user = user
            self._message = fallback_message
            self._persist_session()
            return self.snapshot(message=fallback_message)

        self._session = None
        self._user = user
        self._message = fallback_message
        self._persist_session()
        return self.snapshot(message=fallback_message)

    def _error_message(self, response, data: dict[str, Any], fallback: str) -> str:
        if isinstance(data, dict):
            for key in ("msg", "message", "error_description", "error"):
                value = data.get(key)
                if value:
                    return str(value)
        if response is not None and response.status_code == 429:
            return "Muitas tentativas. Espera um pouco e tenta de novo."
        return fallback

    def load_session(self):
        if not self.is_configured():
            self._clear_session("Supabase não configurado.")
            return self.snapshot()

        if not os.path.exists(self.storage_path):
            self._session = None
            self._user = None
            return self.snapshot()

        try:
            with open(self.storage_path, "r", encoding="utf-8") as handle:
                saved = json.load(handle)
        except (OSError, json.JSONDecodeError):
            self._clear_session("Sessão local inválida. Faça login novamente.")
            return self.snapshot()

        access_token = saved.get("access_token")
        if not access_token:
            self._clear_session()
            return self.snapshot()

        try:
            response, data = self._request("get", "/auth/v1/user", access_token=access_token)
        except requests.RequestException:
            self._session = saved
            self._user = saved.get("user")
            self._message = "Sessão local carregada, mas não foi possível validar online."
            return self.snapshot()

        if response.ok:
            user = self._extract_user(data)
            self._session = {
                **saved,
                "user": user,
            }
            self._user = user
            self._message = ""
            self._persist_session()
            return self.snapshot()

        self._clear_session("Sessão expirada. Entre novamente.")
        return self.snapshot()

    def sign_up(self, email: str, password: str, display_name: str | None = None):
        with self._lock:
            if not self.is_configured():
                return self.snapshot(message="Configure SUPABASE_URL e SUPABASE_ANON_KEY para ativar o login.")

            payload = {
                "email": (email or "").strip(),
                "password": password or "",
                "data": {"display_name": (display_name or "").strip()},
            }

            try:
                response, data = self._request("post", "/auth/v1/signup", payload=payload)
            except requests.RequestException:
                return self.snapshot(message="Não consegui falar com o Supabase agora.")

            if not response.ok:
                return self.snapshot(message=self._error_message(response, data, "Não foi possível criar a conta."))

            if data.get("session"):
                return self._apply_auth_payload(data, fallback_message="Conta criada e sessão iniciada.")

            user = self._extract_user(data)
            self._user = user
            self._session = None
            self._message = "Conta criada. Confirme o e-mail para liberar o acesso."
            self._persist_session()
            return self.snapshot()

    def sign_in(self, email: str, password: str):
        with self._lock:
            if not self.is_configured():
                return self.snapshot(message="Configure SUPABASE_URL e SUPABASE_ANON_KEY para ativar o login.")

            payload = {
                "email": (email or "").strip(),
                "password": password or "",
            }

            try:
                response, data = self._request("post", "/auth/v1/token?grant_type=password", payload=payload)
            except requests.RequestException:
                return self.snapshot(message="Não consegui falar com o Supabase agora.")

            if not response.ok:
                return self.snapshot(message=self._error_message(response, data, "E-mail ou senha inválidos."))

            return self._apply_auth_payload(data, fallback_message="Login realizado com sucesso.")

    def sign_out(self):
        with self._lock:
            access_token = (self._session or {}).get("access_token")
            if self.is_configured() and access_token:
                try:
                    self._request("post", "/auth/v1/logout", payload={"scope": "local"}, access_token=access_token)
                except requests.RequestException:
                    pass
            self._clear_session("Sessão encerrada.")
            return self.snapshot()

    def snapshot(self, *, message: str | None = None) -> dict[str, Any]:
        user = self._user or ((self._session or {}).get("user") if self._session else None)
        return {
            "configured": self.is_configured(),
            "authenticated": bool(self._session and self._session.get("access_token") and user),
            "user": user,
            "message": message if message is not None else self._message,
            "pending_confirmation": bool(user and not (user.get("email_confirmed_at") or (self._session or {}).get("access_token"))),
        }
