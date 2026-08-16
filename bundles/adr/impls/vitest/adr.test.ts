/**
 * ADR bundle - vitest implementation.
 *
 * Walks src/content/docs/decisions/ for ADR pages, parses their frontmatter,
 * and asserts each claim from intent.yaml: adr_status validity, id uniqueness,
 * that supersede references resolve to an existing ADR, and that the decisions
 * index's `## Current` table still matches the records it indexes.
 */

import { readdirSync, readFileSync, statSync } from "node:fs";
import { basename, extname, join } from "node:path";

import { intent } from "@psa-department-of-engineering/vitest-intent";

const DECISIONS_DIR = join(process.cwd(), "src", "content", "docs", "decisions");
const VALID_ADR_STATUSES = new Set([
  "Proposed",
  "Decided",
  "Superseded",
  "Deprecated",
  "Pending",
]);
const FRONTMATTER_RE = /^---\s*\n([\s\S]*?)\n---/;
const H2_RE = /^##\s+(.+?)\s*$/;
// A `[text](target)` cell, the form the decisions-index template's rows take.
const LINK_CELL_RE = /^\[([^\]]*)\]\(([^)]*)\)$/;
// A table delimiter cell: `---`, `:--`, `--:`, `:-:`.
const DELIMITER_CELL_RE = /^:?-{2,}:?$/;
// The index section this bundle owns. `## Superseded` is deliberately NOT
// checked here: INT-ADR-003 already validates the supersede graph on the
// records themselves, and one claim per concern keeps the failure legible.
const CURRENT_HEADING = "Current";
const SUPERSEDED_STATUS = "superseded";

interface Adr {
  slug: string; // filename stem, e.g. ADR-001
  frontmatter: Record<string, string>;
}

function* walkMarkdown(dir: string): Generator<string> {
  let entries: string[];
  try {
    entries = readdirSync(dir);
  } catch {
    return;
  }
  for (const name of entries) {
    const full = join(dir, name);
    let st;
    try {
      st = statSync(full);
    } catch {
      continue;
    }
    if (st.isDirectory()) {
      yield* walkMarkdown(full);
    } else if (st.isFile() && (extname(name) === ".md" || extname(name) === ".mdx")) {
      yield full;
    }
  }
}

