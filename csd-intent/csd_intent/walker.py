"""Multi-language walker that finds @intent / intent() markers in test files.

Two strategies:
  - .py    → AST walk for @intent("INT-...") decorators on test_ functions
  - .ts/.tsx/.js/.jsx/.mts/.cts → regex for intent('INT-...', name, fn) calls

Both produce {claim_id: [test_ref, ...]} where test_ref is "<rel-path>::<name>".
"""

from __future__ import annotations

import ast
import re
from collections.abc import Iterable
from pathlib import Path

__all__ = [
    "DEFAULT_EXCLUDE_DIRS",
    "INTENT_FILENAME",
    "JS_EXTS",
    "PY_EXT",
    "TEST_FILE_RE",
    "collect_attestations",
    "find_nested_intent_projects",
]

DEFAULT_EXCLUDE_DIRS = frozenset(
    {
        "node_modules",
        ".venv",
        "venv",
        "dist",
        "build",
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".tox",
        ".egg-info",
    }
)

PY_EXT = ".py"
JS_EXTS = frozenset({".ts", ".tsx", ".js", ".jsx", ".mts", ".cts"})

# A directory that contains this file (other than the scan root) is a *nested
# intent project* — a separate project boundary. The marker walk must not descend
# into it, so its markers do not orphan against the outer project's claims.
INTENT_FILENAME = "intent.yaml"
TEST_FILE_RE = re.compile(r"(^|[._-])(test|spec)([._-]|$)|test_|_test\.|\.test\.|\.spec\.")

# Matches intent('INT-XXX', "name", ...) OR intent("INT-XXX", "name", ...)
# Also array form: intent(['INT-X', 'INT-Y'], 'name', ...)
_JS_INTENT_RE = re.compile(
    r"\bintent\s*\(\s*"
    r"(?:\[\s*(?P<list>[^\]]+?)\s*\]|(?P<q1>['\"`])(?P<id>INT-[A-Z0-9-]+)(?P=q1))"
    r"\s*,\s*(?P<q2>['\"`])(?P<name>[\s\S]*?)(?P=q2)\s*,"
)
_JS_ID_IN_LIST_RE = re.compile(r"['\"`](INT-[A-Z0-9-]+)['\"`]")


def collect_attestations(
    test_dirs: Iterable[Path],
    exclude_dirs: frozenset[str] = DEFAULT_EXCLUDE_DIRS,
    respect_nested_projects: bool = True,
) -> dict[str, list[str]]:
    """Walk `test_dirs` and return {claim_id: [test_ref, ...]} for every intent marker.

    test_refs are formatted ``<rel-path>::<test-name>`` for readability in error output.

    When ``respect_nested_projects`` is True (the default), any subdirectory below a
    scanned root that contains its own ``intent.yaml`` is treated as a separate project
    boundary: the walk does not descend into it, so the nested project's markers do not
    orphan against the outer project's claims. The scanned root itself is never skipped,
    even though it normally contains an ``intent.yaml`` (it *is* the project under audit).
    """
    out: dict[str, list[str]] = {}
    for root in test_dirs:
        if not root.exists():
            continue
        base = root.resolve()
        for path in _walk_files(base, exclude_dirs, respect_nested_projects):
            if not _is_test_file(path):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            rel = path.relative_to(base).as_posix()
            if path.suffix == PY_EXT:
                _collect_from_python(text, rel, out)
            elif path.suffix in JS_EXTS:
                _collect_from_js(text, rel, out)
    return out


def _walk_files(
    root: Path,
    exclude_dirs: frozenset[str],
    respect_nested_projects: bool = True,
) -> Iterable[Path]:
    """Recursively yield files under ``root``, skipping excluded directory names.

    Stops descending into any nested intent-project subtree (a subdirectory that
    contains its own ``intent.yaml``) when ``respect_nested_projects`` is True. The
    starting ``root`` is always scanned even if it holds an ``intent.yaml``.
    """
    for entry in root.iterdir():
        if entry.is_symlink():
            continue
        if entry.is_dir():
            if entry.name in exclude_dirs:
                continue
            if respect_nested_projects and (entry / INTENT_FILENAME).is_file():
                # A nested intent project — a separate boundary. Do not descend.
                continue
            yield from _walk_files(entry, exclude_dirs, respect_nested_projects)
        elif entry.is_file():
            yield entry


def find_nested_intent_projects(
    root: Path,
    exclude_dirs: frozenset[str] = DEFAULT_EXCLUDE_DIRS,
) -> list[Path]:
    """Return directories *strictly below* ``root`` that hold their own ``intent.yaml``.

    The ``root`` itself is never included (it is the project being audited). Results are
    sorted for deterministic output. Each returned directory is the root of a separate
    intent project; auditing it with ``respect_nested_projects=True`` bounds its marker
    scan against any still-deeper nested projects, giving a complete, non-overlapping
    partition of the tree.
    """
    base = root.resolve()
    found: list[Path] = []

    def _descend(current: Path) -> None:
        for entry in sorted(current.iterdir()):
            if entry.is_symlink() or not entry.is_dir():
                continue
            if entry.name in exclude_dirs:
                continue
            if (entry / INTENT_FILENAME).is_file():
                found.append(entry)
            # Always descend further so deeper-nested projects are also discovered.
            _descend(entry)

    if base.is_dir():
        _descend(base)
    return found


def _is_test_file(path: Path) -> bool:
    """Is this file a test by conventional naming?"""
    name = path.name
    if path.suffix == PY_EXT:
        return name.startswith("test_") or name.endswith("_test.py")
    return bool(TEST_FILE_RE.search(name))


def _collect_from_python(text: str, rel_path: str, out: dict[str, list[str]]) -> None:
    """AST-walk a .py file looking for @intent("INT-...") decorators."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        if not node.name.startswith("test_"):
            continue
        for dec in node.decorator_list:
            for cid in _extract_ids_from_decorator(dec):
                ref = f"{rel_path}::{node.name}"
                out.setdefault(cid, []).append(ref)


def _extract_ids_from_decorator(node: ast.expr) -> list[str]:
    """If `node` is a call to `intent(...)`, return the claim-ID string args."""
    if not isinstance(node, ast.Call):
        return []
    func = node.func
    name = (
        func.id
        if isinstance(func, ast.Name)
        else func.attr
        if isinstance(func, ast.Attribute)
        else None
    )
    if name != "intent":
        return []
    ids: list[str] = []
    for arg in node.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value.startswith("INT-"):
            ids.append(arg.value)
    return ids


def _collect_from_js(text: str, rel_path: str, out: dict[str, list[str]]) -> None:
    """Regex-scan a JS/TS file for intent('INT-...', name, fn) calls."""
    for match in _JS_INTENT_RE.finditer(text):
        name = match.group("name")
        ids: list[str] = []
        if match.group("list"):
            ids.extend(_JS_ID_IN_LIST_RE.findall(match.group("list")))
        elif match.group("id"):
            ids.append(match.group("id"))
        for cid in ids:
            ref = f"{rel_path}::{name}"
            out.setdefault(cid, []).append(ref)
