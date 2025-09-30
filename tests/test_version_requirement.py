"""Version requirement checks for the Monte package."""

from __future__ import annotations

import importlib
import sys

import pytest


def test_import_fails_on_unsupported_python(monkeypatch):
    """Importing the package on Python < 3.11 should raise a helpful error."""

    monkeypatch.setattr(sys, "version_info", (3, 10, 9))
    sys.modules.pop("monte", None)

    with pytest.raises(RuntimeError) as exc:
        importlib.import_module("monte")

    assert "Python 3.11 or newer" in str(exc.value)


def test_import_succeeds_on_supported_python(monkeypatch):
    """After restoring the interpreter version we can import the package."""

    monkeypatch.setattr(sys, "version_info", (3, 11, 0))
    sys.modules.pop("monte", None)

    module = importlib.import_module("monte")

    assert module.__name__ == "monte"
