# tonia Pass API

OpenAPI contract for the official tonia Pass SDKs.

Source: [`public.openapi.yaml`](public.openapi.yaml).

## Servers

- `https://pass.tonia.ca` — Production Pass
- `http://127.0.0.1:8444` — Local development

## Authentication

- `Authorization: Bearer tonia_*`
- `x-api-key: tonia_*`

If both are sent, Bearer wins. Public catalogue, public models,
and `/v1/status` need no credentials.

## Endpoints

### `POST /v1/chat/completions`

OpenAI-shaped chat completions

- Tag: `runtime`
- Auth: required
- Upstream-shaped body. Prefer `Authorization: Bearer`. May return HTTP 200 with `_tonia_policy_block` or `_tonia_entitlement_block` carriers — HTTP 200 may still include `_tonia_policy_block` or `_tonia_entitlement_block` — treat those as errors. Soft-limit headers `x-tonia-limit-*` may appear on success. Top-level `reasoning_effort` is accepted when present; Pass clamps it to the model's declared set.

### `GET /v1/conversations`

List conversations

- Tag: `member_runtime`
- Auth: required
- Requires member-bound `app_session` key and `chat_history` entitlement.

### `POST /v1/conversations`

Create conversation

- Tag: `member_runtime`
- Auth: required

### `DELETE /v1/conversations`

Bulk-delete all conversations for the member

- Tag: `member_runtime`
- Auth: required

### `GET /v1/conversations/export`

Loi 25 conversation export

- Tag: `member_runtime`
- Auth: required

### `GET /v1/conversations/{conversation_id}`

Get conversation with messages

- Tag: `member_runtime`
- Auth: required

### `PATCH /v1/conversations/{conversation_id}`

Archive / unarchive conversation

- Tag: `member_runtime`
- Auth: required

### `DELETE /v1/conversations/{conversation_id}`

Delete one conversation

- Tag: `member_runtime`
- Auth: required

### `POST /v1/conversations/{conversation_id}/messages`

Append messages to a conversation

- Tag: `member_runtime`
- Auth: required
- DLP/media denials always return hard HTTP 451 (no chat_200).

### `POST /v1/embeddings`

OpenAI-shaped embeddings

- Tag: `runtime`
- Auth: required

### `POST /v1/images/edits`

OpenAI-shaped image edits

- Tag: `runtime`
- Auth: required
- Pass may rebuild JSON→multipart before upstream. Policy/entitlement denials are always hard HTTP on this surface.

### `POST /v1/images/generations`

OpenAI-shaped image generations

- Tag: `runtime`
- Auth: required
- Policy/entitlement denials on this surface are always hard HTTP (no chat_200).

### `POST /v1/interactions`

Gemini-shaped interactions

- Tag: `runtime`
- Auth: required

### `POST /v1/messages`

Anthropic-shaped messages

- Tag: `runtime`
- Auth: required
- Prefer `x-api-key`. Same chat_200 carrier / soft-limit rules as chat.

### `GET /v1/models`

Runtime model discovery for the calling key

- Tag: `runtime`
- Auth: required
- Authenticated list scoped to what the key/tenant may call. Header shape affects list presentation (`x-api-key` only → Anthropic- shaped ids; Bearer → OpenAI-shaped). Optional `reasoning` descriptor when the model declares efforts.

### `GET /v1/models/{id}`

Runtime model retrieve

- Tag: `runtime`
- Auth: required

### `GET /v1/public/catalogue`

Commercial tier / offer catalogue

- Tag: `public`
- Auth: none
- Unauthenticated commercial catalogue (Stripe products, public active offers, entitlement templates). Not a model SKU list — use `/v1/public/models` for Managed SKUs.

### `GET /v1/public/model-categories`

Category labels for the public model catalogue

- Tag: `public`
- Auth: none

### `GET /v1/public/models`

Public Managed model SKU list

- Tag: `public`
- Auth: none

### `GET /v1/public/models/{id}`

Public Managed model SKU detail

- Tag: `public`
- Auth: none

### `POST /v1/rerank`

Cohere-shaped rerank

- Tag: `runtime`
- Auth: required

### `POST /v1/responses`

OpenAI Responses API

- Tag: `runtime`
- Auth: required
- WebSocket upgrade on this path is refused with JSON HTTP 426 (`websocket_upgrade_unsupported`). Use HTTPS POST with `stream: true` for SSE.

### `GET /v1/status`

Public service health aggregation

- Tag: `public`
- Auth: none

## Errors

Most runtime errors use `{"error": {"type", "code", "retryable"}}`. On chat-like routes, HTTP 200 may still carry `_tonia_policy_block` or `_tonia_entitlement_block` — treat those as errors.

Content redaction is configured in the [tonia portal](https://portal.tonia.ca).
