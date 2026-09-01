from __future__ import annotations

import importlib.util
from pathlib import Path


PLUGIN_INIT = Path(__file__).resolve().parents[1] / "__init__.py"
spec = importlib.util.spec_from_file_location("dash_normalizer_under_test", PLUGIN_INIT)
assert spec is not None
assert spec.loader is not None
plugin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plugin)


class DummyContext:
    def __init__(self, settings=None):
        self.settings = dict(settings or {})
        self.hooks = {}

    def get_config(self, key, default=None):
        return self.settings.get(key, default)

    def register_hook(self, hook_name, callback):
        self.hooks.setdefault(hook_name, []).append(callback)


def _callback(settings=None):
    ctx = DummyContext(settings=settings)
    plugin.register(ctx)
    assert set(ctx.hooks) == {"transform_llm_output"}
    return ctx.hooks["transform_llm_output"][0]


def test_single_final_response_replaces_em_dash():
    assert plugin.normalize_response_text("Alpha — beta") == "Alpha - beta"


def test_multiple_em_dashes_in_final_response():
    assert plugin.normalize_response_text("A — B — C") == "A - B - C"


def test_no_change_returns_none():
    assert plugin.normalize_response_text("Alpha - beta") is None


def test_en_dash_is_off_by_default():
    assert plugin.normalize_response_text("1999–2001") is None


def test_en_dash_can_be_enabled():
    assert plugin.normalize_response_text("1999–2001", replace_en_dash=True) == "1999-2001"


def test_disabled_returns_none():
    assert plugin.normalize_response_text("Alpha — beta", enabled=False) is None


def test_hook_uses_transform_llm_output_only():
    cb = _callback()
    assert cb("A — B", session_id="s1", model="m", platform="cli") == "A - B"


def test_hook_respects_settings():
    cb = _callback({"replace_em_dash": False, "replace_en_dash": True})
    assert cb("A — B and 1999–2001") == "A — B and 1999-2001"


def test_non_default_scope_disables_transform():
    cb = _callback({"scope": "wrong"})
    assert cb("A — B") is None


def test_tool_payload_like_text_is_not_transformed_unless_passed_as_final_response():
    """The plugin has no tool hook. It registers only final assistant output."""
    ctx = DummyContext()
    plugin.register(ctx)
    assert "transform_tool_result" not in ctx.hooks
    assert "pre_tool_call" not in ctx.hooks
    assert "on_stream_delta" not in ctx.hooks


def test_markdown_survives_except_configured_dash():
    text = "**Note** — cafe and link [details](https://example.com/a-b)."
    assert plugin.normalize_response_text(text) == "**Note** - cafe and link [details](https://example.com/a-b)."
