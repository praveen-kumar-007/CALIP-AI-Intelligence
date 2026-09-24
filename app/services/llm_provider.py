from __future__ import annotations

import json
import logging
import os
import re
from typing import Any
import requests

from app.core.config import settings

logger = logging.getLogger("calip.llm_provider")


class LLMProvider:
    """
    Universal High-Performance Production LLM Provider.
    Supports:
    1. Groq Cloud API (Recommended for production: 100% Free tier, 500-800 tokens/sec)
    2. NVIDIA NIM API (build.nvidia.com - Free credits)
    3. Google Gemini API (Free tier, 1M context window)
    4. Local Ollama (Local developer GPU setup)
    5. Deterministic Legal Engine (Sub-5ms, zero external dependencies, 100% uptime)
    """

    @classmethod
    def get_active_provider(cls) -> str:
        configured = getattr(settings, "LLM_PROVIDER", "auto").lower()
        if configured != "auto":
            return configured

        # Auto-detection priority:
        if getattr(settings, "GROQ_API_KEY", "") or os.getenv("GROQ_API_KEY"):
            return "groq"
        if getattr(settings, "NVIDIA_API_KEY", "") or os.getenv("NVIDIA_API_KEY"):
            return "nvidia"
        if getattr(settings, "GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY"):
            return "gemini"

        return "extractive"

    @classmethod
    def get_model_name(cls) -> str:
        provider = cls.get_active_provider()
        if provider == "nvidia":
            return getattr(settings, "NVIDIA_MODEL", "mistralai/mistral-nemotron")
        elif provider == "groq":
            return getattr(settings, "GROQ_MODEL", "qwen/qwen3.8-27b")
        elif provider == "gemini":
            return getattr(settings, "GEMINI_MODEL", "gemini-2.0-flash")
        elif provider == "ollama":
            return getattr(settings, "OLLAMA_MODEL", "qwen3:8b")
        return "Deterministic Legal Engine"

    @classmethod
    def query(
        cls,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        timeout: int = 60,
    ) -> str | None:
        """Executes query through the active production or local provider with seamless fallback."""
        primary = cls.get_active_provider()

        # Try designated primary provider first:
        if primary == "nvidia":
            res = cls._query_nvidia(prompt, system_prompt, temperature, max_tokens, timeout)
            if res:
                return res
        elif primary == "groq":
            res = cls._query_groq(prompt, system_prompt, temperature, max_tokens, timeout)
            if res:
                return res
        elif primary == "gemini":
            res = cls._query_gemini(prompt, system_prompt, temperature, max_tokens, timeout)
            if res:
                return res
        elif primary == "ollama":
            res = cls._query_ollama(prompt, system_prompt, temperature, timeout)
            if res:
                return res

        # Automatic fallback chain if primary was unavailable
        for fallback_fn in [cls._query_nvidia, cls._query_groq, cls._query_gemini]:
            try:
                res = fallback_fn(prompt, system_prompt, temperature, max_tokens, min(timeout, 35))
                if res:
                    return res
            except Exception:
                continue

        return None

    @classmethod
    def _query_groq(
        cls,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int,
        timeout: int,
    ) -> str | None:
        """
        Groq Cloud API inference:
        Free tier: 30 requests/min, 14,400 requests/day, 500-800 tokens/sec.
        Endpoint: https://api.groq.com/openai/v1/chat/completions
        """
        api_key = getattr(settings, "GROQ_API_KEY", "") or os.getenv("GROQ_API_KEY")
        if not api_key:
            return None

        model = getattr(settings, "GROQ_MODEL", "llama-3.3-70b-versatile")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 0.9,
        }

        try:
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=timeout,
            )
            if res.status_code == 200:
                data = res.json()
                choices = data.get("choices", [])
                if choices:
                    return choices[0]["message"]["content"].strip()
            else:
                logger.warning(f"Groq API error {res.status_code}: {res.text}")
        except Exception as exc:
            logger.error(f"Groq request failed: {exc}")

        return None

    @classmethod
    def _query_nvidia(
        cls,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int,
        timeout: int,
    ) -> str | None:
        """
        NVIDIA NIM API inference:
        Endpoint: https://integrate.api.nvidia.com/v1/chat/completions
        """
        api_key = getattr(settings, "NVIDIA_API_KEY", "") or os.getenv("NVIDIA_API_KEY")
        if not api_key:
            return None

        model = getattr(settings, "NVIDIA_MODEL", "mistralai/mistral-nemotron")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            res = requests.post(
                "https://integrate.api.nvidia.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=timeout,
            )
            if res.status_code == 200:
                data = res.json()
                choices = data.get("choices", [])
                if choices:
                    return choices[0]["message"]["content"].strip()
            else:
                logger.warning(f"NVIDIA API error {res.status_code}: {res.text}")
        except Exception as exc:
            logger.error(f"NVIDIA request failed: {exc}")

        return None

    @classmethod
    def _query_gemini(
        cls,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int,
        timeout: int,
    ) -> str | None:
        """
        Google Gemini API:
        Free tier: 15 RPM, 1M context.
        Endpoint: https://generativelanguage.googleapis.com/v1beta/openai/chat/completions
        """
        api_key = getattr(settings, "GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None

        model = getattr(settings, "GEMINI_MODEL", "gemini-2.0-flash")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            res = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
                headers=headers,
                json=payload,
                timeout=timeout,
            )
            if res.status_code == 200:
                data = res.json()
                choices = data.get("choices", [])
                if choices:
                    return choices[0]["message"]["content"].strip()
            else:
                logger.warning(f"Gemini API error {res.status_code}: {res.text}")
        except Exception as exc:
            logger.error(f"Gemini request failed: {exc}")

        return None

    @classmethod
    def _query_ollama(
        cls,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        timeout: int,
    ) -> str | None:
        """Local Ollama instance fallback."""
        url = getattr(settings, "OLLAMA_GENERATE_URL", "http://127.0.0.1:11434/api/generate")
        model = getattr(settings, "OLLAMA_MODEL", "qwen3:8b")

        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.9,
            },
        }

        # Cap Ollama timeout to 6 seconds max so it never blocks the pipeline
        effective_timeout = min(timeout, 6)
        try:
            res = requests.post(url, json=payload, timeout=effective_timeout)
            if res.status_code == 200:
                return res.json().get("response", "").strip()
        except Exception as exc:
            logger.warning(f"Ollama call warning: {exc}")

        return None


def query_llm(
    prompt: str,
    system_prompt: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 2048,
    timeout: int = 60,
) -> str | None:
    """Convenience functional wrapper around LLMProvider."""
    return LLMProvider.query(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
    )


def get_active_model_name() -> str:
    """Returns human-readable name of active model & provider."""
    provider = LLMProvider.get_active_provider()
    model = LLMProvider.get_model_name()
    if provider == "groq":
        return f"{model} (Groq Ultra-Fast LPU)"
    elif provider == "nvidia":
        return f"{model} (NVIDIA NIM)"
    elif provider == "gemini":
        return f"{model} (Google Gemini Flash)"
    elif provider == "ollama":
        return f"{model} (Local Ollama)"
    return "Deterministic Legal Engine (Built-in)"
