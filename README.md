# tonia-api

Public OpenAPI 3.1 contract for [tonia Pass](https://pass.tonia.ca).

This specification is the source of truth for the official SDKs and API
reference. It covers the developer API only: unauthenticated catalogue /
models / status, plus authenticated runtime helpers (chat, messages,
embeddings, images, responses, rerank, interactions).

Workspace settings, billing, and API-key management stay in the
[tonia portal](https://portal.tonia.ca). Server-side chat history is
chat-app only — not part of this contract.

## Files

| Path | Role |
| --- | --- |
| `public.openapi.yaml` | OpenAPI 3.1 specification |
| `API.md` | Markdown API reference |
| `check_public_openapi.py` | Spec integrity check |
| `render_api_reference.py` | Rebuild `API.md` from the spec |
| `LICENSE` / `NOTICE` | Apache 2.0; copyright tonia; keep attribution |

## Validate

```bash
python check_public_openapi.py
```

Requires [PyYAML](https://pyyaml.org/).

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

Copyright 2026 tonia. Apache 2.0 — commercial use allowed. Keep the
copyright notice and `NOTICE` (attribution to tonia, https://tonia.ca)
if you copy or redistribute this specification.
