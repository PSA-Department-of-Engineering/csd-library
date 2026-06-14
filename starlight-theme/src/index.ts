/**
 * @psa-department-of-engineering/starlight-theme - the shared Starlight look.
 *
 * One source of truth for the docs-site theme, consumed in two parts:
 *   - the stylesheet (warm dark palette override + a token-based Mermaid contrast
 *     layer), wired through Starlight:
 *       customCss: ['@psa-department-of-engineering/starlight-theme/styles.css']
 *   - the `mermaidConfig` object, spread into the astro-mermaid integration:
 *       mermaid({ autoTheme: true, mermaidConfig })
 *
 * This package is deliberately a CSS asset plus a config object, NOT a Starlight or
 * Astro integration. astro-mermaid must run before starlight() in the integrations
 * array (it transforms ```mermaid blocks before expressive-code renders them as
 * code), and an integration that injected astro-mermaid for the site could not
 * guarantee that ordering. So each site keeps its explicit mermaid()/starlight()
 * wiring and consumes the stylesheet and config from here.
 *
 * This is a runtime-styling concern, distinct from the STARLIGHT *intent bundle*
 * (csd-library/bundles/starlight/), which governs page frontmatter and structure
 * claims and their tests, not the look.
 */

export { mermaidConfig } from "./mermaid-config.js";
export type { StarlightThemeMermaidConfig } from "./mermaid-config.js";

export const VERSION = "0.1.0";
