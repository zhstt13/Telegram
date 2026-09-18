import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("binary_hub")
MANIFEST = ROOT / "manifest.json"


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def detect_type(name, mime_type=None):
    mime_type = (mime_type or "").lower()
    ext = Path(name).suffix.lower()

    if mime_type.startswith("image/") or ext in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}:
        return "images"
    if mime_type == "application/pdf" or ext == ".pdf":
        return "pdf"
    if mime_type.startswith("video/") or ext in {".mp4", ".mov", ".mkv", ".webm", ".avi"}:
        return "video"
    if mime_type.startswith("audio/") or ext in {".mp3", ".wav", ".m4a", ".ogg", ".flac"}:
        return "audio"
    if ext in {".zip", ".7z", ".rar", ".tar", ".gz", ".bz2", ".xz"}:
        return "archives"
    return "other"


def normalize_destination(destination):
    value = (destination or "edit").strip().lower()
    aliases = {
        "telegram": "telegram",
        "bot": "telegram",
        "robot": "telegram",
        "edit": "edit",
        "edit-queue": "edit",
        "editor": "edit",
    }
    if value not in aliases:
        raise ValueError(f"Unsupported destination: {destination}")
    return aliases[value]


def _read_json(path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return fallback


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _clear_stale_ticket(destination):
    stale = (
        ROOT / "edit-queue" / "ticket.json"
        if destination == "telegram"
        else ROOT / "outbox" / "telegram" / "ticket.json"
    )
    if stale.exists():
        stale.unlink()


def route_file(source_path, metadata, destination, request_id):
    source_path = Path(source_path)
    destination = normalize_destination(destination)
    category = detect_type(source_path.name, metadata.get("mime_type"))

    if destination == "telegram":
        ticket_path = ROOT / "outbox" / "telegram" / "ticket.json"
    else:
        ticket_path = ROOT / "edit-queue" / "ticket.json"

    _clear_stale_ticket(destination)

    ticket = {
        "version": 1,
        "request_id": request_id,
        "created_at": utc_now(),
        "source": "google_drive",
        "destination": destination,
        "category": category,
        "name": source_path.name,
        "canonical_path": source_path.as_posix(),
        "drive_id": metadata.get("drive_id"),
        "mime_type": metadata.get("mime_type"),
        "modified_time": metadata.get("modified_time"),
        "size": metadata.get("size"),
    }
    _write_json(ticket_path, ticket)

    manifest = _read_json(
        MANIFEST,
        {"version": "2.0", "latest_file": None, "history": []},
    )
    history = manifest.get("history")
    if not isinstance(history, list):
        history = []

    manifest.update(
        {
            "version": "2.0",
            "latest_file": ticket,
            "source": "google_drive",
            "route": destination,
            "destination": ticket_path.parent.as_posix(),
            "updated_at": utc_now(),
            "history": (history + [ticket])[-100:],
        }
    )
    _write_json(MANIFEST, manifest)
    return ticket


if __name__ == "__main__":
    print(json.dumps({"status": "ready", "engine": "binary_intake_router"}))
