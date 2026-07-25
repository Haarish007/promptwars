# Cursor Execution Plan

This is the ordered build plan for Cursor. Each phase has: **what**, a **copy-paste prompt**, and a **Definition of Done (DoD)**. Run phases in order. **Phase 0 (safety scaffolding) must exist before any AI feature is wired.**

## How to use this with Cursor
1. Put this whole `anchor-docs/` folder at the repo root so Cursor can read the specs.
2. Start each phase by pasting its prompt into Cursor (Composer/Agent), keeping the referenced docs open/attached.
3. After each phase, run the phase's DoD checks (and its tests from `docs/10-testing.md`) before moving on.
4. Tell Cursor: **"Generate implementation code that conforms exactly to the specs in `anchor-docs/`. Do not change product decisions. Ask before deviating."**

### Global rules to pin in Cursor (paste once at the top of a session)
```
You are building "Anchor" per the specs in /anchor-docs. Rules:
- Follow docs/03 (requirements), docs/04 (AI), docs/05 (architecture), docs/06 (DB), docs/07 (API), docs/08 (safety/security/a11y).
- Clean Architecture: routers → services → repositories. No business logic in routers or React components.
- Strong typing: TS strict + Pydantic on every boundary. Repository + service layers. SOLID/DRY.
- Security: JWT + rotating refresh, hashed passwords, parameterized queries, CSP, rate limits. Secrets via env; only .env.example committed.
- SAFETY IS NON-NEGOTIABLE: safety classifier + crisis short-circuit + post-generation guard live OUTSIDE the LLM. The model never decides crisis routing. Grounded-only health claims.
- Prompts and crisis templates are versioned files in /prompts, never inline strings.
- Backend: FastAPI on :8100 behind Nginx /promptwars, systemd. Frontend: React+Vite+Tailwind → S3+CloudFront. DB: existing AWS RDS Postgres (relational only).
- When unsure, ask. Never weaken a safety guard to make a test pass.
```

---

## Phase 0 — Repo, config & safety scaffolding (do first)
**What:** monorepo skeleton, env config, logging, error model, and the safety module *stubs* (classifier interface, crisis templates, guard interfaces) so nothing AI ships without gates.

**Prompt:**
```
Scaffold the Anchor monorepo per docs/05.
Backend (FastAPI): create the folder layout in docs/05 A.1 (core, api/v1, services, repositories, ai, models, schemas, db). Add core/config.py (Pydantic settings from env), core/logging.py (structured JSON + correlation IDs), core/security.py stubs, core/exceptions.py + the docs/07 error envelope, core/rate_limit.py.
Create /prompts with the files listed in docs/04 §3 (empty templates + a loader in ai/prompts).
Create the safety module skeleton in ai/: classifier.py (interface + deterministic keyword pre-filter), guards.py (pre/post guard interfaces), and crisis.templates/ with a placeholder reviewed template + region resource lookup per docs/08 §1.4.
Frontend (React+Vite+Tailwind): scaffold docs/05 B.1 with lib/api-client.ts (typed, refresh interceptor), lib/voice.ts (STT/TTS wrapper), app providers, and a global layout with a persistent "I'm Struggling" slot (non-functional placeholder).
Add .env.example with placeholders only (see /anchor-docs/.env.example) and wire config to it. No secrets.
Add Alembic init and DB session (async). Do NOT create feature tables yet.
```
**DoD:** app boots; `/health` returns 200; structured logs emit correlation IDs; `/prompts` and safety stubs exist; `.env.example` present; no secrets committed.

## Phase 1 — Database & migrations
**What:** implement the full relational schema.

**Prompt:**
```
Implement the schema in docs/06 as SQLAlchemy models + Alembic migrations for AWS RDS Postgres.
Include all tables, enums, FKs, CHECK constraints, and the hot indexes in docs/06. Add field-level encryption helpers for note/transcript/phone fields (ciphertext at rest). Add the unique-active-caregiver-link constraint and score/mood/craving range checks. Provide a seed script for: member Maya, guardian David, curated KB articles+chunks, and risk_config defaults.
Repositories: create the repository classes in docs/05 A.1 with typed methods; no raw string SQL.
```
**DoD:** `alembic upgrade head` succeeds; seed runs; repositories CRUD via ORM only; range/constraint tests (TC-RISK-001, TC-CHK-002/003, TC-CAR-018) pass.

