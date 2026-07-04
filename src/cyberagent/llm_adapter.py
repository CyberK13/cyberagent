"""LLM adapters — bring your own key, any provider.

The whole chain only needs one capability from an LLM:

    async def complete(self, system: str, user: str) -> str

Concrete adapters wrap each provider's SDK and import it lazily, so installing
cyberagent does not drag in every LLM SDK. Use the factory helpers or pass a
provider name to AnalystChain:

    AnalystChain(llm="gemini", api_key="...")
    AnalystChain(llm=LLMAdapter.openai(api_key="sk-..."))
    AnalystChain(llm=MyCustomAdapter())
"""

from __future__ import annotations

import abc
import os
from typing import Optional

DEFAULT_MODELS = {
    "openai": "gpt-4o",
    "gemini": "gemini-2.5-pro",
    "claude": "claude-sonnet-4-5",
    "deepseek": "deepseek-chat",
}


class LLMAdapter(abc.ABC):
    """Abstract base. Implement `complete` to plug in any model."""

    name: str = "custom"
    #: True only when the adapter can verify facts via live web search (e.g.
    #: Gemini grounding). Prompts adapt: non-search models are told to rely on
    #: the injected live data block and to flag memory-based claims as stale.
    supports_search: bool = False

    @abc.abstractmethod
    async def complete(self, system: str, user: str) -> str:
        """Return the model's text completion for a system + user prompt."""
        raise NotImplementedError

    # ---- factory helpers -------------------------------------------------
    @staticmethod
    def openai(api_key: Optional[str] = None, model: Optional[str] = None, **kw) -> "OpenAIAdapter":
        return OpenAIAdapter(api_key=api_key, model=model, **kw)

    @staticmethod
    def gemini(api_key: Optional[str] = None, model: Optional[str] = None, **kw) -> "GeminiAdapter":
        return GeminiAdapter(api_key=api_key, model=model, **kw)

    @staticmethod
    def claude(api_key: Optional[str] = None, model: Optional[str] = None, **kw) -> "ClaudeAdapter":
        return ClaudeAdapter(api_key=api_key, model=model, **kw)

    @staticmethod
    def deepseek(api_key: Optional[str] = None, model: Optional[str] = None, **kw) -> "DeepSeekAdapter":
        return DeepSeekAdapter(api_key=api_key, model=model, **kw)


class OpenAIAdapter(LLMAdapter):
    name = "openai"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None,
                 base_url: Optional[str] = None, temperature: float = 0.7):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL") or DEFAULT_MODELS["openai"]
        self.base_url = base_url
        self.temperature = temperature

    async def complete(self, system: str, user: str) -> str:
        try:
            from openai import AsyncOpenAI
        except ImportError as e:  # pragma: no cover
            raise ImportError("OpenAI provider needs `pip install 'cyberagent[openai]'`") from e
        client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        resp = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=self.temperature,
        )
        return resp.choices[0].message.content or ""


class DeepSeekAdapter(OpenAIAdapter):
    """DeepSeek is OpenAI-API compatible."""

    name = "deepseek"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, **kw):
        super().__init__(
            api_key=api_key or os.getenv("DEEPSEEK_API_KEY"),
            model=model or os.getenv("DEEPSEEK_MODEL") or DEFAULT_MODELS["deepseek"],
            base_url=kw.pop("base_url", "https://api.deepseek.com"),
            **kw,
        )


class GeminiAdapter(LLMAdapter):
    """Gemini adapter. ``grounding=True`` enables real-time Google Search
    grounding — the framework's default way to verify current facts (prices,
    capacity, lead-times, consensus) instead of relying on model memory."""

    name = "gemini"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None,
                 temperature: float = 0.7, grounding: bool = True):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GOOGLE_MODEL") or DEFAULT_MODELS["gemini"]
        self.temperature = temperature
        self.grounding = grounding
        self.supports_search = grounding

    async def complete(self, system: str, user: str) -> str:
        try:
            from google import genai
            from google.genai import types
        except ImportError as e:  # pragma: no cover
            raise ImportError("Gemini provider needs `pip install 'cyberagent[gemini]'`") from e
        client = genai.Client(api_key=self.api_key)
        cfg_kw = dict(system_instruction=system, temperature=self.temperature)
        if self.grounding:
            try:
                cfg_kw["tools"] = [types.Tool(google_search=types.GoogleSearch())]
            except Exception:  # pragma: no cover — older SDK without GoogleSearch
                pass
        resp = await client.aio.models.generate_content(
            model=self.model,
            contents=user,
            config=types.GenerateContentConfig(**cfg_kw),
        )
        return resp.text or ""


