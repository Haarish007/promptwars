# 09 · Performance, Logging & Deployment

## Part 1 — Performance

### Budgets (from `docs/03` NFR-PERF)
| Path | Budget |
|---|---|
| Non-AI API (P95) | < 300 ms |
| SOS tap → first step rendered | < 1.5 s (client-first, non-AI) |
| AI companion first token (P95) | < 2.5 s |
| AI grounded full answer (P95) | < 8 s |
| Safety classification overhead | < 400 ms (parallelized) |

### Techniques
- **Async everywhere:** async FastAPI + asyncpg; no blocking calls in the event loop.
- **Streaming:** stream companion tokens (SSE/chunked) for perceived latency; render skeletons.
- **SOS pre-warm:** first calming step is client-side/static — never blocks on the model.
- **Parallelize the pipeline:** run safety classification and context retrieval concurrently where the classification result doesn't preclude retrieval; short-circuit on crisis.
- **Caching:** cache KB retrieval + resource lookups; cache the member's current risk band per session.
- **DB:** hot indexes (see `docs/06`), connection pooling, pagination on all lists.
- **Frontend:** Vite code-splitting per feature; lazy-load non-critical routes; keep SOS in the initial bundle; CloudFront caching for static assets with SPA fallback.
- **Provider resilience:** timeouts + retries + circuit breaker; safe canned fallback on failure (never a raw error to the user).

## Part 2 — Logging & Observability

### Principles
- **Structured JSON logs** with a `correlation_id` per request, propagated through services.
- **No PII/PHI in application logs.** Log identifiers and event types, not note text or transcripts.
- **Dedicated safety audit stream:** every safety event (classification, action, tier, resource shown) written append-only to `safety_events` + `audit_logs`, access-controlled.

### What to log
| Stream | Contents |
|---|---|
| App logs | request/response metadata, latency, errors, correlation IDs (no content) |
| Safety audit | label, confidence, action_taken, tier, resource, timestamp (minimized) |
| AI telemetry | provider, model, tokens, latency, grounded(bool), citations_count — no raw content |
| Access audit | auth events, consent grants/revokes, caregiver link changes, exports/deletes |

### Metrics & alerts
- Latency (P50/P95), error rate, AI provider failure rate.
- Safety-event counts, **false-negative crisis rate** (from eval), grounding rate.
- Alerts: any ungrounded health claim in prod, any crisis-label without a resource shown, provider circuit-breaker open.

### Health checks
- `/health` liveness; `/health/ready` verifies DB + AI provider reachability (readiness gate for deploys).

## Part 3 — Deployment

### Topology
```
Browser ─HTTPS─▶ CloudFront ─▶ S3 (React static build)
Browser ─HTTPS─▶ CloudFront/ALB ─▶ Nginx (Ubuntu) ── /promptwars ──▶ FastAPI (uvicorn/gunicorn) :8100
                                                              │
                                                              ▼
                                                        AWS RDS (PostgreSQL)
                                                              │
                                                              ▼
                                                    LLM provider (Gemini) via HTTPS
```

### Frontend (S3 + CloudFront)
1. `vite build` → static assets.
2. Upload `dist/` to the S3 bucket (private; served via CloudFront OAC).
3. CloudFront: HTTPS + HSTS, SPA fallback (`index.html` for 403/404), cache static assets, short TTL for `index.html`.
4. Env: `VITE_API_BASE=https://<host>/promptwars/api/v1`.

### Backend (FastAPI + Nginx + systemd on Ubuntu)
1. Deploy code to the Ubuntu host; create a virtualenv; install pinned deps.
2. Run migrations: `alembic upgrade head`.
3. Serve with Gunicorn + Uvicorn workers bound to `127.0.0.1:8100`.
4. **systemd unit** `anchor.service` manages the process (auto-restart, env file, non-root user).
5. **Nginx** reverse-proxies `/promptwars` → `127.0.0.1:8100`, sets forwarded headers, enables gzip, request-size limits, and rate limits on `/auth`, `/companion`, `/sos`.
6. TLS termination (Nginx or upstream ALB/CloudFront), HSTS.

**Example systemd unit (`/etc/systemd/system/anchor.service`)**
```ini
[Unit]
Description=Anchor FastAPI (PromptWars)
After=network.target

[Service]
User=anchor
WorkingDirectory=/opt/anchor
EnvironmentFile=/opt/anchor/.env
ExecStart=/opt/anchor/.venv/bin/gunicorn app.main:app \
  -k uvicorn.workers.UvicornWorker -w 4 -b 127.0.0.1:8100 --timeout 60
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Example Nginx location**
```nginx
location /promptwars/ {
    proxy_pass http://127.0.0.1:8100/;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_http_version 1.1;
    proxy_buffering off;            # allow SSE streaming for AI
    client_max_body_size 5m;
}
```

### Config & secrets
- All secrets via `EnvironmentFile`; only `.env.example` (placeholders) is committed.
- Separate DB user with least privilege; scoped IAM roles for S3/CloudFront.

### Rollout & ops
- Migrations gated by `/health/ready`.
- Zero-downtime restart via systemd; keep the prior release for quick rollback.
- Post-deploy smoke test: auth → check-in → companion (grounded) → SOS first-step → safety classify → caregiver share.
