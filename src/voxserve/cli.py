"""`voxserve` command line: serve, pull, voices."""
from __future__ import annotations

import argparse
import sys

from . import __version__
from .settings import Settings


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="voxserve", description="Zero-GPU OpenAI-compatible voice server."
    )
    p.add_argument("--version", action="version", version=f"voxserve {__version__}")
    sub = p.add_subparsers(dest="cmd")

    serve = sub.add_parser("serve", help="start the HTTP server (default)")
    serve.add_argument("--host", default=None)
    serve.add_argument("--port", type=int, default=None)

    sub.add_parser("pull", help="download the Kokoro model files").add_argument(
        "--model-dir", default=None
    )

    sub.add_parser("voices", help="list available voices")

    return p


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    args = parser.parse_args(argv if argv else ["serve"])
    settings = Settings()

    if args.cmd in (None, "serve"):
        import uvicorn

        from .main import create_app

        host = args.host or settings.host
        port = args.port or settings.port
        uvicorn.run(create_app(settings), host=host, port=port)
        return 0

    if args.cmd == "pull":
        from .models import pull
        pull(args.model_dir or settings.model_dir)
        return 0

    if args.cmd == "voices":
        from .engines.kokoro import select_engine

        engine = select_engine(settings)
        for v in engine.voices():
            print(f"{v['id']:<16} {v['language']:<6} {v['name']}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
