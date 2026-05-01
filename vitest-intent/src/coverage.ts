/**
 * AST-free coverage walker.
 *
 * Scans test files for `intent('INT-XXX-NNN', ...)` calls via regex.
 * Mirrors pytest-intent's AST-based collector — slightly weaker (no scope
 * awareness, can't follow aliases), but zero TypeScript-compiler dependency.
 *
 * Returns a map of claim ID -> array of "<file>::<test name>" pointers.
 */

import { readFileSync, readdirSync, statSync } from "node:fs";
import { extname, join, relative, sep } from "node:path";

import type { Claims } from "./schema.js";

const TEST_EXT = new Set([".ts", ".tsx", ".mts", ".cts", ".js", ".jsx", ".mjs", ".cjs"]);
const TEST_FILE_RE = /\.(test|spec)\./;

// Matches intent('INT-XXX', "test name", ...) OR intent("INT-XXX", "test name", ...)
// Also handles arrays: intent(['INT-XXX', 'INT-YYY'], 'name', ...)
const INTENT_CALL_RE =
  /\bintent\s*\(\s*(?:\[\s*([^\]]+?)\s*\]|(['"`])(INT-[A-Z0-9-]+)\2)\s*,\s*(['"`])([\s\S]*?)\4\s*,/g;

const ID_IN_LIST_RE = /['"`](INT-[A-Z0-9-]+)['"`]/g;

export interface AnnotatedTests {
  [claimId: string]: string[];
}

/**
 * Walk `testsDir` and collect all `intent(...)` calls.
 *
 * Returns map of claim ID -> array of "<rel-file-path>::<test name>" pointers.
 */
export function collectAnnotatedTests(testsDir: string): AnnotatedTests {
  const out: AnnotatedTests = {};
  if (!existsAndIsDir(testsDir)) {
    return out;
  }

  for (const file of walk(testsDir)) {
    if (!TEST_FILE_RE.test(file)) {
      continue;
    }
    if (!TEST_EXT.has(extname(file))) {
      continue;
    }
    let text: string;
    try {
      text = readFileSync(file, "utf-8");
    } catch {
      continue;
    }

    // reset regex state across files
    INTENT_CALL_RE.lastIndex = 0;
    let m: RegExpExecArray | null;
    while ((m = INTENT_CALL_RE.exec(text)) !== null) {
      const ids: string[] = [];
      if (m[1]) {
        // array form
        ID_IN_LIST_RE.lastIndex = 0;
        let lm: RegExpExecArray | null;
        while ((lm = ID_IN_LIST_RE.exec(m[1])) !== null) {
          ids.push(lm[1]);
        }
      } else if (m[3]) {
        ids.push(m[3]);
      }
      const testName = m[5];
      const rel = relative(testsDir, file).split(sep).join("/");
      const ref = `tests/${rel}::${testName}`;
      for (const cid of ids) {
        if (!out[cid]) out[cid] = [];
        out[cid].push(ref);
      }
    }
  }
  return out;
}

/**
 * Compare claims against annotated tests. Returns violation strings.
 */
export function coverageViolations(
  claims: Claims,
  annotated: AnnotatedTests,
): string[] {
  const violations: string[] = [];
  const claimIds = new Set(Object.keys(claims));
  const annotatedIds = new Set(Object.keys(annotated));

  for (const cid of claimIds) {
    if (!annotatedIds.has(cid)) {
      violations.push(`claim ${cid} has no test (no \`intent('${cid}', ...)\` found)`);
    }
  }
  for (const cid of annotatedIds) {
    if (!claimIds.has(cid)) {
      const refs = annotated[cid].join(", ");
      violations.push(`test references ${cid} but no such claim in intent.yaml (${refs})`);
    }
  }
  return violations;
}

function existsAndIsDir(p: string): boolean {
  try {
    return statSync(p).isDirectory();
  } catch {
    return false;
  }
}

function* walk(dir: string): Generator<string> {
  for (const name of readdirSync(dir)) {
    const full = join(dir, name);
    let st;
    try {
      st = statSync(full);
    } catch {
      continue;
    }
    if (st.isDirectory()) {
      if (name === "node_modules" || name === "dist" || name === ".git") continue;
      yield* walk(full);
    } else if (st.isFile()) {
      yield full;
    }
  }
}
