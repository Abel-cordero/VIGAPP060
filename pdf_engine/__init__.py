"""Compatibility wrapper exposing ``src.pdf_engine`` as top-level package."""
from importlib import import_module
_module = import_module("src.pdf_engine")

globals().update(_module.__dict__)
__all__ = getattr(_module, "__all__", [k for k in globals() if not k.startswith("_")])
__path__ = _module.__path__
