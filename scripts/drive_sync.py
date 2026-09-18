import io
import json
import os
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

TARGETS = [
    ("image", "imported/images"),
    ("pdf", "imported/pdf"),
]

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def get_latest_file(service, mime_prefix):
    query = (
        "trashed=false and "
        f"mimeType contains '{mime_prefix}'"
    )

    result = service.files().list(
        q=query,
        orderBy="modifiedTime desc",
        pageSize=1,
        fields="files(id,name,modifiedTime)"
    ).execute()

    files = result.get("files", [])
    return files[0] if files else None


def main():
    info = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    credentials = service_account.Credentials.from_service_account_info(
        info, scopes=SCOPES
    )
    service = build("drive", "v3", credentials=credentials)

    manifest = []

    for mime_prefix, folder in TARGETS:
        file = get_latest_file(service, mime_prefix)
        if not file:
            continue

        original_name = file["name"]
        output = Path(folder) / original_name
        output.parent.mkdir(parents=True, exist_ok=True)

        request = service.files().get_media(fileId=file["id"])
        with io.FileIO(output, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

        manifest.append({
            "name": original_name,
            "drive_id": file["id"],
            "modifiedTime": file.get("modifiedTime"),
            "path": str(output)
        })

    Path("imported/manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8"
    )


if __name__ == "__main__":
    main()