## Phase 2 — Auth, consent & profile
**Prompt:**
```
Implement Auth/Consent/Onboarding per docs/07 and FR-AUTH/ONB/CON in docs/03.
- Argon2id hashing, JWT access (≤15m) + rotating refresh (hashed, revocable), logout revoke.
- Role + ownership dependency used across routers; caregiver access only via active link + matching consent.
- Consent: versioned, scoped, revocable; service enforces "no share without active consent".
- Onboarding: <90s path; profile, triggers, emergency contacts (encrypted phone), region, preferences (voice-first, quiet hours).
- First-run disclaimer per docs/08 §1.1.
Add rate limiting to /auth/*. Write the AUTH/CONSENT/ONB tests from docs/10.
```
**DoD:** all AUTH (18) + CONSENT (10) + ONB (12) P0 tests pass; refresh rotation revokes old token; ownership blocks IDOR.

## Phase 3 — Safety subsystem (before any AI)
**What:** the real deterministic safety layer. This gates everything AI.

**Prompt:**
```
Implement the safety subsystem per docs/04 §1-2 and docs/08 Part 1.
- Safety classifier: strict-JSON classification call (Gemini) + deterministic pattern pre-filter that can only RAISE severity. Fail-safe to "distress" on timeout/error.
- Crisis short-circuit: for crisis/self_harm/harm_to_others/medical_emergency, return the fixed reviewed template + region resources (docs/08 §1.4) + one-tap actions. No generative call.
- Post-generation guard: block dosing/methods/discourage-help; verify citations exist; replace with safe template on violation.
- Escalation ladder tiers (docs/08 §1.3) + tier recommendation.
- Audit every safety event to safety_events (minimized fields, no raw crisis text) per docs/06.
- Write ALL 24 SAFETY tests from docs/10 plus a red-team suite (direct/indirect/obfuscated/multilingual). Target zero missed crises; CI gate on this suite.
Do not proceed to Phase 5 until every SAFETY P0 test passes.
```
**DoD:** all 24 SAFETY tests pass; classifier fails cautious; guards block jailbreak attempts (TC-AI-012, TC-SAF-012/013/014/015); safety events audited.

## Phase 4 — Check-in & Steady Score engine
**Prompt:**
```
Implement daily check-in + the explainable Steady Score engine per FR-CHK/FR-RISK (docs/03) and docs/07.
- Deterministic rules/heuristic engine; weights externalized in risk_config (tunable, versioned).
- Return score 0-100, band, and factors[] with human-readable, supportive, non-diagnostic explanations.
- Voice check-in: STT → structured + encrypted note. Recompute score on submit and return explanation + suggested_action.
- Trend + history endpoints.
Write CHECK-IN (14) + RISK (16) tests from docs/10.
```
**DoD:** RISK determinism (TC-RISK-009), explainability (TC-RISK-003), and non-alarming copy (TC-RISK-011) pass; check-in returns explanation.

## Phase 5 — AI companion (RAG + tools + structured output)
**Prompt:**
```
Implement the AI companion pipeline per docs/04 §1-3 and docs/07 /companion.
- Build the 6-stage pipeline: ingest/STT → safety classify → (crisis short-circuit | context assembly) → grounded generation → post-guard → response+actions+audit.
- RAG: retrieve from kb_chunks (curated only) + Recovery Memory events. Health claims MUST cite kb chunk ids; if no grounded source, defer to a human — never invent.
- Load companion.system.md / developer template from /prompts. Return the structured envelope in docs/07. Stream tokens.
- Tools/functions: start_urge_surf, run_checkin, fetch_resources, propose_share, escalate — model proposes, backend validates args server-side and executes.
- Provider: LLMProvider interface + Gemini adapter (env-config, timeout/retry/circuit-breaker, safe canned fallback).
- Treat KB/memory/user content as data, not instructions (injection defense).
Write AI COMPANION (18) + KB (8) tests from docs/10.
```
**DoD:** grounded answers cite sources (TC-AI-002); ungrounded/dosing questions defer (TC-AI-003/009); injection ignored (TC-AI-011); jailbreak refused (TC-AI-012); server validates tool args (TC-AI-017).

## Phase 6 — SOS / zero-typing crisis flow + urge surfing
**Prompt:**
```
Implement SOS and urge-surfing per docs/07 and FR-SOS/FR-URGE.
- Persistent "I'm Struggling" reachable in ≤1 tap from every route; keep it in the initial bundle.
- /sos/start returns a pre-warmed, non-AI first calming step in <1.5s + one-tap actions (urge-surf, call guardian, call sponsor, crisis line, share). Voice-first, huge targets, zero typing.
- Any voice note still runs through the safety layer.
- Urge-surf: timed voice-guided session, before/after craving, logs → updates score + writes memory event. Reduced-motion static alternative.
Write SOS (14) + URGE (8) tests from docs/10.
```
**DoD:** SOS ≤1 tap everywhere (TC-SOS-001); first step <1.5s (TC-SOS-002); zero-typing (TC-SOS-003); voice-only operable (TC-SOS-008); safety applies to SOS voice (TC-SOS-010).