function parseFrontmatter(text: string): Record<string, string> | null {
  const m = FRONTMATTER_RE.exec(text);
  if (!m) return null;
  const out: Record<string, string> = {};
  for (const line of m[1].split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const colon = trimmed.indexOf(":");
    if (colon === -1) continue;
    const key = trimmed.slice(0, colon).trim();
    let value = trimmed.slice(colon + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    out[key] = value;
  }
  return out;
}

/** The decisions index is a navigation page, not an ADR. */
function isIndexPage(file: string): boolean {
  return basename(file, extname(file)).toLowerCase() === "index";
}

function extractBody(text: string): string {
  // Everything after the closing frontmatter delimiter; a page without
  // frontmatter is all body.
  const m = FRONTMATTER_RE.exec(text);
  return m === null ? text : text.slice(m[0].length);
}

function loadAdrs(): Adr[] {
  const adrs: Adr[] = [];
  for (const file of walkMarkdown(DECISIONS_DIR)) {
    if (isIndexPage(file)) continue;
    let text: string;
    try {
      text = readFileSync(file, "utf-8");
    } catch {
      continue;
    }
    const fm = parseFrontmatter(text);
    if (fm === null) continue;
    adrs.push({ slug: basename(file, extname(file)), frontmatter: fm });
  }
  return adrs;
}

/** The decisions index's body, or null when the collection has no index page. */
function loadIndexBody(): string | null {
  for (const file of walkMarkdown(DECISIONS_DIR)) {
    if (!isIndexPage(file)) continue;
    try {
      return extractBody(readFileSync(file, "utf-8"));
    } catch {
      return null;
    }
  }
  return null;
}

/**
 * The lines under a named level-2 heading, up to the next level-2 heading;
 * null when the page carries no such section. Deeper headings (`###`) belong
 * to the section, so they do not end it.
 */
function sectionLines(body: string, heading: string): string[] | null {
  const lines = body.split("\n");
  const want = heading.toLowerCase();
  let start = -1;
  for (let i = 0; i < lines.length; i += 1) {
    const m = H2_RE.exec(lines[i]);
    if (m !== null && m[1].trim().toLowerCase() === want) {
      start = i + 1;
      break;
    }
  }
  if (start === -1) return null;
  const out: string[] = [];
  for (let i = start; i < lines.length; i += 1) {
    if (H2_RE.test(lines[i])) break;
    out.push(lines[i]);
  }
  return out;
}

function splitRow(line: string): string[] {
  return line
    .replace(/^\|/, "")
    .replace(/\|\s*$/, "")
    .split("|")
    .map((cell) => cell.trim());
}

/**
 * The data rows of the first markdown table in `lines`. GitHub-flavoured
 * markdown requires a header row and a delimiter row, so everything before the
 * delimiter is the header and everything after it is data.
 */
function tableDataRows(lines: string[]): string[][] {
  const rows: string[][] = [];
  let afterDelimiter = false;
  for (const raw of lines) {
    const line = raw.trim();
    if (!line.startsWith("|")) continue;
    const cells = splitRow(line);
    if (cells.every((cell) => DELIMITER_CELL_RE.test(cell))) {
      afterDelimiter = true;
      continue;
    }
    if (!afterDelimiter) continue; // the header row
    rows.push(cells);
  }
  return rows;
}

/**
 * The record a row points at, as a lowercased slug.
 *
 * Deliberately link-form agnostic: a row may be written page-relative
 * (`[ADR-001](adr-001/)`) or root-absolute (`[ADR-001](/decisions/adr-001/)`),
 * and both name the same record. Which form a site may use is not this claim's
 * concern - INT-STARLIGHT-011 owns that - so the link text is read first, then
 * the target's last path segment, then whatever the cell says.
 */
function rowSlug(cell: string, known: Set<string>): string {
  const trimmed = cell.trim();
  const m = LINK_CELL_RE.exec(trimmed);
  if (m === null) return trimmed.toLowerCase();
  const text = m[1].trim().toLowerCase();
  if (known.has(text)) return text;
  const target = m[2].trim().replace(/[#?].*$/, "").replace(/\/+$/, "");
  const segment = (target.split("/").pop() ?? "").replace(/\.mdx?$/i, "").toLowerCase();
  if (segment && known.has(segment)) return segment;
  return text || segment;
}

/**
 * A record's title as the index states it. Records conventionally title
 * themselves `ADR-001: the decision`, while the index's Id column already
 * carries the slug, so a leading `<slug>:` prefix is stripped from both sides
 * rather than being demanded of, or forbidden to, either.
 */
function bareTitle(title: string, slug: string): string {
  const prefix = `${slug.toLowerCase()}:`;
  return title.toLowerCase().startsWith(prefix) ? title.slice(prefix.length).trim() : title.trim();
}

/** One comparable line per row: slug and status are case-insensitive, the title is not. */
function indexLine(slug: string, title: string, status: string): string {
  return `${slug.toLowerCase()} | ${bareTitle(title, slug)} | ${status.trim().toLowerCase()}`;
}

import { describe, expect } from "vitest";

describe("ADR bundle", () => {
  const adrs = loadAdrs();

  intent("INT-ADR-001", "every ADR has a valid adr_status", () => {
    const offenders = adrs
      .filter((a) => !VALID_ADR_STATUSES.has(a.frontmatter["adr_status"]))
      .map((a) => `${a.slug} (adr_status=${a.frontmatter["adr_status"]})`);
    expect(offenders, `ADRs with invalid adr_status: ${offenders.join(", ")}`).toEqual([]);
  });

  intent("INT-ADR-002", "ADR ids are unique across the decisions collection", () => {
    const ids = new Map<string, string[]>();
    for (const a of adrs) {
      const id = a.frontmatter["id"];
      if (!id) continue;
      if (!ids.has(id)) ids.set(id, []);
      ids.get(id)!.push(a.slug);
    }
    const dupes = [...ids.entries()].filter(([, slugs]) => slugs.length > 1);
    const msg = dupes.map(([id, slugs]) => `${id}: ${slugs.join(" + ")}`).join("; ");
    expect(dupes, `duplicate ADR ids: ${msg}`).toEqual([]);
  });

  intent("INT-ADR-003", "supersede references resolve to existing ADRs", () => {
    const known = new Set(adrs.map((a) => a.slug));
    const broken: string[] = [];
    for (const a of adrs) {
      for (const field of ["supersedes", "superseded_by"]) {
        const ref = a.frontmatter[field];
        if (ref && !known.has(ref)) {
          broken.push(`${a.slug}.${field} -> ${ref}`);
        }
      }
    }
    expect(broken, `unresolved supersede references: ${broken.join(", ")}`).toEqual([]);
  });

  intent(
    "INT-ADR-004",
    "the decisions index's Current table lists exactly the live records",
    () => {
      const body = loadIndexBody();
      // No index page, nothing restating the records: this claim is about an
      // index that drifts, not about requiring one to exist.
      if (body === null) return;

      const live = adrs.filter(
        (a) => (a.frontmatter["adr_status"] ?? "").trim().toLowerCase() !== SUPERSEDED_STATUS,
      );
      const expected = live
        .map((a) => indexLine(a.slug, a.frontmatter["title"] ?? "", a.frontmatter["adr_status"] ?? ""))
        .sort();

      const lines = sectionLines(body, CURRENT_HEADING);
      const known = new Set(adrs.map((a) => a.slug.toLowerCase()));
      const actual = tableDataRows(lines ?? [])
        .map((cells) =>
          indexLine(rowSlug(cells[0] ?? "", known), cells[1] ?? "", cells[2] ?? ""),
        )
        .sort();

      expect(
        actual,
        lines === null
          ? `the decisions index has no \`## ${CURRENT_HEADING}\` section, so nothing states the current decisions`
          : `the decisions index's \`## ${CURRENT_HEADING}\` table has drifted from the records (each line is \`id | title | status\`); regenerate it from the records' frontmatter`,
      ).toEqual(expected);
    },
  );
});
