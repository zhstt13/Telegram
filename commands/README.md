# Command Layer

This folder contains the command contract used by ChatGPT to trigger repository workflows.

## Binary command

When the user's intent involves the latest Google Drive binary, ChatGPT writes a normalized command to `commands/command.json`.

Example — send latest binary to Telegram:

```json
{
  "action": "route_latest_binary",
  "source": "google_drive",
  "destination": "telegram",
  "request_id": "unique-request-id",
  "status": "requested"
}
```

Example — send latest binary into the edit cycle:

```json
{
  "action": "route_latest_binary",
  "source": "google_drive",
  "destination": "edit",
  "request_id": "unique-request-id",
  "status": "requested"
}
```

## Intent rule

The user does not need to use a fixed phrase. ChatGPT resolves the user's intent and writes the normalized command.

Typical intents may be expressed as:
- send it to the bot
- put the output in Telegram
- move the latest file into editing
- work on the Drive file first
- use the latest project file

## Execution flow

ChatGPT intent
→ `commands/command.json`
→ Google Drive Sync Pipeline
→ Binary Hub canonical inbox
→ route ticket
→ Telegram OR edit queue

Every new execution should use a new `request_id`. This lets downstream handlers distinguish a new user request from an already completed request.
