# tonia-api

Public API reference for [tonia Pass](https://pass.tonia.ca).

This covers the developer API only: unauthenticated catalogue / models /
status, plus authenticated runtime helpers (chat, messages, embeddings,
images, responses, rerank, interactions).

Workspace settings, billing, and API-key management stay in the
[tonia portal](https://portal.tonia.ca). Server-side chat history is
chat-app only — not part of this contract.

## Files

| Path | Role |
| --- | --- |
| `API.md` | Markdown API reference |
| `LICENSE` / `NOTICE` | Apache 2.0; copyright tonia inc.; keep attribution |

## Related packages

- [`typescript-sdk`](https://github.com/tonia-router/typescript-sdk) → `@tonia/sdk`
- [`python-sdk`](https://github.com/tonia-router/python-sdk) → `tonia`
- [`rust-sdk`](https://github.com/tonia-router/rust-sdk) → `tonia-sdk`

## Authentication

Runtime routes accept either:

- `Authorization: Bearer tonia_*`, or
- `x-api-key: tonia_*`

If both are sent, Bearer wins. Public catalogue, public models, and
`/v1/status` need no credentials.

## License

Copyright (c) 2026 tonia inc. Apache 2.0 — commercial use allowed. Keep the
copyright notice and `NOTICE` (attribution to tonia, https://tonia.ca)
if you copy or redistribute this reference.
