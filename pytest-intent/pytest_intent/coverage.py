"""Intent ↔ test coverage analysis.

Walks tests/*.py via AST (no import) — finds `@intent("INT-NNN")` decorators on test
functions and builds the mapping. AST avoids import-side-effect failures (relative
imports, missing fixtures, etc.) while still seeing the decorator annotations.
"""

from __future__ import annotations

import ast
from pathlib import Path


def _extract_intent_ids_from_decorator(node: ast.expr) -> list[str]:
    """If `node` is a call to `intent(...)`, return the string args. Else empty list."""
    if not isinstance(node, ast.Call):
        return []
    func = node.func
    name = None
    if isinstance(func, ast.Name):
        name = func.id
    elif isinstance(func, ast.Attribute):
        name = func.attr
    if name != "intent":
        return []
    out: list[str] = []
    for arg in node.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            out.append(arg.value)
    return out


def collect_annotated_tests(tests_dir: Path) -> dict[str, list[str]]:
    """Return {claim_id: [test_refs]}. Test ref format: tests/<file>.py::<func>."""
    out: dict[str, list[str]] = {}
    if not tests_dir.exists():
        return out
    for path in tests_dir.glob("test_*.py"):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef) and not isinstance(node, ast.AsyncFunctionDef):
                continue
            if not node.name.startswith("test_"):
                continue
            for dec in node.decorator_list:
                claim_ids = _extract_intent_ids_from_decorator(dec)
                if not claim_ids:
                    continue
                ref = f"tests/{path.name}::{node.name}"
                for cid in claim_ids:
                    out.setdefault(cid, []).append(ref)
    return out


def _suggest(target: str, candidates: set[str], n: int = 3) -> list[str]:
    """Return up to n closest candidate IDs by edit distance."""
    import difflib
    return difflib.get_close_matches(target, list(candidates), n=n, cutoff=0.6)


def coverage_violations(claims: dict[str, dict[str, object]], annotated: dict[str, list[str]]) -> list[str]:
    """Return violations: claims without tests, tests referencing non-claims.

    On orphan-test violations (test references a claim that doesn't exist), include
    fuzzy-match suggestions for the likely-intended claim ID.
    """
    violations: list[str] = []
    claim_ids = set(claims.keys())
    annotated_ids = set(annotated.keys())

    uncovered = sorted(claim_ids - annotated_ids)
    for cid in uncovered:
        violations.append(f"{cid}: no @intent-decorated test serves this claim")

    orphan = sorted(annotated_ids - claim_ids)
    for cid in orphan:
        refs = annotated.get(cid, [])
        suggestions = _suggest(cid, claim_ids)
        suggestion_part = f" — did you mean one of: {suggestions}?" if suggestions else ""
        violations.append(f"{cid}: tests reference this claim but it doesn't exist in intent.yaml ({refs}){suggestion_part}")

    return violations
