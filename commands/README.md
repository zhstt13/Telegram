# Command Layer

This folder contains commands that route ChatGPT requests to GitHub workflows.

Flow:

ChatGPT request -> command.json -> GitHub Actions router -> operation handler -> destination

Supported actions will include:
- send
- sync
- build
- process
- export
