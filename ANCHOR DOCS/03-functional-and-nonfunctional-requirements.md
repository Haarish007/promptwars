# 03 · Functional & Non-Functional Requirements

Requirement IDs: `FR-<module>-<n>` and `NFR-<category>-<n>`. Each FR is testable and maps to a test case in `docs/10-testing.md`.

## Functional Requirements

### Auth & Consent (AUTH)
- **FR-AUTH-1** Users register with email + password; passwords hashed (Argon2id or bcrypt).
- **FR-AUTH-2** Login issues a short-lived JWT access token + long-lived refresh token (rotating).
- **FR-AUTH-3** Refresh endpoint rotates refresh tokens and revokes the prior token.
- **FR-AUTH-4** Logout revokes the active refresh token.
- **FR-AUTH-5** Onboarding captures explicit, versioned consent for data processing and for each sharing scope; consent is revocable.
- **FR-AUTH-6** Roles: `member`, `guardian`. Endpoints enforce role + ownership.
- **FR-AUTH-7** A "not medical advice / crisis resources" disclaimer is shown at first run and always reachable.

### Onboarding & Profile (ONB)
- **FR-ONB-1** Member sets recovery goal, substance focus (free-text/enum), recovery start date, and known triggers.
- **FR-ONB-2** Member configures emergency contacts and preferred crisis resources (region-aware defaults).
- **FR-ONB-3** Member selects communication preferences (voice-first toggle, nudge frequency, quiet hours).
- **FR-ONB-4** Onboarding is skippable/minimal-first: usable after < 90 seconds.

### Daily Check-in (CHK)
- **FR-CHK-1** Member submits a check-in: mood (1–5), sleep quality, craving level (0–10), HALT flags (Hungry/Angry/Lonely/Tired), free-text/voice note, optional trigger tags.
- **FR-CHK-2** Voice input is transcribed to text (STT) and stored with the structured fields.
- **FR-CHK-3** Check-in submission recomputes the Steady Score and returns it with an explanation.
- **FR-CHK-4** Check-ins are viewable as a trend (mood/craving over time).

### Steady Score / Risk Engine (RISK)
- **FR-RISK-1** Compute a 0–100 risk score from weighted signals: recent craving trend, sleep, HALT flags, missed check-ins, medication adherence, high-risk time-of-day, active triggers, days since last milestone/relapse.
- **FR-RISK-2** Return a **band** (Low/Guarded/Elevated/High) plus a human-readable **explanation** listing the top contributing factors.
- **FR-RISK-3** The engine is deterministic and rules/heuristic-based for the build; the weighting config is externalized (not hardcoded in logic) to allow tuning.
- **FR-RISK-4** Elevated/High bands trigger a proactive nudge subject to quiet hours.
- **FR-RISK-5** The score never *itself* diagnoses; explanation copy is supportive and non-alarming.

### AI Companion (AI)
- **FR-AI-1** Member chats with the companion via text or voice.
- **FR-AI-2** Every response is generated with (a) the member's relevant memory/context and (b) retrieved passages from the trusted knowledge base (RAG).
- **FR-AI-3** Health/clinical claims include a citation to the source passage; if no grounded source exists, the companion says so and recommends a human/clinician instead of inventing an answer.
- **FR-AI-4** All user input is passed through the **safety classifier before and the response after** generation (see SAFETY).
- **FR-AI-5** The companion can call tools/functions: start urge-surf, trigger check-in, fetch resources, propose caregiver share, escalate.
- **FR-AI-6** Responses use person-first, non-judgmental language; relapse is framed as a data point.

### Safety Layer & Escalation (SAFETY) — highest priority
- **FR-SAFETY-1** A dedicated safety classifier labels each inbound message: `none | distress | crisis | self_harm | harm_to_others | medical_emergency`.
- **FR-SAFETY-2** For `crisis | self_harm | harm_to_others | medical_emergency`, the system **short-circuits** normal AI generation and returns a fixed, reviewed crisis-response template with region-appropriate human resources and one-tap contact actions.
- **FR-SAFETY-3** Escalation ladder tiers: self-help → coping tool → peer/sponsor → guardian → crisis line → emergency services. The system recommends the appropriate tier and offers one-tap action.
- **FR-SAFETY-4** The LLM is **never** the sole decision-maker for crisis routing; classification + routing are deterministic and independently logged.
- **FR-SAFETY-5** Every safety event is audit-logged (see LOG) with timestamp, classification, action taken, and outcome — without storing more sensitive free-text than necessary.
- **FR-SAFETY-6** Post-generation guard: if a generated response contains disallowed content (dosing instructions, methods of self-harm, discouragement from seeking help), it is blocked and replaced with a safe template.
- **FR-SAFETY-7** The safety layer degrades safely: if the classifier is unavailable, the system defaults to the *cautious* path (offer resources) rather than free generation.

