"""CLI REPL — proves the kernel is surface-agnostic (zero Twilio)."""
from __future__ import annotations

import asyncio
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from .config import load_config
from .kernel.harness import Harness


async def _async_main() -> None:
    cfg = load_config()
    harness = Harness.create(cfg)
    session_id = "cli"
    print("Wakeel CLI — discipline kernel (draft → verify). Ctrl+C to exit.\n")
    while True:
        try:
            text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        if not text:
            continue
        reply = await harness.respond(session_id, text)
        print(f"\nWakeel: {reply}\n")


def main() -> None:
    asyncio.run(_async_main())


if __name__ == "__main__":
    main()
