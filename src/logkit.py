#!/usr/bin/env -S uv run --script
# pyright: skip-file
# %%pep 723
# requires-python = ">=3.10"
# dependencies = [
#   "structlog>=24.1",
# ]

import asyncio
import contextvars
import functools
import logging
import os
import pathlib
import time
import uuid
from logging.handlers import RotatingFileHandler
from typing import Any, Callable

import structlog

# ---------------------------------------------------------------- context plumbing
_CTX: contextvars.ContextVar[dict[str, Any] | None] = contextvars.ContextVar(
    'ctx', default=None
)


def _merge_ctx(_, __, event):  # inject current ContextVars into every event
    ctx = _CTX.get()
    if ctx:
        event.update(ctx)
    return event


# ---------------------------------------------------------------- file handler (offline-friendly)
def _attach_file_handler(path: str | os.PathLike, rotate_mb: int) -> None:
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(path, maxBytes=rotate_mb * 1_048_576, backupCount=5)
    handler.setFormatter(logging.Formatter('%(message)s'))
    logging.getLogger().addHandler(handler)


# ---------------------------------------------------------------- global configure
def _configure_once() -> None:
    profile = os.getenv('LOG_PROFILE', 'dev').lower()  # dev | prod
    base_lvl = getattr(
        logging, os.getenv('LOG_LEVEL', 'DEBUG' if profile == 'dev' else 'INFO').upper()
    )
    sample = float(os.getenv('LOG_SAMPLE', 1))  # 1 = keep all
    log_file = os.getenv('LOG_FILE', 'run.log')  # JSONL sink for offline agents
    rotate_mb = int(os.getenv('LOG_ROTATE_MB', 10))

    processors = [
        structlog.contextvars.merge_contextvars,
        _merge_ctx,
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.stdlib.add_log_level,
    ]
    try:
        sample_proc = structlog.processors.SampleByLevel(
            lower=logging.DEBUG,
            upper=logging.INFO,
            sample_rate=sample,
        )
        processors.append(sample_proc)
    except AttributeError:
        pass
    processors.extend(
        [
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()
            if profile == 'dev'
            else structlog.processors.JSONRenderer(),
        ]
    )

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(base_lvl),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        level=base_lvl, handlers=[logging.StreamHandler()]
    )  # std-lib parity

    if log_file:  # local JSONL file so agents can read after the run
        _attach_file_handler(log_file, rotate_mb)


_CONFIG_FLAG = '_LOGKIT_CONFIGURED'
if _CONFIG_FLAG not in globals():
    _configure_once()
    globals()[_CONFIG_FLAG] = True

log = structlog.get_logger()  # ← every import gets the same, fully wired logger


# ---------------------------------------------------------------- public helpers
def new_context(**kv: Any) -> str:
    """
    Clear any stale context, start (or continue) a trace and bind user-supplied keys.
    Returns the active trace_id so callers can forward it across process boundaries.
    """
    structlog.contextvars.clear_contextvars()
    trace_id = kv.pop('trace_id', uuid.uuid4().hex)
    all_kv = {'trace_id': trace_id, **kv}
    structlog.contextvars.bind_contextvars(**all_kv)
    _CTX.set(all_kv)
    return trace_id


class capture:
    """
    Decorator *and* context-manager.
    * Adds span_id, logs one END record with dur_ms + status.
    * Works on sync and async functions.
    """

    def __init__(self, **kv):
        self._kv = kv

    # -- decorator -----------------------------------------------------------
    def __call__(self, fn: Callable):
        if asyncio.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def awrapper(*a, **kw):
                with self.__class__(fn=fn.__qualname__, **self._kv):
                    return await fn(*a, **kw)

            return awrapper
        else:

            @functools.wraps(fn)
            def swrapper(*a, **kw):
                with self.__class__(fn=fn.__qualname__, **self._kv):
                    return fn(*a, **kw)

            return swrapper

    # -- context-manager -----------------------------------------------------
    def __enter__(self):
        self._t0 = time.perf_counter()
        self._span = {'span_id': uuid.uuid4().hex, **self._kv}
        structlog.contextvars.bind_contextvars(**self._span)
        return self

    def __exit__(self, exc_type, exc, __):
        dur_ms = int((time.perf_counter() - self._t0) * 1000)
        logger = log.exception if exc else log.info
        logger('END', dur_ms=dur_ms, status='error' if exc else 'success', exc_info=exc)
        structlog.contextvars.unbind_contextvars(*self._span.keys())
        return False  # re-raise exceptions


# ---------------------------------------------------------------- optional async helper
def ctx_task(coro):
    """
    Schedule an asyncio Task that inherits the *current* ContextVars snapshot.
    Use instead of `asyncio.create_task` to avoid the “spawn-before-bind” foot-gun.
    """
    ctx = contextvars.copy_context()
    return asyncio.create_task(ctx.run(coro))
