# dash-normalizer

Standalone Hermes Agent plugin that normalizes dash characters in final assistant output.

Built by [Rad Paluszak](https://paluszak.me/) and [NON.agency](https://non.agency/) for Hermes Agent profiles that need simpler final-output typography without Hermes core changes.

## Bottom Line Up Front

`dash-normalizer` registers the Hermes Agent `transform_llm_output` hook.

By default, it changes em dash characters (`—`) in the final assistant reply to a simple hyphen (`-`). It leaves en dash characters (`–`) unchanged unless you enable that setting.

This plugin is deliberately small:

- it does **not** patch Hermes core;
- it does **not** monkeypatch runtime objects;
- it does **not** modify tool calls, tool results, logs, or conversation history;
- it does **not** try to modify in-flight stream chunks;
- it can live as a normal Git repository and be symlinked into one or more Hermes profile plugin directories.

## Status

- Version: `0.1.0`
- Hermes API used: `ctx.register_hook("transform_llm_output", ...)`
- Runtime dependencies: Python standard library only
- Test dependency: `pytest`
- License: BSD 3-Clause, with attribution to Rad Paluszak and NON.agency

## What this is not

This is **not** an in-stream text rewriter. Hermes stream hooks are observer-only. Their return values do not replace streamed output.

This is **not** a formatter for tool payloads. It receives only the final assistant response text from `transform_llm_output`.

## Prerequisites

Before installing this plugin, you need:

1. Hermes Agent with plugin support.
2. A Hermes profile that will load the plugin.
3. Python 3.11+ for tests and development.
4. `pytest` if you want to run the included unit tests.

## Installation

Choose one layout.

### Option A: shared checkout with profile symlinks

Good when more than one Hermes profile should use the same plugin source.

```bash
mkdir -p ~/.hermes/plugins
git clone <your-remote-url> ~/.hermes/plugins/dash-normalizer

mkdir -p ~/.hermes/profiles/<profile>/plugins
ln -s ~/.hermes/plugins/dash-normalizer \
  ~/.hermes/profiles/<profile>/plugins/dash-normalizer

hermes -p <profile> plugins enable dash-normalizer
```

### Option B: profile-local checkout

Good when one Hermes profile owns its own plugin copy.

```bash
mkdir -p ~/.hermes/profiles/<profile>/plugins
git clone <your-remote-url> \
  ~/.hermes/profiles/<profile>/plugins/dash-normalizer

hermes -p <profile> plugins enable dash-normalizer
```

After enabling the plugin, restart the relevant Hermes session or gateway so the plugin is loaded by the running process:

```bash
hermes -p <profile> gateway restart
```

If you are running from inside the same gateway-managed chat and Hermes refuses to restart itself, run the restart from a normal shell on the host.

## Configuration

The default configuration is safe for normal use.

```yaml
plugins:
  entries:
    dash-normalizer:
      settings:
        enabled: true
        replace_em_dash: true
        replace_en_dash: false
        scope: assistant_text_only
```

### Settings

| Setting | Type | Default | Meaning |
|---|---:|---:|---|
| `enabled` | bool | `true` | Enables or disables the final-output transform. |
| `replace_em_dash` | bool | `true` | Replaces `—` with `-`. |
| `replace_en_dash` | bool | `false` | Replaces `–` with `-`. |
| `scope` | string | `assistant_text_only` | Documentation guard. Other values disable the transform. |

## Behavior

Default behavior:

```text
Input:  Plan — option A; years 1999–2001.
Output: Plan - option A; years 1999–2001.
```

With `replace_en_dash: true`:

```text
Input:  Plan — option A; years 1999–2001.
Output: Plan - option A; years 1999-2001.
```

The plugin returns `None` when no change is needed. This lets Hermes treat the response as unchanged.

## Why `transform_llm_output`

The original goal was to normalize dashes while the model streamed text.

That is not possible through the current stream hooks without a Hermes core change. The stream hooks are observer hooks. They can watch stream events, but they cannot replace the stream text.

`transform_llm_output` is the update-safe hook for this job. It runs after the tool-calling loop completes and before the final assistant text is delivered.

## Verification

Run unit tests:

```bash
python -m pytest tests -q -o 'addopts='
```

Run Hermes plugin doctor for a target profile:

```bash
hermes -p <profile> plugins doctor dash-normalizer --ci
```

Run a direct hook smoke test:

```bash
HERMES_HOME=~/.hermes/profiles/<profile> \
PYTHONPATH=~/.hermes/hermes-agent \
python - <<'PY'
from hermes_cli.plugins import PluginManager

pm = PluginManager()
pm.discover_and_load()

print('plugin_loaded=', 'dash-normalizer' in pm._plugins)
print('hook_count=', len(pm._hooks.get('transform_llm_output', [])))
print('transform=', pm.invoke_hook(
    'transform_llm_output',
    response_text='Plan — option A; years 1999–2001.',
))
PY
```

Expected output includes:

```text
plugin_loaded= True
hook_count= 1
transform= ['Plan - option A; years 1999–2001.']
```

## Live check

Ask the target Hermes profile:

```text
Reply with exactly this text and nothing else: TEST — TEST
```

Expected final delivered response:

```text
TEST - TEST
```

If you still receive `TEST — TEST`, restart the target Hermes gateway and test again.

## Development workflow

- Keep the plugin standalone.
- Do not patch Hermes core.
- Do not add runtime dependencies unless there is a strong reason.
- Keep tests focused on hook behavior and text-only normalization.
- Do not publish, push, or change repository remotes without explicit operator approval.

Useful commands:

```bash
python -m pytest tests -q -o 'addopts='
hermes -p <profile> plugins doctor dash-normalizer --ci
git status --short --untracked-files=all
```

## Support and liability

This software is provided as-is. The authors do not guarantee that it will fit your use case or that it will be free of defects.

Fixes and support are handled only in the authors' own time and at their own discretion.

## Author

- Rad Paluszak: [paluszak.me](https://paluszak.me/)
- LinkedIn: [Rad Paluszak](https://uk.linkedin.com/in/radpaluszak/pl)
- NON.agency: [non.agency](https://non.agency/)

## License

BSD 3-Clause License.

See [`LICENSE`](LICENSE) for the full license text.
