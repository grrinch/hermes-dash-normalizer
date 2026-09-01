"""Dash Normalizer plugin for Hermes Agent.

This plugin uses the transform_llm_output hook. It runs only on the final
assistant response text after the tool-calling loop completes. It does not
observe or modify tool calls, tool results, logs, conversation history, or
in-flight stream chunks.
"""

from __future__ import annotations

from typing import Any

EM_DASH = "—"
EN_DASH = "–"
HYPHEN = "-"


class _Defaults:
    enabled = True
    replace_em_dash = True
    replace_en_dash = False
    scope = "assistant_text_only"


def _as_bool(value: Any, default: bool) -> bool:
    """Return a strict bool with simple string compatibility."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    return default


def normalize_response_text(
    response_text: str,
    *,
    enabled: bool = _Defaults.enabled,
    replace_em_dash: bool = _Defaults.replace_em_dash,
    replace_en_dash: bool = _Defaults.replace_en_dash,
) -> str | None:
    """Normalize configured dash characters in final assistant text.

    Returns None when no replacement is needed. That keeps Hermes's
    transform_llm_output contract cheap and avoids marking an unchanged reply
    as transformed.
    """
    if not enabled or not isinstance(response_text, str) or not response_text:
        return None

    normalized = response_text
    if replace_em_dash:
        normalized = normalized.replace(EM_DASH, HYPHEN)
    if replace_en_dash:
        normalized = normalized.replace(EN_DASH, HYPHEN)

    if normalized == response_text:
        return None
    return normalized


def register(ctx: Any) -> None:
    """Register final-output dash normalization with Hermes."""

    def _transform_llm_output(response_text: str, **_kwargs: Any) -> str | None:
        scope = ctx.get_config("scope", _Defaults.scope)
        if scope != _Defaults.scope:
            return None

        return normalize_response_text(
            response_text,
            enabled=_as_bool(ctx.get_config("enabled", _Defaults.enabled), _Defaults.enabled),
            replace_em_dash=_as_bool(
                ctx.get_config("replace_em_dash", _Defaults.replace_em_dash),
                _Defaults.replace_em_dash,
            ),
            replace_en_dash=_as_bool(
                ctx.get_config("replace_en_dash", _Defaults.replace_en_dash),
                _Defaults.replace_en_dash,
            ),
        )

    ctx.register_hook("transform_llm_output", _transform_llm_output)
