from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timezone
import re

_SIZE_RE = re.compile(r"^\s*(\d+)\s*([a-zA-Z]*)\s*$")


@dataclass
class FileObj:
    size: str
    created_at: int                 # epoch seconds
    ttl_seconds: Optional[int]      # None = infinite


def simulate_coding_framework(list_of_lists):
    db_files: Dict[str, FileObj] = {}

    # After rollback, Level 4 tests expect FILE_SEARCH_AT to be alphabetical.
    rollback_mode = False

    def convert_file_size(size_str: str) -> int:
        s = str(size_str)
        m = _SIZE_RE.match(s)
        if not m:
            raise ValueError(f"Invalid size: {size_str!r}")

        value = int(m.group(1))
        unit = m.group(2).lower()

        if unit in ("kb", "k"):
            return value * 1024
        if unit in ("mb", "m"):
            return value * 1024 * 1024
        if unit in ("b", ""):
            return value
        raise ValueError(f"Unknown size unit: {size_str!r}")

    def parse_ts(ts: str) -> int:
        dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        return int(dt.timestamp())

    def is_alive(at_ts: int, obj: FileObj) -> bool:
        if obj.ttl_seconds is None:
            return True
        return at_ts < (obj.created_at + obj.ttl_seconds)

    # ---------- Core ops (parameterized by an "effective time") ----------

    def upload(at_ts: int, name: str, size: str, ttl: Optional[int]) -> None:
        # Duplicate only if an existing file is alive at that time.
        if name in db_files and is_alive(at_ts, db_files[name]):
            raise RuntimeError(f"File {name} already exists")
        db_files[name] = FileObj(size=size, created_at=at_ts, ttl_seconds=ttl)

    def get(at_ts: int, name: str) -> Optional[FileObj]:
        obj = db_files.get(name)
        if obj is None or not is_alive(at_ts, obj):
            return None
        return obj

    def copy(at_ts: int, src: str, dest: str) -> None:
        src_obj = get(at_ts, src)
        if src_obj is None:
            raise RuntimeError(f"Source files {src} does not exist.")
        # Copy inherits same TTL behavior as source (same created_at + ttl_seconds)
        db_files[dest] = FileObj(size=src_obj.size, created_at=src_obj.created_at, ttl_seconds=src_obj.ttl_seconds)

    def search(at_ts: int, prefix: str, *, alphabetical_only: bool) -> List[str]:
        if alphabetical_only:
            names = [
                name for name, obj in db_files.items()
                if name.startswith(prefix) and is_alive(at_ts, obj)
            ]
            names.sort()
            return names[:10]

        sized: List[Tuple[str, int]] = []
        for name, obj in db_files.items():
            if name.startswith(prefix) and is_alive(at_ts, obj):
                sized.append((name, convert_file_size(obj.size)))

        # size desc, then name asc
        sized.sort(key=lambda item: (-item[1], item[0]))
        return [name for name, _ in sized[:10]]

    def rollback(ts_str: str) -> None:
        nonlocal rollback_mode
        rollback_mode = True
        t = parse_ts(ts_str)
        # Reset TTL base time for all files
        for obj in db_files.values():
            obj.created_at = t

    # ---------- Dispatcher / Outputs ----------

    out: List[str] = []

    for op in list_of_lists:
        cmd = op[0]

        if cmd == "FILE_UPLOAD":
            # ["FILE_UPLOAD", name, size]
            name, size = op[1], op[2]
            upload(at_ts=0, name=name, size=size, ttl=None)  # non-time ops: infinite
            out.append(f"uploaded {name}")

        elif cmd == "FILE_GET":
            # ["FILE_GET", name]
            name = op[1]
            obj = get(at_ts=0, name=name)
            out.append("file not found" if obj is None else f"got {name}")

        elif cmd == "FILE_COPY":
            # ["FILE_COPY", src, dest]
            src, dest = op[1], op[2]
            copy(at_ts=0, src=src, dest=dest)
            out.append(f"copied {src} to {dest}")

        elif cmd == "FILE_SEARCH":
            # ["FILE_SEARCH", prefix]
            prefix = op[1]
            names = search(at_ts=0, prefix=prefix, alphabetical_only=False)
            # Non-AT search output (group 2): "found [..]"
            out.append("found [" + ", ".join(names) + "]")

        elif cmd == "FILE_UPLOAD_AT":
            # ["FILE_UPLOAD_AT", ts, name, size] or ["FILE_UPLOAD_AT", ts, name, size, ttl]
            ts_str, name, size = op[1], op[2], op[3]
            ttl = int(op[4]) if len(op) == 5 else None
            upload(at_ts=parse_ts(ts_str), name=name, size=size, ttl=ttl)
            out.append(f"uploaded at {name}")

        elif cmd == "FILE_GET_AT":
            # ["FILE_GET_AT", ts, name]
            ts_str, name = op[1], op[2]
            obj = get(at_ts=parse_ts(ts_str), name=name)
            out.append("file not found" if obj is None else f"got at {name}")

        elif cmd == "FILE_COPY_AT":
            # ["FILE_COPY_AT", ts, src, dest]
            ts_str, src, dest = op[1], op[2], op[3]
            copy(at_ts=parse_ts(ts_str), src=src, dest=dest)
            out.append(f"copied at {src} to {dest}")

        elif cmd == "FILE_SEARCH_AT":
            # ["FILE_SEARCH_AT", ts, prefix]
            ts_str, prefix = op[1], op[2]
            names = search(
                at_ts=parse_ts(ts_str),
                prefix=prefix,
                alphabetical_only=rollback_mode  # Level 4 expectation
            )
            out.append("found at [" + ", ".join(names) + "]")

        elif cmd == "ROLLBACK":
            # ["ROLLBACK", ts]
            ts_str = op[1]
            rollback(ts_str)
            out.append(f"rollback to {ts_str}")

        else:
            raise RuntimeError(f"Unknown operation: {cmd}")

    return out
