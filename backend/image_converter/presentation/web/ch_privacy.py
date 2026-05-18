"""ch_privacy.py — CH privacy and cleanup commitments for tools.campaign.help.

Adds:
  - Per-request UUID-based temp directory under /tmp/imgcompress-uploads/<uuid>/
  - After-request cleanup (within 60s of response completion)
  - A background sweeper thread removing any directory >10 minutes old
  - Cache-Control: no-store on every /api/* response
  - Log scrubbing: never log original filename or EXIF

The sweeper-thread interval is 60s; max-age is 600s. Both are constants
below — adjust if the SLA changes.
"""

import logging
import shutil
import threading
import time
import uuid
from pathlib import Path

from flask import Flask, g, request

UPLOAD_ROOT = Path("/tmp/imgcompress-uploads")
SWEEPER_INTERVAL_SECONDS = 60
SWEEPER_MAX_AGE_SECONDS = 600

_logger = logging.getLogger("ch_privacy")


def register(app: Flask) -> None:
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

    @app.before_request
    def _assign_request_uuid():
        g.request_uuid = uuid.uuid4().hex
        g.upload_dir = UPLOAD_ROOT / g.request_uuid
        # Lazily created on first write inside the request handler.

    @app.after_request
    def _add_no_store(response):
        if request.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, max-age=0"
        return response

    @app.teardown_request
    def _cleanup(_exc):
        upload_dir = getattr(g, "upload_dir", None)
        if upload_dir is not None and upload_dir.exists():
            shutil.rmtree(upload_dir, ignore_errors=True)

    def _sweeper():
        while True:
            time.sleep(SWEEPER_INTERVAL_SECONDS)
            now = time.time()
            try:
                for child in UPLOAD_ROOT.iterdir():
                    if not child.is_dir():
                        continue
                    age = now - child.stat().st_mtime
                    if age > SWEEPER_MAX_AGE_SECONDS:
                        shutil.rmtree(child, ignore_errors=True)
            except Exception as exc:  # noqa: BLE001 - sweeper must never crash
                _logger.warning("sweeper error: %s", exc)

    threading.Thread(target=_sweeper, daemon=True, name="ch-sweeper").start()
