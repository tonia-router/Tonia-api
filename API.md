# tonia Pass API

OpenAPI contract for the official tonia Pass SDKs.

Source: [`public.openapi.yaml`](public.openapi.yaml).

## Servers

- `https://pass.tonia.ca:8443` — Production Pass
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

### `POST /v1/embeddings`

OpenAI-shaped embeddings

- Tag: `runtime`
- Auth: required

### `POST /v1/images/edits`

OpenAI-shaped image edits

- Tag: `runtime`
- Auth: required
- openai / xAI / StepFun only. Pass may rebuild JSON→multipart before upstream. Gemini image SKUs return HTTP 400 `provider_requires_surface` (`required_surface: interactions`) — use `POST /v1/interactions` with multimodal `input` parts. Policy/entitlement denials are always hard HTTP.

### `POST /v1/images/generations`

OpenAI-shaped image generations

- Tag: `runtime`
- Auth: required
- openai / xAI / StepFun only. Gemini image SKUs return HTTP 400 `provider_requires_surface` (`required_surface: interactions`) — use `POST /v1/interactions`. Policy/entitlement denials are always hard HTTP (no chat_200).

### `POST /v1/interactions`

Gemini-shaped interactions

- Tag: `runtime`
- Auth: required
- Gemini text and image SKUs. Image generate: `{model, input: "<prompt>", stream: false}`. Image edit: `input` is `[{type: text, text}, {type: image, mime_type, data}]` (`data` is raw base64, not a data URL). Response is native `interaction.steps`; output images are `model_output` parts with `type: image` or `mime_type` starting with `image/`. Do not call `/v1/images/*` or `/v1/chat/completions` for Gemini image SKUs.

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

Most runtime errors use `{"error": {"type", "code", "retryable"}}`. Official SDKs do not auto-retry — honor `retryable` and `Retry-After`.

Admission 429 is `type: rate_limit_error`, `code: admission_rate_limited`, with `reason` (`rpm_per_key` | `concurrency_per_key` | `concurrency_per_tenant` | `concurrency_global`) and `scope` (`key` | `tenant` | `global`). Pass refuses immediately; the call is not queued. Per-key RPM defaults to 600. In-flight concurrency is a separate limit; a streaming call holds a slot until the stream ends.

Monthly quota 429 is `type: entitlement_error`, `code: request_quota_exhausted` (`retryable: true`). Budget exhaustion is 402 `entitlement_error` and is not retryable. `api_error` / `audit_tip_contention` is 503 with `Retry-After: 1`. `managed_credential_unavailable` is 503 with `Retry-After: 60`.

On chat-like routes, HTTP 200 may still carry `_tonia_policy_block` or `_tonia_entitlement_block` — treat those as errors.

Content redaction is configured in the [tonia portal](https://portal.tonia.ca).
