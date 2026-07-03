# Slidev theme catalog

Brand- and organization-specific themes for the `bootstrap-slidev-deck` skill (master copy in the sibling `ai-coding-prompts` playbook). The skill resolves themes from its built-in `themes/` directory first, then from this catalog (override with `--themes-root`).

Each theme is a directory:

```
<name>/
├── style.css    # the theme, copied verbatim into the scaffolded deck
└── meta.json    # {"prefix": "<short>", "description": "..."}
```

`prefix` is the namespace for the theme's utility classes (e.g. `vf-footer`, `k-alert`). Themes are immutable per brand: meaningful variations get a new directory here; project-specific one-offs use the skill's `--theme-css` flag instead.

| Theme | Prefix | Notes |
|---|---|---|
| `vodafone` | `vf` | Vodafone corporate. Red accent on white, Inter sans, full standard taxonomy. |
| `celfocus` | `k` | Celfocus corporate. Terracotta accent, editorial typography, standard taxonomy plus decorative extras (eyebrow, kicker, big, huge, tag). |
