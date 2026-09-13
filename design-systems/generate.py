"""Project approved palettes into consumer files; preserve authored layouts. Run with --check in CI."""
from __future__ import annotations

import argparse
import colorsys
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def identities() -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(ROOT.glob("*/identity.json"))]


def hsl(value: str) -> str:
    rgb = [int(value.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    h, l, s = colorsys.rgb_to_hls(*rgb)
    return f"{h * 360:.2f} {s * 100:.2f}% {l * 100:.2f}%"


def tokens(identity: dict, mode: str) -> dict:
    p = identity["modes"][mode]
    mapping = {
        "background": "canvas", "foreground": "ink", "card": "surface",
        "card-foreground": "ink", "primary": "brand", "primary-foreground": "action-ink",
        "secondary": "raised", "secondary-foreground": "ink", "muted": "raised",
        "muted-foreground": "muted", "accent": "raised", "accent-foreground": "ink",
        "destructive": "bad", "destructive-foreground": "canvas", "border": "line",
        "input": "line", "ring": "focus",
    }
    out = {"--" + k: hsl(p[v]) for k, v in mapping.items()}
    return out | {"--radius": "0.625rem", "--font-sans": p["sans"]}


def css_tokens(identity: dict, mode: str) -> str:
    return ":root{" + f"color-scheme:{mode};" + "".join(
        f"--ds-{k}:{v};" for k, v in identity["modes"][mode].items()
    ) + "}\n"


def outputs() -> dict[Path, str]:
    out = {}
    previews = {}
    for identity in identities():
        for mode in ("dark", "light"):
            slug = identity["id"] + ("-light" if mode == "light" else "")
            base = ROOT / identity["id"] / "generated" / mode
            guidance = (ROOT / identity["id"] / "DESIGN.md").read_text(encoding="utf-8")
            reference = {"slug": slug, "name": identity["name"] + " / " + mode.title(),
                         "category": "Foundry identities", "source": identity["source"],
                         "tokens": tokens(identity, mode), "guidance": guidance}
            out[base / "protopane.json"] = json.dumps(reference, indent=2) + "\n"
            out[base / "tokens.css"] = css_tokens(identity, mode)
            theme = ROOT.parent / "slidev-themes" / slug
            source = (theme / "style.css").read_text(encoding="utf-8")
            # Only the colour/type declarations propagate. The theme owns everything else.
            style = re.sub(r":root\{color-scheme:[^}]+}\n", lambda _: css_tokens(identity, mode), source, count=1)
            out[theme / "style.css"] = style
            chrome = (theme / "global-top.vue").read_text(encoding="utf-8")
            chrome = re.sub(r"<script.*?</script>", "", chrome, flags=re.S).replace("<template>", "").replace("</template>", "")
            previews[slug] = ('<!doctype html><html><head><style>body{margin:0}.slidev-slide-content{position:relative;min-height:552px;overflow:hidden}.slidev-layout{box-sizing:border-box}.ds-brand{top:26px}</style><style>'
                + style + '</style></head><body><div class="slidev-slide-content">' + chrome
                + '<main class="slidev-layout ds-cover"><div class="ds-eyebrow">Slide theme specimen</div><h1>Engineering.<br>Clearly expressed.</h1><p class="ds-lede">An authored slide theme with its own stylesheet, chrome and page templates.</p><div class="ds-grid-two"><div class="ds-card"><h2>Approved palette</h2><p>Colour, typography and original marks.</p></div><div class="ds-card"><h2>Owned composition</h2><p>Layouts and motion belong to this theme.</p></div></div></main></div></body></html>')
    preview_shell = (ROOT / "templates/preview.html").read_text(encoding="utf-8")
    out[ROOT / "preview.html"] = preview_shell.replace("__PREVIEWS__", json.dumps(previews).replace("</", "<\\/"))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    for path, value in outputs().items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != value:
                stale.append(str(path.relative_to(ROOT.parent)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value, encoding="utf-8", newline="\n")
    if stale:
        raise SystemExit("Stale generated themes: " + ", ".join(stale))
    print("Design system projections verified" if args.check else "Design system projections generated")


if __name__ == "__main__":
    main()
