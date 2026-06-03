"""Sanity test: version string is correct."""

import cyberagent


def test_version_is_string():
    assert isinstance(cyberagent.__version__, str)


def test_version_format():
    parts = cyberagent.__version__.split(".")
    assert len(parts) == 3
    assert all(p.isdigit() for p in parts)
