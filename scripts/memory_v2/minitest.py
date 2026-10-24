"""Run the memory_v2 unit tests without pytest (the /opt/mwam env has none).

    /opt/mwam/bin/python scripts/memory_v2/minitest.py [test_train_v2 test_motion ...]   (default: all)

Supports what the tests use: pytest.approx, pytest.raises, pytest.importorskip, pytest.mark.parametrize,
the tmp_path fixture. Exit code 1 if any test fails. Not a pytest replacement for anything else.
"""
from __future__ import annotations

import importlib
import inspect
import math
import sys
import tempfile
import traceback
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


class _Approx:
    def __init__(self, value, rel=1e-6, abs=1e-12):
        self.value, self.rel, self.abs = value, rel, abs

    def __eq__(self, other):
        try:
            import numpy as np
            if isinstance(self.value, (list, tuple, np.ndarray)) or hasattr(other, "__len__"):
                return bool(np.allclose(np.asarray(other, float), np.asarray(self.value, float), rtol=self.rel, atol=self.abs))
        except ImportError:
            pass
        return math.isclose(float(other), float(self.value), rel_tol=self.rel, abs_tol=self.abs)

    __req__ = __eq__

    def __repr__(self):
        return f"approx({self.value})"


class _Raises:
    def __init__(self, exc, match=None):
        self.exc, self.match = exc, match

    def __enter__(self):
        return self

    def __exit__(self, kind, value, tb):
        if kind is None:
            raise AssertionError(f"expected {self.exc.__name__}")
        ok = issubclass(kind, self.exc)
        if ok and self.match:
            import re
            ok = re.search(self.match, str(value)) is not None
        return ok


def _importorskip(name, *a, **k):
    try:
        return importlib.import_module(name)
    except ImportError:
        raise _Skip(name)


class _Skip(Exception):
    pass


def _parametrize(names, values):
    def deco(fn):
        fn._params = (names, values)
        return fn
    return deco


def pytest_shim():
    pt = types.ModuleType("pytest")
    pt.approx = _Approx
    pt.raises = _Raises
    pt.importorskip = _importorskip
    pt.skip = lambda msg="": (_ for _ in ()).throw(_Skip(msg))
    pt.mark = types.SimpleNamespace(parametrize=_parametrize, skip=lambda *a, **k: (lambda f: f),
                                    skipif=lambda *a, **k: (lambda f: f))
    return pt


def main(argv):
    sys.modules["pytest"] = pytest_shim()
    tests_dir = ROOT / "src" / "fastwam" / "memory_v2" / "tests"
    names = argv or sorted(p.stem for p in tests_dir.glob("test_*.py"))
    passed = failed = skipped = 0
    for name in names:
        try:
            module = importlib.import_module(f"fastwam.memory_v2.tests.{name}")
        except _Skip as s:
            print(f"SKIP {name} (needs {s})")
            skipped += 1
            continue
        for attr in sorted(dir(module)):
            if not attr.startswith("test_"):
                continue
            fn = getattr(module, attr)
            params = getattr(fn, "_params", None)
            cases = [{}]
            if params:
                keys = [k.strip() for k in params[0].split(",")]
                cases = [dict(zip(keys, v if isinstance(v, (tuple, list)) and len(keys) > 1 else (v,))) for v in params[1]]
            for case in cases:
                kwargs = dict(case)
                if "tmp_path" in inspect.signature(fn).parameters:
                    kwargs["tmp_path"] = Path(tempfile.mkdtemp(prefix="minitest_"))
                label = f"{name}::{attr}" + (f"[{case}]" if case else "")
                try:
                    fn(**kwargs)
                    passed += 1
                except _Skip as s:
                    print(f"SKIP {label} ({s})")
                    skipped += 1
                except Exception:
                    failed += 1
                    print(f"FAIL {label}")
                    traceback.print_exc()
    print(f"{passed} passed, {failed} failed, {skipped} skipped")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
