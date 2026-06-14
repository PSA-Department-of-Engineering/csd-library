/**
 * The astro-mermaid `mermaidConfig` shared by every docs site.
 *
 * Under astro-mermaid's `autoTheme` a single config is shared by both the light
 * and dark Mermaid themes, so it carries only theme-NEUTRAL choices: font family
 * and size, node and rank spacing, and the edge curve. Diagram COLOUR is set in
 * the stylesheet (`styles.css`) against Starlight's `--sl-color-*` tokens, which
 * flip with the active theme; a fixed colour here would be correct in only one of
 * the two modes. See REF-StarlightDocs section 8.1.
 */

export interface StarlightThemeMermaidConfig {
  flowchart: {
    curve: string;
    nodeSpacing: number;
    rankSpacing: number;
    padding: number;
    useMaxWidth: boolean;
  };
  themeVariables: {
    fontFamily: string;
    fontSize: string;
  };
}

export const mermaidConfig: StarlightThemeMermaidConfig = {
  flowchart: { curve: "basis", nodeSpacing: 50, rankSpacing: 60, padding: 14, useMaxWidth: true },
  themeVariables: { fontFamily: "ui-sans-serif, system-ui, sans-serif", fontSize: "14px" },
};
