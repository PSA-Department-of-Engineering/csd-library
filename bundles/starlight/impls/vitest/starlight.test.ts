/**
 * STARLIGHT bundle — vitest implementation.
 *
 * Walks src/content/docs/** for markdown files, parses their frontmatter,
 * and asserts each claim from intent.yaml.
 */

import { readdirSync, readFileSync, statSync } from "node:fs";
import { extname, join, relative } from "node:path";

import { intent } from "@psa-department-of-engineering/vitest-intent";

const DOCS_DIR = join(process.cwd(), "src", "content", "docs");
const VALID_TYPES = new Set(["Overview", "Guide", "Standard", "Reference"]);
const VALID_STATUSES = new Set(["Draft", "Active", "Deprecated"]);
const ISO_DATE_RE = /^\d{4}-\d{2}-\d{2}$/;
const FRONTMATTER_RE = /^---\s*\n([\s\S]*?)\n---/;

interface Doc {
  path: string;          // path relative to DOCS_DIR
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
    // strip surrounding quotes
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

function loadDocs(): Doc[] {
  const docs: Doc[] = [];
  for (const file of walkMarkdown(DOCS_DIR)) {
    let text: string;
    try {
      text = readFileSync(file, "utf-8");
    } catch {
      continue;
    }
    const fm = parseFrontmatter(text);
    if (fm === null) continue;
    docs.push({
      path: relative(DOCS_DIR, file),
      frontmatter: fm,
    });
  }
  return docs;
}

import { describe, expect } from "vitest";

describe("STARLIGHT bundle", () => {
  const docs = loadDocs();

  intent("INT-STARLIGHT-001", "every doc has a non-empty title", () => {
    const offenders = docs
      .filter((d) => !d.frontmatter["title"] || d.frontmatter["title"].length === 0)
      .map((d) => d.path);
    expect(offenders, `docs missing title: ${offenders.join(", ")}`).toEqual([]);
  });

  intent("INT-STARLIGHT-002", "every doc has a non-empty id", () => {
    const offenders = docs
      .filter((d) => !d.frontmatter["id"] || d.frontmatter["id"].length === 0)
      .map((d) => d.path);
    expect(offenders, `docs missing id: ${offenders.join(", ")}`).toEqual([]);
  });

  intent("INT-STARLIGHT-003", "doc ids are unique across the collection", () => {
    const ids = new Map<string, string[]>();
    for (const d of docs) {
      const id = d.frontmatter["id"];
      if (!id) continue;
      if (!ids.has(id)) ids.set(id, []);
      ids.get(id)!.push(d.path);
    }
    const dupes = [...ids.entries()].filter(([, paths]) => paths.length > 1);
    const msg = dupes.map(([id, paths]) => `${id}: ${paths.join(" + ")}`).join("; ");
    expect(dupes, `duplicate ids: ${msg}`).toEqual([]);
  });

  intent("INT-STARLIGHT-004", "every doc has a valid type", () => {
    const offenders = docs
      .filter((d) => !VALID_TYPES.has(d.frontmatter["type"]))
      .map((d) => `${d.path} (type=${d.frontmatter["type"]})`);
    expect(offenders, `docs with invalid type: ${offenders.join(", ")}`).toEqual([]);
  });

  intent("INT-STARLIGHT-005", "every doc has a valid status", () => {
    const offenders = docs
      .filter((d) => !VALID_STATUSES.has(d.frontmatter["status"]))
      .map((d) => `${d.path} (status=${d.frontmatter["status"]})`);
    expect(offenders, `docs with invalid status: ${offenders.join(", ")}`).toEqual([]);
  });

  intent("INT-STARLIGHT-006", "every doc has updated as YYYY-MM-DD", () => {
    const offenders = docs
      .filter((d) => !ISO_DATE_RE.test(d.frontmatter["updated"] ?? ""))
      .map((d) => `${d.path} (updated=${d.frontmatter["updated"]})`);
    expect(offenders, `docs with missing/invalid updated: ${offenders.join(", ")}`).toEqual([]);
  });
});