class ClaudeAdapter(LLMAdapter):
    name = "claude"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None,
                 temperature: float = 0.7, max_tokens: int = 4096):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model or os.getenv("ANTHROPIC_MODEL") or DEFAULT_MODELS["claude"]
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def complete(self, system: str, user: str) -> str:
        try:
            from anthropic import AsyncAnthropic
        except ImportError as e:  # pragma: no cover
            raise ImportError("Claude provider needs `pip install 'cyberagent[claude]'`") from e
        client = AsyncAnthropic(api_key=self.api_key)
        resp = await client.messages.create(
            model=self.model,
            system=system,
            messages=[{"role": "user", "content": user}],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        return "".join(block.text for block in resp.content if getattr(block, "type", "") == "text")


class MockLLM(LLMAdapter):
    """Offline adapter for tests/examples — echoes a deterministic stub so the
    chain can run end-to-end without any API key or network."""

    name = "mock"

    def __init__(self, reply: Optional[str] = None):
        self.reply = reply

    async def complete(self, system: str, user: str) -> str:
        if self.reply is not None:
            return self.reply
        head = user.strip().splitlines()[0][:80] if user.strip() else ""
        return (
            "## (mock analysis)\n\n"
            f"This is a deterministic mock report for: {head}\n\n"
            "**final_decision: HOLD** — replace MockLLM with a real provider for real analysis."
        )


_PROVIDERS = {
    "openai": OpenAIAdapter,
    "gemini": GeminiAdapter,
    "claude": ClaudeAdapter,
    "anthropic": ClaudeAdapter,
    "deepseek": DeepSeekAdapter,
    "mock": MockLLM,
}


# Selectable model catalog — used by the CLI "model selection" menu and to
# auto-match the right API key (env var) when a user picks a provider/model.
PROVIDER_CATALOG = [
    {"provider": "gemini",   "label": "Google Gemini (default, real-time grounding)", "env_key": "GOOGLE_API_KEY",    "default_model": DEFAULT_MODELS["gemini"],   "extra": "gemini"},
    {"provider": "openai",   "label": "OpenAI GPT",                                   "env_key": "OPENAI_API_KEY",    "default_model": DEFAULT_MODELS["openai"],   "extra": "openai"},
    {"provider": "claude",   "label": "Anthropic Claude",                             "env_key": "ANTHROPIC_API_KEY", "default_model": DEFAULT_MODELS["claude"],   "extra": "claude"},
    {"provider": "deepseek", "label": "DeepSeek",                                     "env_key": "DEEPSEEK_API_KEY",  "default_model": DEFAULT_MODELS["deepseek"], "extra": "openai"},
]


def provider_for_model(model: str) -> Optional[str]:
    """Infer the provider from a model name (so a user can pick a *model* and the
    right API key is matched automatically)."""
    m = (model or "").lower()
    if m.startswith("gemini") or m.startswith("models/gemini"):
        return "gemini"
    if m.startswith(("gpt-", "o1", "o3", "o4", "chatgpt")):
        return "openai"
    if m.startswith("claude"):
        return "claude"
    if m.startswith("deepseek"):
        return "deepseek"
    return None  # grok / others: no built-in adapter yet


def resolve_llm(llm, api_key: Optional[str] = None, model: Optional[str] = None) -> LLMAdapter:
    """Turn `llm` (an adapter instance or a provider-name string) into an adapter."""
    if isinstance(llm, LLMAdapter):
        return llm
    if isinstance(llm, str):
        key = llm.strip().lower()
        cls = _PROVIDERS.get(key)
        if cls is None:
            raise ValueError(
                f"Unknown LLM provider {llm!r}. Choose one of {sorted(_PROVIDERS)} "
                f"or pass an LLMAdapter instance."
            )
        if cls is MockLLM:
            return cls()
        return cls(api_key=api_key, model=model)
    raise TypeError(f"llm must be a provider name or LLMAdapter, got {type(llm).__name__}")
