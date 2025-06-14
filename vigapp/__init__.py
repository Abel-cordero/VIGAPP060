"""Compatibility wrapper exposing the ``src.vigapp`` package as ``vigapp``."""

from importlib import import_module

_module = import_module("src.vigapp")

globals().update(_module.__dict__)

__all__ = getattr(_module, "__all__", [k for k in globals() if not k.startswith("_")])

# Ensure submodules can be imported from this package
__path__ = _module.__path__
