"""Optional Sentry error reporting. No-ops unless SENTRY_DSN is set, so dev and tests
never phone home. PII is scrubbed by disabling send_default_pii."""

from __future__ import annotations

import logging

from app.core.config import Settings

logger = logging.getLogger("quantastica.observability")


def init_sentry(settings: Settings) -> None:
    if not settings.sentry_dsn:
        return
    try:
        import sentry_sdk
    except ImportError:
        logger.warning("SENTRY_DSN set but sentry-sdk is not installed; skipping")
        return
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.app_env,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        send_default_pii=False,
    )
    logger.info("Sentry initialised for env=%s", settings.app_env)