### One-Tap "I'm Struggling" / SOS (SOS)
- **FR-SOS-1** A persistent, high-contrast "I'm Struggling" control is reachable from every screen in ≤ 1 tap.
- **FR-SOS-2** Activating it launches a voice-first, low-text guided flow requiring zero typing.
- **FR-SOS-3** The flow offers, as one-tap actions: breathe/urge-surf, call guardian, call sponsor, call crisis line, share moment.
- **FR-SOS-4** The flow is fully operable by voice and by large tap targets; it works with the safety layer active.

### Urge Surfing (URGE)
- **FR-URGE-1** A timed, guided urge-surfing session (default ~4 min) with voice guidance and a visual "wave."
- **FR-URGE-2** At completion, prompt a quick craving re-rating and one-tap log.
- **FR-URGE-3** Session outcomes feed the Steady Score and memory ("urge-surfing worked for Maya at 9pm").

### Caregiver / Guardian (CARE)
- **FR-CARE-1** Member invites a Guardian by email; Guardian accepts; link requires mutual consent.
- **FR-CARE-2** Member controls, per event type, what may be shared (nothing shared by default).
- **FR-CARE-3** **Caregiver Copilot** generates situation-specific guidance ("suggested message" + "avoid") grounded in supportive-communication best practices.
- **FR-CARE-4** When the Member shares a moment, the Guardian receives a calm, consented alert + Copilot suggestion.
- **FR-CARE-5** Either party can revoke the link at any time; revocation is immediate and audited.
- **FR-CARE-6** Guardian never sees raw clinical detail unless the Member explicitly shares it.

### Knowledge Base (KB)
- **FR-KB-1** Curated, clinically-reviewed articles are browsable and searchable.
- **FR-KB-2** Each article has source attribution and a review date.
- **FR-KB-3** KB content is the retrieval corpus for RAG; only curated content is retrievable.

### Milestones & Medication (TRK)
- **FR-TRK-1** Track recovery milestones/streaks with **non-shaming** relapse handling (reset with encouragement, history preserved).
- **FR-TRK-2** Optional medication schedule + adherence logging; adherence feeds the Steady Score.

### Notifications (NOTIF)
- **FR-NOTIF-1** Scheduler sends proactive nudges based on risk band + preferences + quiet hours.
- **FR-NOTIF-2** Nudges are opt-out and rate-limited (no nagging).

## Non-Functional Requirements

### Performance (PERF)
- **NFR-PERF-1** P95 API latency (non-AI endpoints) < 300 ms.
- **NFR-PERF-2** "I'm Struggling" tap → first guided step rendered < 1.5 s (pre-warmed, non-AI first step).
- **NFR-PERF-3** AI companion first-token (streamed) < 2.5 s P95; full grounded answer < 8 s P95.
- **NFR-PERF-4** Safety classification adds < 400 ms overhead (runs in parallel where possible).

### Security & Privacy (SEC)
- **NFR-SEC-1** TLS 1.2+ everywhere; HSTS on CloudFront.
- **NFR-SEC-2** Sensitive fields encrypted at rest (RDS encryption + app-level field encryption for free-text notes).
- **NFR-SEC-3** JWT access ≤ 15 min; refresh rotation; tokens revocable.
- **NFR-SEC-4** All queries parameterized (ORM/param binding) — no string-built SQL.
- **NFR-SEC-5** Output encoding + CSP to prevent XSS.
- **NFR-SEC-6** Rate limiting + brute-force protection on auth and AI endpoints.
- **NFR-SEC-7** Principle of least privilege for DB and AWS IAM roles.
- **NFR-SEC-8** Data minimization + configurable retention; user data export & delete supported.

### Reliability (REL)
- **NFR-REL-1** Safety layer degrades to cautious defaults on dependency failure (never fails open to free generation).
- **NFR-REL-2** Idempotent write endpoints where retries are likely (check-in, share).
- **NFR-REL-3** Graceful AI provider fallback/timeout with a safe canned response.

### Accessibility (A11Y)
- **NFR-A11Y-1** WCAG 2.1 AA: contrast, focus order, labels, keyboard operability.
- **NFR-A11Y-2** Voice-first paths for all crisis features; screen-reader compatible.
- **NFR-A11Y-3** Large tap targets (≥ 44px) and reduced-text crisis UI.
- **NFR-A11Y-4** Respect reduced-motion and high-contrast preferences.

### Maintainability (MNT)
- **NFR-MNT-1** Clean Architecture: routers → services → repositories; no business logic in routers.
- **NFR-MNT-2** Strong typing: TypeScript strict mode; Pydantic models on all boundaries.
- **NFR-MNT-3** Config via environment; secrets never committed (`.env.example` placeholders only).
- **NFR-MNT-4** Prompt templates and safety templates are versioned, reviewable files — not inline strings.

### Observability (OBS)
- **NFR-OBS-1** Structured JSON logs with correlation IDs; safety events on a dedicated, tamper-evident audit stream.
- **NFR-OBS-2** Metrics for latency, error rate, safety-event counts, grounding rate.
- **NFR-OBS-3** No PII/PHI in application logs; audit logs access-controlled.
