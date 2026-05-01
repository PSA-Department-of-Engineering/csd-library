/**
 * Reusable meta-tests for vitest-intent projects.
 *
 * Drop-in usage in any project's `tests/meta.test.ts`:
 *
 *     import { registerIntentMetaTests } from 'vitest-intent/meta-tests';
 *     registerIntentMetaTests({ packRoot: __dirname + '/..' });
 *
 * Or for multi-file / multi-dir layouts:
 *
 *     registerIntentMetaTests({
 *       intentYamlPaths: [path.join(root, 'intent', 'a.yaml'), path.join(root, 'intent', 'b.yaml')],
 *       testsDirs: [path.join(root, 'src', 'a', 'tests'), path.join(root, 'src', 'b', 'tests')],
 *     });
 */

import { existsSync } from "node:fs";
import { join } from "node:path";

import { test, expect } from "vitest";

import { collectAnnotatedTests, coverageViolations, type AnnotatedTests } from "./coverage.js";
import { checkSchema, parseIntentYaml, type Claims } from "./schema.js";

export interface RegisterOptions {
  /** Project root containing intent.yaml + tests/, used as a default for both lists. */
  packRoot?: string;
  /** Override: explicit list of intent.yaml file paths. */
  intentYamlPaths?: string[];
  /** Override: explicit list of test directories to scan. */
  testsDirs?: string[];
}

/**
 * Registers two meta-tests with vitest:
 *   - intent.schema  — every claim conforms to required fields + valid values
 *   - intent.coverage — every claim has a test, every annotated test has a claim
 *
 * Both tests pass vacuously if no claims are declared (empty / missing intent.yaml).
 */
export function registerIntentMetaTests(opts: RegisterOptions = {}): void {
  const intentPaths = resolveIntentPaths(opts);
  const testDirs = resolveTestDirs(opts);

  test("intent.schema — every claim conforms to schema", () => {
    const claims = mergedClaims(intentPaths);
    if (Object.keys(claims).length === 0) return;
    const violations = checkSchema(claims);
    expect(violations, violations.join("\n  ")).toEqual([]);
  });

  test("intent.coverage — claims and tests are 1:1", () => {
    const claims = mergedClaims(intentPaths);
    if (Object.keys(claims).length === 0) return;
    const annotated = mergedAnnotated(testDirs);
    const violations = coverageViolations(claims, annotated);
    expect(violations, violations.join("\n  ")).toEqual([]);
  });
}

function resolveIntentPaths(opts: RegisterOptions): string[] {
  if (opts.intentYamlPaths && opts.intentYamlPaths.length > 0) {
    return opts.intentYamlPaths;
  }
  if (opts.packRoot) {
    return [join(opts.packRoot, "intent.yaml")];
  }
  return ["intent.yaml"];
}

function resolveTestDirs(opts: RegisterOptions): string[] {
  if (opts.testsDirs && opts.testsDirs.length > 0) {
    return opts.testsDirs;
  }
  if (opts.packRoot) {
    return [join(opts.packRoot, "tests")];
  }
  return ["tests"];
}

function mergedClaims(paths: string[]): Claims {
  const out: Claims = {};
  for (const p of paths) {
    if (!existsSync(p)) continue;
    Object.assign(out, parseIntentYaml(p));
  }
  return out;
}

function mergedAnnotated(dirs: string[]): AnnotatedTests {
  const out: AnnotatedTests = {};
  for (const d of dirs) {
    const found = collectAnnotatedTests(d);
    for (const [cid, refs] of Object.entries(found)) {
      if (!out[cid]) out[cid] = [];
      out[cid].push(...refs);
    }
  }
  return out;
}
