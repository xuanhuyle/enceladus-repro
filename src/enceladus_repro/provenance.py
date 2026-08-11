"""Provenance-enforcing download helper.

Implements CLAUDE.md Rule 2: every downloaded file gets its URL + SHA256 logged
in data/MANIFEST.md, with a UTC retrieval timestamp.

A file that is not in the manifest is not evidence. The only supported way to
put a file under ``data/`` is :func:`fetch`, so that the manifest cannot drift
out of sync with what is on disk.
"""

from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
MANIFEST = DATA_DIR / "MANIFEST.md"

# Marker after which manifest rows are appended. Must match data/MANIFEST.md.
_TABLE_MARKER = "<!-- MANIFEST-ROWS -->"

_CHUNK_BYTES = 1 << 16


class FetchError(RuntimeError):
    """Raised when a download fails. Scripts fail loudly; they do not fall back."""


def sha256_file(path: Path) -> str:
    """Return the hex SHA256 of a file, read in chunks."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(_CHUNK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _ensure_manifest() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not MANIFEST.exists():
        raise FetchError(
            f"{MANIFEST} is missing. It is a tracked file and must exist before "
            "any download; recreate it from git rather than letting a fetch "
            "silently start a new provenance record."
        )


def log_to_manifest(url: str, path: Path, sha256: str, size_bytes: int, note: str = "") -> None:
    """Append one provenance row to data/MANIFEST.md.

    Idempotent on (relative path, sha256): re-fetching identical bytes does not
    duplicate the row, so reruns stay clean.
    """
    _ensure_manifest()
    rel = path.relative_to(REPO_ROOT).as_posix()
    retrieved = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    text = MANIFEST.read_text(encoding="utf-8")
    if f"| `{rel}` |" in text and sha256 in text:
        return  # already recorded with these exact bytes

    row = (
        f"| `{rel}` | {size_bytes} bytes | `{sha256}` | {retrieved} | {url} | {note} |\n"
    )
    if _TABLE_MARKER not in text:
        raise FetchError(
            f"{MANIFEST} has no {_TABLE_MARKER} marker; refusing to guess where "
            "to append the provenance row."
        )
    text = text.replace(_TABLE_MARKER, _TABLE_MARKER + "\n" + row.rstrip("\n"), 1)
    MANIFEST.write_text(text, encoding="utf-8")


def fetch(url: str, dest: Path, note: str = "", timeout: int = 120) -> Path:
    """Download ``url`` to ``dest``, then log URL + SHA256 to the manifest.

    Raises :class:`FetchError` on any non-200 response or transport failure.
    There is deliberately no retry-with-alternate-source and no cached fallback:
    per CLAUDE.md, a blocked fetch is UNRESOLVED, not something to route around.
    """
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Honours HTTPS_PROXY / REQUESTS_CA_BUNDLE from the environment.
        response = requests.get(url, stream=True, timeout=timeout)
    except requests.RequestException as exc:
        raise FetchError(f"transport failure for {url}: {exc!r}") from exc

    if response.status_code != 200:
        raise FetchError(
            f"HTTP {response.status_code} for {url} "
            f"(body starts: {response.text[:200]!r})"
        )

    tmp = dest.with_suffix(dest.suffix + ".partial")
    with open(tmp, "wb") as handle:
        for chunk in response.iter_content(chunk_size=_CHUNK_BYTES):
            handle.write(chunk)
    os.replace(tmp, dest)

    digest = sha256_file(dest)
    size = dest.stat().st_size
    log_to_manifest(url, dest, digest, size, note=note)
    print(f"[fetch] {url}\n        -> {dest} ({size} bytes)\n        sha256 {digest}")
    return dest
