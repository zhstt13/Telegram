import io
import json
import os
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from binary_intake_router import detect_type, route_file

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
COMMAND_PATH = Path("commands/command.json")
INBOX_ROOT = Path("binary_hub/inbox/google-drive")

TEXTUAL_MIME_TYPES = {
    "application/json",
    "application/xml",
    "application/javascript",
    "application/x-javascript",
}


def load_command():
    try:
        return json.loads(COMMAND_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def is_binary_candidate(item):
    mime = (item.get("mimeType") or "").lower()
    if not mime or mime == "application/vnd.google-apps.folder":
        return False
    if mime.startswith("application/vnd.google-apps."):
        return False
    if mime.startswith("text/") or mime in TEXTUAL_MIME_TYPES:
        return False
    return True


def latest_binary_file(service):
    folder_id = os.environ.get("DRIVE_FOLDER_ID", "").strip()
    query = "trashed=false"
    if folder_id:
        query += f" and '{folder_id}' in parents"

    page_token = None
    while True:
        result = service.files().list(
            q=query,
            orderBy="modifiedTime desc",
            pageSize=100,
            pageToken=page_token,
            fields="nextPageToken,files(id,name,mimeType,size,modifiedTime)",
        ).execute()

        for item in result.get("files", []):
            if is_binary_candidate(item):
                return item

        page_token = result.get("nextPageToken")
        if not page_token:
            return None


def safe_name(name):
    cleaned = Path(name or "drive-file.bin").name.strip()
    return cleaned or "drive-file.bin"


def download_file(service, item):
    name = safe_name(item.get("name"))
    category = detect_type(name, item.get("mimeType"))
    output = INBOX_ROOT / category / name
    output.parent.mkdir(parents=True, exist_ok=True)

    request = service.files().get_media(fileId=item["id"])
    with io.FileIO(output, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

    return output


def main():
    command = load_command()
    destination = command.get("destination")
    source = (command.get("source") or "google_drive").lower()

    if not destination or source not in {"google_drive", "drive", "latest_file", "latest_binary"}:
        print("No Google Drive binary routing command requested.")
        return

    request_id = str(
        command.get("request_id")
        or os.environ.get("GITHUB_RUN_ID")
        or "manual"
    )

    info = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    credentials = service_account.Credentials.from_service_account_info(
        info, scopes=SCOPES
    )
    service = build("drive", "v3", credentials=credentials)

    item = latest_binary_file(service)
    if not item:
        raise RuntimeError("No binary file is available in Google Drive.")

    output = download_file(service, item)
    ticket = route_file(
        output,
        {
            "drive_id": item.get("id"),
            "mime_type": item.get("mimeType"),
            "modified_time": item.get("modifiedTime"),
            "size": item.get("size"),
        },
        destination,
        request_id,
    )

    print(json.dumps(ticket, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
