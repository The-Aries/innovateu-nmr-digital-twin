"""Configuration and deterministic artifact I/O."""

import hashlib
import json
import os
from collections.abc import Mapping
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from .contracts import Config, ObjectRef


def setting(config: Config, *keys: str) -> Any:
    entry = config
    for key in keys:
        entry = entry[key]
    if not isinstance(entry, Mapping) or "value" not in entry:
        raise ValueError(f"Invalid configuration entry {'.'.join(keys)}")
    return entry["value"]


def load_config(path: Path) -> Config:
    config = json.loads(path.read_text(encoding="utf-8"))
    if not setting(config, "config_version"):
        raise ValueError("Configuration version is required")
    return config


def canonical_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_ref(path: Path) -> ObjectRef:
    return {"path": str(path), "sha256": sha256_bytes(path.read_bytes())}


def write_json(path: Path, obj: Any) -> ObjectRef:
    data = canonical_bytes(obj)
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as scratch:
        temporary = Path(scratch.name)
        try:
            scratch.write(data)
            scratch.flush()
            os.fsync(scratch.fileno())
            scratch.close()
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)
    return {"path": str(path), "sha256": sha256_bytes(data)}
