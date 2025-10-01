"""Version requirement checks for the Monte package."""

from __future__ import annotations

import importlib
import sys
import types

import pytest


def test_import_fails_on_unsupported_python(monkeypatch):
    """Importing the package on Python < 3.11 should raise a helpful error."""

    fake_sys = types.ModuleType("sys")
    fake_sys.version_info = (3, 10, 9)
    fake_sys.modules = sys.modules

    monkeypatch.setitem(sys.modules, "sys", fake_sys)
    sys.modules.pop("monte", None)

    with pytest.raises(RuntimeError) as exc:
        importlib.import_module("monte")

    sys.modules.pop("monte", None)

    assert "Python 3.11 or newer" in str(exc.value)


def test_import_succeeds_on_supported_python(monkeypatch):
    """After restoring the interpreter version we can import the package."""

    fake_sys = types.ModuleType("sys")
    fake_sys.version_info = (3, 11, 0)
    fake_sys.modules = sys.modules

    monkeypatch.setitem(sys.modules, "sys", fake_sys)
    sys.modules.pop("monte", None)

    module = importlib.import_module("monte")

    assert module.__name__ == "monte"

    sys.modules.pop("monte", None)