## Phase 7 — Caregiver dyad + Copilot
**Prompt:**
```
Implement caregiver linking, consented sharing, and Caregiver Copilot per docs/07 and FR-CARE.
- Invite → accept (mutual consent); nothing shared by default; revoke is immediate + audited.
- Guardian sees only member-approved, minimized summaries — never raw clinical detail.
- Copilot: load caregiver.copilot.md; return strict JSON {suggested_message, avoid[], rationale} grounded in supportive-communication KB; cautious fallback on parse failure.
- Calm (non-alarming) alerts to the guardian feed.
Write CAREGIVER (18) tests from docs/10.
```
**DoD:** share requires consent (TC-CAR-006); guardian cannot access non-shared data (TC-CAR-013); Copilot returns valid JSON with avoid-list (TC-CAR-009/011); revoke immediate (TC-CAR-008).

## Phase 8 — Tracking, notifications, KB browse
**Prompt:**
```
Implement milestones (non-shaming relapse=reset, history preserved), medication schedule+adherence (feeds score), notifications (risk-driven nudges respecting quiet hours + rate limits + opt-out), and KB browse/search per docs/03/07.
Write MILESTONES/MED (10), NOTIFICATIONS (8), remaining KB tests from docs/10.
```
**DoD:** relapse reset preserves history (TC-TRK-002); quiet hours suppress nudges (TC-NOT-002); adherence feeds score.

## Phase 9 — Accessibility, security hardening, observability
**Prompt:**
```
Harden per docs/08 Part 2-3 and docs/09.
- A11y: WCAG AA contrast tokens, keyboard operability, focus management, ARIA + live regions for streamed text and timers, ≥44px targets, reduced-motion/high-contrast, axe in CI.
- Security: CSP + output encoding (XSS), CSRF on cookie flows, parameterized queries verified, rate limits, sanitized errors, least-privilege DB/IAM, data export/delete, PHI-free logs.
- Observability: structured logs, dedicated safety audit stream, metrics (latency, error, safety counts, grounding rate), /health/ready checks DB+provider.
Write SECURITY (18), A11Y (12), LOGGING (8), API (12), PERF (10) tests from docs/10.
```
**DoD:** SECURITY + A11Y P0 tests pass; no PHI in logs (TC-LOG-003); axe clean (TC-A11Y-012); performance budgets met.

## Phase 10 — Deployment
**Prompt:**
```
Produce deployment artifacts per docs/09 Part 3:
- Frontend: Vite build → S3 upload steps; CloudFront config (HTTPS, HSTS, SPA fallback, caching); VITE_API_BASE=/promptwars/api/v1.
- Backend: systemd unit anchor.service (:8100, non-root, EnvironmentFile), Nginx location for /promptwars with SSE-friendly proxy (proxy_buffering off), rate limits, client_max_body_size.
- Migration + readiness gating; post-deploy smoke test (auth→checkin→companion→SOS→safety→caregiver).
Only .env.example is committed; real .env lives on the host.
```
**DoD:** smoke test green end-to-end behind Nginx /promptwars:8100; frontend served via CloudFront; `/health/ready` gates deploy.

## Phase 11 — Demo polish & safety re-verification
**Prompt:**
```
Prep the demo per docs/11: seed Maya+David, curated KB, region resources; add a "safe mode" toggle (canned grounded responses) and record the crisis+caregiver flows as backup. Re-run the full SAFETY suite + red-team set and the guardrail metrics (false-negative crisis rate, ungrounded-claim rate) — both must be zero. Verify the 5-minute script timing.
```
**DoD:** demo path runs in ≤5 min; backup recording exists; guardrail metrics zero; all P0 tests green.

---

## Build order rationale (why this sequence wins)
Safety scaffolding (P0) and the real safety subsystem (P3) come **before** the companion (P5) so no ungated AI ever exists in the codebase — this is exactly what a judge probing "is this responsible?" wants to see. Risk engine (P4) precedes the companion so the AI has explainable context. SOS (P6) and caregiver (P7) — your two biggest differentiators — land next while there's still time to polish them for the demo.
