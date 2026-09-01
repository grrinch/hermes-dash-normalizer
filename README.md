# dash-normalizer

Hermes Agent profile-local plugin for `sales-team-agent`.

It registers `transform_llm_output` and normalizes dash characters in the final assistant response text.

## Defaults

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

## Behavior

- Replaces em dash `—` with hyphen `-` by default.
- Does not replace en dash `–` unless `replace_en_dash` is set to `true`.
- Runs only on final assistant text.
- Does not modify tool calls, tool results, logs, or conversation history.
- Does not transform in-flight stream chunks.

## Why this hook

Hermes stream hooks are observer-only. They cannot change text in-flight without a core change. This plugin stays within the no-core-changes constraint by using the existing `transform_llm_output` hook.
