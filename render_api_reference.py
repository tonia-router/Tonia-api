"""Render a customer-facing Markdown API reference from public.openapi.yaml.

Usage:
  python render_api_reference.py
  # writes API.md next to this script
"""

from __future__ import annotations

import sys
from pathlib import Path

SPEC_PATH = Path(__file__).resolve().parent / "public.openapi.yaml"
OUT_PATH = Path(__file__).resolve().parent / "API.md"


def _load() -> dict:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("PyYAML required (pip install PyYAML)") from exc
    data = yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("expected OpenAPI mapping")
    return data


def render(spec: dict) -> str:
    info = spec.get("info") or {}
    lines: list[str] = [
        f"# {info.get('title', 'tonia Pass API')}",
        "",
        str(info.get("summary") or "").strip(),
        "",
        "Source: [`public.openapi.yaml`](public.openapi.yaml).",
        "",
        "## Servers",
        "",
    ]
    for server in spec.get("servers") or []:
        if isinstance(server, dict):
            lines.append(
                f"- `{server.get('url')}` — {server.get('description', '')}".rstrip()
            )
    lines += ["", "## Authentication", ""]
    schemes = ((spec.get("components") or {}).get("securitySchemes")) or {}
    if "BearerAuth" in schemes:
        lines.append("- `Authorization: Bearer tonia_*`")
    if "ApiKeyAuth" in schemes:
        lines.append("- `x-api-key: tonia_*`")
    lines.append("")
    lines.append("If both are sent, Bearer wins. Public catalogue, public models,")
    lines.append("and `/v1/status` need no credentials.")
    lines += ["", "## Endpoints", ""]

    paths = spec.get("paths") or {}
    for path in sorted(paths):
        ops = paths[path]
        if not isinstance(ops, dict):
            continue
        for method in ("get", "post", "put", "patch", "delete"):
            op = ops.get(method)
            if not isinstance(op, dict):
                continue
            summary = op.get("summary") or op.get("operationId") or ""
            tags = ", ".join(op.get("tags") or []) or "—"
            lines.append(f"### `{method.upper()} {path}`")
            lines.append("")
            lines.append(f"{summary}")
            lines.append("")
            lines.append(f"- Tag: `{tags}`")
            if op.get("security"):
                lines.append("- Auth: required")
            else:
                lines.append("- Auth: none")
            desc = (op.get("description") or "").strip()
            if desc:
                # Keep short — first paragraph only.
                first = desc.split("\n\n", 1)[0].replace("\n", " ")
                lines.append(f"- {first}")
            lines.append("")

    lines += [
        "## Errors",
        "",
        "Most runtime errors use "
        '`{"error": {"type", "code", "retryable"}}`. '
        "Official SDKs do not auto-retry — follow `retryable` and "
        "`Retry-After`.",
        "",
        "Admission 429 is `type: rate_limit_error`, "
        "`code: admission_rate_limited`, with `reason` "
        "(`rpm_per_key` | `concurrency_per_key` | "
        "`concurrency_per_tenant` | `concurrency_global`) and "
        "`scope` (`key` | `tenant` | `global`). Pass refuses "
        "immediately; the call is not queued. Per-key RPM defaults "
        "to 600. In-flight concurrency is a separate limit; a "
        "streaming call holds a slot until the stream ends.",
        "",
        "Monthly quota 429 is `type: entitlement_error`, "
        "`code: request_quota_exhausted` (`retryable: true`). "
        "Budget exhaustion is 402 `entitlement_error` and is not "
        "retryable. `api_error` / `audit_tip_contention` is 503 "
        "with `Retry-After: 1`. "
        "`managed_credential_unavailable` is 503 with "
        "`Retry-After: 60`.",
        "",
        "On chat-like routes, HTTP 200 may still carry "
        "`_tonia_policy_block` or `_tonia_entitlement_block` — "
        "treat those as errors.",
        "",
        "Content redaction is configured in the "
        "[tonia portal](https://portal.tonia.ca).",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    text = render(_load())
    OUT_PATH.write_text(text, encoding="utf-8")
    print(f"OK wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
