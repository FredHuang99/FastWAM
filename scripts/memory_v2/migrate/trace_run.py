"""Run a Python module and record every file it touches (for the migration manifest).

    python trace_run.py --out trace.json -m fastwam.memory_v2.train_v2 evaluate --config ...

Sources: the 'open' audit event (Python open/io.open_code, incl. imports and torch.load) plus a
sampler of /proc/self/maps and /proc/self/fd every 0.5 s (mmapped safetensors, native readers).
"""
import json
import os
import runpy
import sys
import threading
import time

PATHS = set()
STOP = threading.Event()


def _hook(event, args):
    if event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
        try:
            PATHS.add(os.path.abspath(os.fsdecode(args[0])))
        except Exception:
            pass


def _sample():
    while not STOP.is_set():
        try:
            with open("/proc/self/maps") as f:
                for line in f:
                    parts = line.split(None, 5)
                    if len(parts) == 6 and parts[5].startswith("/"):
                        PATHS.add(parts[5].strip().replace(" (deleted)", ""))
            for fd in os.listdir("/proc/self/fd"):
                try:
                    target = os.readlink(f"/proc/self/fd/{fd}")
                    if target.startswith("/"):
                        PATHS.add(target)
                except OSError:
                    pass
        except Exception:
            pass
        STOP.wait(0.5)


def main():
    argv = sys.argv[1:]
    if len(argv) < 4 or argv[0] != "--out" or argv[2] != "-m":
        raise SystemExit("usage: trace_run.py --out TRACE.json -m MODULE [ARGS...]")
    out, module, rest = argv[1], argv[3], argv[4:]
    sys.addaudithook(_hook)
    thread = threading.Thread(target=_sample, daemon=True)
    thread.start()
    code, started = 0, time.time()
    sys.argv = [module] + rest
    sys.path[0] = os.getcwd()                 # as `python -m`: cwd first, not this script's folder
    try:
        runpy.run_module(module, run_name="__main__", alter_sys=True)
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    except BaseException:
        import traceback
        traceback.print_exc()
        code = 1
    finally:
        STOP.set()
        thread.join(timeout=2)
        files = sorted(p for p in PATHS if os.path.isfile(p))
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with open(out, "w") as f:
            json.dump({"module": module, "args": rest, "returncode": code, "seconds": time.time() - started,
                       "cwd": os.getcwd(), "files": files}, f, indent=1)
        print(f"[trace] {len(files)} files -> {os.path.abspath(out)} (exit {code})", flush=True)
    sys.exit(code)


if __name__ == "__main__":
    main()
