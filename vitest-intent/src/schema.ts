/**
 * intent.yaml parsing + schema validation.
 *
 * Mirrors the Python pytest-intent schema layer: same required fields, same
 * valid criticality / scope sets, so cross-language bundles use a single
 * intent.yaml format.
 */

import { readFileSync, existsSync } from "node:fs";
import { parse as parseYaml } from "yaml";

export const REQUIRED_FIELDS = [
  "statement",
  "rationale",
  "criticality",
  "scope",
] as const;

export const VALID_CRITICALITY = new Set([
  "critical",
  "high",
  "medium",
  "low",
]);

export const VALID_SCOPE = new Set([
  "unit",
  "integration",
  "e2e",
  "system",
]);

const INTENT_ID_RE = /^INT-[A-Z0-9-]+$/;

export type Claim = Record<string, unknown>;
export type Claims = Record<string, Claim>;

/**
 * Parse intent.yaml at `path`. Returns a map of {INT-XXX-NNN: {field: value}}.
 * Non-INT-prefixed top-level keys are ignored. Empty/missing file returns {}.
 */
export function parseIntentYaml(path: string): Claims {
  if (!existsSync(path)) {
    return {};
  }
  const text = readFileSync(path, "utf-8");
  if (text.trim().length === 0) {
    return {};
  }
  const raw = parseYaml(text);
  if (!raw || typeof raw !== "object") {
    return {};
  }
  const out: Claims = {};
  for (const [k, v] of Object.entries(raw as Record<string, unknown>)) {
    if (!INTENT_ID_RE.test(k)) {
      continue;
    }
    if (v && typeof v === "object" && !Array.isArray(v)) {
      out[k] = v as Claim;
    }
  }
  return out;
}

/**
 * Check schema for every claim. Returns a list of human-readable violation
 * strings; empty list means clean.
 */
export function checkSchema(claims: Claims): string[] {
  const violations: string[] = [];
  for (const [cid, claim] of Object.entries(claims)) {
    for (const field of REQUIRED_FIELDS) {
      if (!(field in claim)) {
        violations.push(`${cid}: missing required field '${field}'`);
      }
    }
    if ("criticality" in claim) {
      const v = String(claim["criticality"]);
      if (!VALID_CRITICALITY.has(v)) {
        violations.push(
          `${cid}: invalid criticality '${v}' (must be one of ${[...VALID_CRITICALITY].join("|")})`,
        );
      }
    }
    if ("scope" in claim) {
      const v = String(claim["scope"]);
      if (!VALID_SCOPE.has(v)) {
        violations.push(
          `${cid}: invalid scope '${v}' (must be one of ${[...VALID_SCOPE].join("|")})`,
        );
      }
    }
  }
  return violations;
}
