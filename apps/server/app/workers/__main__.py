"""Worker entry point: `python -m app.workers`. Handles SIGINT/SIGTERM for graceful
shutdown so an in-flight tick finishes before the process exits."""

from __future__ import annotations

import asyncio
import contextlib
import signal

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.workers.runner import run_forever


async def _main() -> None:
    settings = get_settings()
    configure_logging(settings.app_env, settings.log_level)
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        with contextlib.suppress(NotImplementedError):
            loop.add_signal_handler(sig, stop.set)
    await run_forever(stop)


if __name__ == "__main__":
    asyncio.run(_main())
