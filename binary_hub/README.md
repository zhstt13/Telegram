# Binary Hub

Dedicated binary-file layer for files entering from Google Drive.

## Canonical flow

Google Drive
→ `binary_hub/inbox/google-drive/<type>/FILE`
→ routing ticket
→ `binary_hub/edit-queue/ticket.json` OR `binary_hub/outbox/telegram/ticket.json`

The actual binary has one canonical copy under `inbox/google-drive`. Route folders contain lightweight JSON tickets that point to that canonical file, so large files are not duplicated inside Git history.

## Routes

- `telegram`: send the original binary directly to the Telegram bot.
- `edit`: hand the original binary to the edit cycle.

## Rules

- Intake never converts file formats.
- Original bytes and original filename are preserved.
- Text and Google-native Workspace files are excluded from Binary Hub intake.
- Routing is command-driven through `commands/command.json`, not scheduled.
- A new command should use a new `request_id`.
- Telegram delivery records the last successful request under `binary_hub/sent/telegram.json` to prevent accidental duplicate sends.
