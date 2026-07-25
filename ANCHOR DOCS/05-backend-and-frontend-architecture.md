# 05 · Backend & Frontend Architecture

Applies SOLID, DRY, Clean Architecture, repository pattern, and a service layer throughout. No business logic in routers or React components.

## Part A — Backend (FastAPI on Ubuntu, Nginx `/promptwars`, port `8100`, systemd)

### A.1 Layered structure (Clean Architecture)

```
app/
  main.py                     # FastAPI app factory, router registration, middleware
  core/
    config.py                 # env-driven settings (Pydantic BaseSettings)
    security.py               # hashing, JWT create/verify, dependencies
    logging.py                # structured JSON logging + correlation IDs
    rate_limit.py
    exceptions.py             # domain errors → HTTP mapping
  api/                        # ROUTERS ONLY — thin, no business logic
    v1/
      auth.py  onboarding.py  checkin.py  risk.py  companion.py
      safety.py  sos.py  urge.py  caregiver.py  kb.py  tracking.py
      notifications.py  health.py
  services/                   # BUSINESS LOGIC (service layer)
    auth_service.py  risk_service.py  companion_service.py
    safety_service.py  caregiver_service.py  kb_service.py
    checkin_service.py  notification_service.py  memory_service.py
  repositories/               # DATA ACCESS (repository pattern, one per aggregate)
    user_repo.py  checkin_repo.py  risk_repo.py  memory_repo.py
    caregiver_repo.py  kb_repo.py  audit_repo.py  consent_repo.py
  ai/                         # AI orchestration (see docs/04)
    provider/                 # LLMProvider interface + Gemini adapter
    pipeline.py               # the 6-stage orchestration
    classifier.py             # safety classifier + deterministic pre-filter
    rag.py                    # KB + memory retrieval
    guards.py                 # pre/post guards, output validation
    prompts/ (loader)         # loads versioned prompt files
  models/                     # SQLAlchemy ORM models
  schemas/                    # Pydantic request/response DTOs (strong typing)
  db/
    session.py  base.py  migrations/ (Alembic)
prompts/                      # versioned prompt & crisis-template files (docs/04 §3)
tests/
```

### A.2 Dependency rule
Direction of dependencies points inward: `api → services → repositories → models/db`. Services depend on repository **interfaces**, enabling test doubles (Dependency Inversion). AI pipeline is a service the companion service composes.

### A.3 Cross-cutting middleware
- **AuthN/AuthZ:** JWT dependency resolves current user; ownership/role checks in services.
- **Correlation ID:** attach per request; propagate into logs and audit events.
- **Rate limiting:** stricter on `/auth/*`, `/companion/*`, `/safety/*`.
- **Error handling:** domain exceptions → sanitized HTTP responses; never leak stack traces or provider errors to clients.
- **Request validation:** Pydantic schemas at every boundary.

### A.4 Safety subsystem placement
`safety_service` is a first-class service invoked by `companion_service` and `sos_service` **before** any generation and **after** it (post-guard). It writes to `audit_repo` on every safety event. It has no dependency on the LLM provider for *routing* decisions.

### A.5 Async & performance
- Async FastAPI endpoints; async DB driver (asyncpg via SQLAlchemy async).
- AI streaming via server-sent events / chunked responses for first-token latency.
- Pre-warm the SOS first step so it renders without waiting on the model.

### A.6 Config & secrets
- `core/config.py` reads all secrets/URLs from env. `.env.example` holds placeholders only. No secret is ever committed or logged.

## Part B — Frontend (React + Vite + Tailwind → S3 + CloudFront)

### B.1 Structure (feature-first, reusable components)

```
src/
  main.tsx  App.tsx  router.tsx
  app/                      # providers: auth, query client, theme, a11y
  components/ui/            # reusable primitives (Button, Card, VoiceButton, Sheet...)
  components/               # shared composite components
  features/
    auth/  onboarding/  checkin/  companion/  sos/  urge/
    steady-score/  caregiver/  knowledge-base/  tracking/  notifications/
      (each: components/, hooks/, api.ts, types.ts, index.ts)
  lib/
    api-client.ts           # typed fetch wrapper, token refresh interceptor
    voice.ts                # STT/TTS abstraction (Web Speech API)
    types.ts                # shared TS types (mirror backend schemas)
  styles/
```

### B.2 State & data
- Server state via a query library (e.g., TanStack Query): caching, retries, optimistic updates for check-ins.
- Auth token handling: access token in memory, refresh via httpOnly cookie or secure storage; silent refresh on 401.
- Strong typing: TS strict mode; API types mirror Pydantic schemas (generate or hand-maintain a shared `types.ts`).

### B.3 The SOS surface (design-critical)
- A persistent, high-contrast "I'm Struggling" affordance in a global layout slot — reachable in ≤ 1 tap from any route.
- SOS view: minimal text, huge targets, voice-first, one-tap actions (breathe, call guardian, call sponsor, crisis line, share). No forms, no typing.
- Renders its first calming step instantly (client-side), then streams AI guidance.

### B.4 Voice-first
- `voice.ts` wraps STT/TTS; every crisis/urge flow is operable hands-mostly-free.
- Graceful fallback to tap when speech APIs are unavailable.

### B.5 Accessibility baked in
- Design tokens for AA contrast; focus-visible styles; semantic landmarks; ARIA labels; reduced-motion + high-contrast support (see `docs/08`).

### B.6 Build & deploy
- Vite build → static assets to S3; CloudFront in front (HTTPS, HSTS, caching, SPA fallback to `index.html`).
- API base URL points at the backend behind Nginx `/promptwars` (env-configured).

### B.7 Component reuse & DRY
- All buttons, cards, sheets, and the VoiceButton are shared primitives.
- Feature APIs go through the single typed `api-client`; no scattered fetch calls.
