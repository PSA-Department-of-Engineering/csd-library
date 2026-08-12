#!/usr/bin/env node
// Self-containment gate for the deck theme catalog.
//
// A theme is self-contained when it can be taken on its own: its templates use only
// classes its own style.css defines, and the chrome classes its style.css styles are
// produced by its own component. Both directions matter - a template reaching for a
// class the theme lacks renders unstyled, and a theme styling chrome it does not ship
// is styling markup that exists nowhere.
//
// Asset references (fonts, logos, textures) are REPORTED, not failed: those are brand
// payload the catalog deliberately does not carry. See the slidev-theming flyer.
//
//   node check-themes.mjs          all themes
//   node check-themes.mjs <name>   one theme
import { readdirSync, readFileSync, existsSync, statSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = dirname(fileURLToPath(import.meta.url))

// Selector text is everything before a `{`, minus at-rules and declaration bodies.
// Parsing it (rather than the whole file) keeps class names inside url(), content:
// strings and font names out of the "defined" set.
function definedClasses(css) {
    const out = new Set()
    const stripped = css.replace(/\/\*[\s\S]*?\*\//g, '')
    for (const chunk of stripped.split('}')) {
        const head = chunk.split('{')[0]
        if (!head || head.trim().startsWith('@')) {
            // An at-rule's own prelude carries no classes, but its body does; keep going
            // so @media / @supports blocks still contribute their selectors.
            const inner = chunk.split('{').slice(1).join('{')
            for (const m of inner.matchAll(/\.(-?[A-Za-z_][\w-]*)/g)) out.add(m[1])
            continue
        }
        for (const m of head.matchAll(/\.(-?[A-Za-z_][\w-]*)/g)) out.add(m[1])
    }
    return out
}

// class="a b c" and :class="'a b'" in pages and in the chrome component.
function usedClasses(text) {
    const out = new Set()
    for (const m of text.matchAll(/(?:^|\s):?class\s*=\s*"([^"]*)"/g)) {
        for (const tok of m[1].split(/[\s'"{}?:]+/)) {
            if (/^-?[A-Za-z_][\w-]*$/.test(tok)) out.add(tok)
        }
    }
    return out
}

// Utility classes come from UnoCSS at build time, not from the theme, so they are not
// the theme's to define. Anything matching these shapes is out of scope for the gate.
const UTILITY = [
    /^(m|p)[trblxy]?-/, /^(w|h|min-w|min-h|max-w|max-h)-/, /^(text|font|leading|tracking)-/,
    /^(flex|grid|gap|items|justify|self|order|col|row|place)-/, /^(bg|border|rounded|shadow|ring|opacity)-/,
    /^(absolute|relative|fixed|sticky|static)$/, /^(top|bottom|left|right|inset|z)-/,
    /^(hidden|block|inline|inline-block|contents|flex|grid|table|flow-root)$/,
    /^(overflow|whitespace|break|truncate)/,
    /^(mt|mb|ml|mr|mx|my|pt|pb|pl|pr|px|py)-/, /^-?(mt|mb|ml|mr|mx|my)-/,
    /^(slidev|uno)-/, /^v-/,
]
const isUtility = (c) => UTILITY.some((re) => re.test(c))

const only = process.argv[2]
const themes = readdirSync(root).filter((n) => {
    if (n.startsWith('_') || n.startsWith('.')) return false
    if (!statSync(join(root, n)).isDirectory()) return false
    return existsSync(join(root, n, 'style.css'))
}).filter((n) => !only || n === only)

let failed = 0
for (const theme of themes) {
    const dir = join(root, theme)
    const css = readFileSync(join(dir, 'style.css'), 'utf8')
    const defined = definedClasses(css)

    const pagesDir = join(dir, 'pages')
    const pages = existsSync(pagesDir) ? readdirSync(pagesDir).filter((f) => f.endsWith('.md')) : []
    const vue = join(dir, 'global-top.vue')

    const problems = []
    const notes = []

    if (!pages.length) problems.push('ships no pages/ templates')

    // 1. Every class a template uses must be defined here.
    for (const page of pages) {
        const used = usedClasses(readFileSync(join(pagesDir, page), 'utf8'))
        const missing = [...used].filter((c) => !defined.has(c) && !isUtility(c)).sort()
        if (missing.length) problems.push(`pages/${page} uses ${missing.length} undefined: ${missing.join(' ')}`)
    }

    // 2. Chrome is DECLARED, not guessed. A prefix is a namespace, not a role - vodafone's
    //    vf- classes are its whole page vocabulary, so inferring chrome from the prefix
    //    read 31 page classes as chrome. meta.chrome lists the classes the theme's own
    //    component must produce; absent or empty means the theme has no chrome.
    const metaPath = join(dir, 'meta.json')
    const meta = existsSync(metaPath) ? JSON.parse(readFileSync(metaPath, 'utf8')) : {}
    const chrome = Array.isArray(meta.chrome) ? meta.chrome : []

    if (chrome.length) {
        const undeclared = chrome.filter((c) => !defined.has(c))
        if (undeclared.length) problems.push(`meta.chrome names classes style.css does not define: ${undeclared.join(' ')}`)
        if (!existsSync(vue)) {
            problems.push(`declares ${chrome.length} chrome classes but ships no global-top.vue: ${chrome.join(' ')}`)
        } else {
            const produced = usedClasses(readFileSync(vue, 'utf8'))
            const orphan = chrome.filter((c) => !produced.has(c))
            if (orphan.length) problems.push(`chrome declared but not produced by global-top.vue: ${orphan.join(' ')}`)
        }
    } else if (existsSync(vue)) {
        problems.push('ships global-top.vue but meta.chrome declares nothing it must produce')
    }

    // Whatever the component does produce must be styled here, or it renders bare.
    if (existsSync(vue)) {
        const produced = [...usedClasses(readFileSync(vue, 'utf8'))]
        const unstyled = produced.filter((c) => !defined.has(c) && !isUtility(c)).sort()
        if (unstyled.length) problems.push(`global-top.vue emits classes style.css does not define: ${unstyled.join(' ')}`)
    }

    // 3. Assets: reported only. Brand payload is declared, not carried.
    const assets = [...css.matchAll(/url\(["']?(\/[^)"']+)/g)].map((m) => m[1])
    const missingAssets = [...new Set(assets)].filter((a) => !existsSync(join(dir, 'public', a)))
    if (missingAssets.length) notes.push(`references ${missingAssets.length} file(s) it does not ship: ${[...new Set(missingAssets)].join(' ')}`)

    const mark = problems.length ? 'FAIL' : 'ok  '
    if (problems.length) failed++
    console.log(`${mark} ${theme}  (${defined.size} classes, ${pages.length} templates)`)
    for (const p of problems) console.log(`       ! ${p}`)
    for (const n of notes) console.log(`       - ${n}`)
}

console.log(failed ? `\n${failed} theme(s) not self-contained` : `\n${themes.length} theme(s) self-contained`)
process.exit(failed ? 1 : 0)
