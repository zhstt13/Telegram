import io
import json
import os
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

FILES = {
    "LoPRax_Phoenix.png": "imported/images/LoPRax_Phoenix.png",
    "Gothic_Rose_Parchment_Frame.pdf": "imported/pdf/Gothic_Rose_Parchment_Frame.pdf",
}

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def main():
    info = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    credentials = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    service = build("drive", "v3", credentials=credentials)

    manifest = []

    for name, output in FILES.items():
        result = service.files().list(
            q=f"name='{name}' and trashed=false",
            fields="files(id,name)"
        ).execute()

        files = result.get("files", [])
        if not files:
            continue

        file_id = files[0]["id"]
        request = service.files().get_media(fileId=file_id)
        Path(output).parent.mkdir(parents=True, exist_ok=True)

        with io.FileIO(output, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

        manifest.append({"name": name, "drive_id": file_id, "path": output})

    Path("imported/manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8"
    )


if __name__ == "__main__":
    main()
