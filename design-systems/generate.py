"""Generate consumer themes from the approved identities. Run with --check in CI."""
from __future__ import annotations

import argparse
import base64
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


def asset(identity: dict, name: str) -> str:
    p = next((ROOT / identity["id"] / "assets").glob(name + ".*"))
    mime = "image/svg+xml" if p.suffix == ".svg" else "image/png"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def logo(identity: dict, mode: str) -> str:
    slug = identity["id"]
    if slug == "psa":
        return '<span class="ds-wordmark">psa<span class="ds-dot">.</span></span>'
    if slug == "celfocus-digital":
        return f'<img class="ds-logo" src="{asset(identity, "logo")}" alt="Celfocus"><span class="ds-unit">Digital</span>'
    return (f'<span class="ds-speechmark" role="img" aria-label="Vodafone"></span>'
            '<span class="ds-lockup-text">Digital Engineering<small>VODAFONE PORTUGAL</small></span>'
            f'<img class="ds-flag" src="{asset(identity, "flag")}" alt="Portugal">')


def atmosphere(identity: dict) -> str:
    slug = identity["id"]
    if slug == "psa":
        paths = "".join(
            f'<path d="M {720+i*11} -90 C {450+i*8} 70 {970+i*6} 190 {710+i*12} 335 S {560+i*10} 540 {860+i*8} 680"/>'
            for i in range(9)
        )
        return f'<svg class="ds-stream" viewBox="0 0 980 552" preserveAspectRatio="xMidYMid slice">{paths}</svg>'
    if slug == "vodafone-digital-engineering":
        return '<div class="ds-grid"></div><div class="ds-orbit"><i></i><i></i><i></i></div>'
    return '<div class="ds-arcs"><i></i><i></i><i></i></div>'


def css(identity: dict, mode: str) -> str:
    style = (ROOT / "templates" / "shared.css").read_text(encoding="utf-8")
    extra = ""
    fonts = []
    if identity["id"] == "vodafone-digital-engineering":
        fonts = [("Vodafone", w, f"Vodafone-{w}.woff2", "woff2") for w in (300, 400, 500, 600, 700, 800)]
        extra = '.ds-speechmark{mask:url("' + asset(identity, "logo") + '") center/contain no-repeat;background:' + ("#e60000" if mode == "light" else "white") + ';}\n'
    if identity["id"] == "celfocus-digital":
        fonts = [("Aptos", w, f"Aptos-{name}.ttf", "truetype") for w, name in ((300, "Light"), (400, "Regular"), (600, "SemiBold"), (700, "Bold"), (800, "ExtraBold"))]
        extra += '.ds-logo{filter:' + ("none" if mode == "light" else "brightness(0) invert(1)") + ';}\n'
    font_css = "".join(f'@font-face{{font-family:"{family}";font-weight:{weight};font-display:swap;src:url("/fonts/{file}") format("{fmt}")}}\n' for family, weight, file, fmt in fonts)
    return font_css + css_tokens(identity, mode) + style + extra


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
            out[base / "press.css"] = css(identity, mode)
            out[base / "mark.html"] = logo(identity, mode)
            out[base / "ambient.html"] = '<div class="ds-ambient" aria-hidden="true"><div class="ds-glow"></div>' + atmosphere(identity) + '</div>'
            theme = ROOT.parent / "slidev-themes" / slug
            out[theme / "style.css"] = "/* Generated by design-systems/generate.py. */\n" + css(identity, mode)
            chrome = '<template><div class="ds-ambient" aria-hidden="true"><div class="ds-glow"></div>' + atmosphere(identity) + '<div class="ds-embers">' + '<i></i>' * 12 + '</div></div><div class="ds-brand">' + logo(identity, mode) + '</div></template>\n'
            runtime = '''<script setup>
import { onMounted, onUnmounted } from 'vue'
const syncVisibility = () => { document.documentElement.dataset.dsHidden = String(document.hidden) }
onMounted(() => { syncVisibility(); document.addEventListener('visibilitychange', syncVisibility) })
onUnmounted(() => document.removeEventListener('visibilitychange', syncVisibility))
</script>
'''
            out[theme / "global-top.vue"] = chrome + runtime
            previews[slug] = '<!doctype html><html><head><style>body{margin:0}.slidev-slide-content{position:relative;min-height:552px;overflow:hidden}.slidev-layout{box-sizing:border-box}.ds-brand{top:26px}</style><style>' + css(identity, mode) + '</style></head><body><div class="slidev-slide-content">' + chrome.replace('<template>', '').replace('</template>', '') + '<main class="slidev-layout ds-cover"><div class="ds-eyebrow">Engineering / Shared identity</div><h1>One identity.<br>Every expression.</h1><p class="ds-lede">The same source flows into prototypes, slides and the documents we produce.</p><div class="ds-grid-two"><div class="ds-card"><h2>Shared tokens</h2><p>Colour, typography and original marks.</p></div><div class="ds-card"><h2>Local choice</h2><p>One installation default. Every identity available.</p></div></div></main></div></body></html>'
            pages = {}
            for p in (ROOT / "templates" / "pages").glob("*.md"):
                pages[p.stem] = p.read_text(encoding="utf-8")
                out[theme / "pages" / p.name] = pages[p.stem]
            out[theme / "meta.json"] = json.dumps({
                "prefix": "ds", "description": identity["name"] + " / " + mode.title(),
                "tiers": ["core", "ambient"],
                "chrome": sorted(set(re.findall(r'ds-[a-z-]+', chrome))), "pages": list(pages),
                "identity": identity["id"], "mode": mode,
                "requires": {"assets": re.findall(r'url\("(/fonts/[^\"]+)"\)', css(identity, mode)), "note": "Licensed brand fonts are supplied by the installation. System fallbacks are supported."},
            }, indent=2) + "\n"
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
