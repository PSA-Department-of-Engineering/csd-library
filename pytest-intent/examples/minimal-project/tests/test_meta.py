"""Wires pytest-intent meta-tests into this example project."""

from pytest_intent.meta_tests import (  # noqa: F401
    test_intent_schema,
    test_intent_coverage,
    intent_yaml_paths,
    intent_tests_dirs,
)
