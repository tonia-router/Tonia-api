# tonia-api

Public OpenAPI 3.1 contract for [tonia Pass](https://pass.tonia.ca).

This specification is the source of truth for the official SDKs and API
reference. It covers the developer API: public catalogue and models,
authenticated runtime calls, and member conversation history.

Organization settings, billing, and API-key management stay in the
[tonia portal](https://portal.tonia.ca).

## Files

| Path | Role |
| --- | --- |
| `public.openapi.yaml` | OpenAPI 3.1 specification |
| `API.md` | Markdown API reference (generated) |
| `check_public_openapi.py` | Spec integrity check |
| `check_public_secrets.py` | Public-tree credential scan |
| `render_api_reference.py` | Rebuild `API.md` from the OpenAPI spec |
| `generate.sh` / `Makefile` | Regenerate official SDK clients |

## Validate

```bash
python check_public_openapi.py
# or: make check
```

Requires [PyYAML](https://pyyaml.org/).

## Regenerate SDK clients

```bash
make generate-sdk
```

Requires Docker.

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
