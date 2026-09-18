# Binary Hub

Central storage layer for binary files entering from Google Drive.

Flow:

Google Drive
→ binary_hub/inbox/google-drive
→ route
→ edit-queue OR outbox/telegram

Rules:
- Keep original binary files unchanged.
- Do not convert formats in intake stage.
- Processing happens only after routing.
