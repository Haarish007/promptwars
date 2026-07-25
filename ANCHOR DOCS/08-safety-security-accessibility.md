# 08 · Responsible AI, Safety, Security & Accessibility

**Read this first.** With a vulnerable population, safety design *is* the product. It is also the single clearest signal to judges that you understand the domain. This document is both an ethical requirement and a scoring differentiator.

---

## Part 1 — Responsible AI & Safety

### 1.1 Core commitments
1. Anchor is a **support tool, not a medical device.** It does not diagnose, treat, or replace clinicians, sponsors, or crisis services. This is stated at onboarding and reachable in-app at all times.
2. **Crisis handling is deterministic**, never left to LLM improvisation.
3. **All health/recovery claims are grounded** in cited, reviewed sources or not made at all.
4. **Consent gates every share.** Nothing leaves the member's account without explicit, revocable consent.
5. **Non-judgmental by design.** Person-first language; relapse is a data point, not a failure.

### 1.2 The safety layer (deterministic, out-of-model)
Two independent gates the LLM cannot bypass:

**Pre-generation classifier** (see `docs/04 §2.1`)
- Labels inbound text: `none | distress | crisis | self_harm | harm_to_others | medical_emergency`.
- Deterministic pattern pre-filter can only *raise* severity, never lower it.
- Fail-safe: on error/timeout → treat as `distress` (cautious), never `none`.

**Crisis short-circuit**
- For `crisis | self_harm | harm_to_others | medical_emergency`, the system returns a **fixed, human-reviewed template** with region-appropriate human resources and one-tap contact actions. No generative call is made for the crisis response itself.

**Post-generation guard**
- Blocks disallowed output even from a jailbroken model: no dosing/method instructions, no content discouraging professional help, no method-of-self-harm content. On a block → replace with safe template.
- Verifies citations exist for health claims; if missing → strip claim / defer to human.

### 1.3 Escalation ladder (tiered, one-tap)
```
Tier 0  Self-help / psychoeducation (KB, grounded answer)
Tier 1  Coping tool (urge-surf, grounding, HALT check)
Tier 2  Peer / sponsor (one-tap call)
Tier 3  Guardian (consented alert + Copilot)
Tier 4  Crisis line (region resource, one-tap)
Tier 5  Emergency services (clear guidance to contact local emergency number)
```
- The system recommends the appropriate tier from classification + Steady band; the user always retains agency (one-tap, not forced), **except** that crisis resources are always surfaced for crisis-labelled input.

### 1.4 Crisis resources (region-configurable)
Resolved at runtime from the member's `region`. Ship with defaults and make it a config table, not hardcoded copy.
- **US:** 988 Suicide & Crisis Lifeline (call/text 988); SAMHSA National Helpline 1-800-662-HELP (4357).
- **India:** KIRAN Mental Health Helpline 1800-599-0019; iCall; Vandrevala Foundation; AASRA.
- **Generic fallback:** "contact your local emergency number and a trusted person now."
- Always present alongside, never instead of, one-tap contact to the user's own emergency contacts/sponsor.

### 1.5 What the AI must never do (hard rules in the system prompt + guards)
- Never give dosing, tapering, or "how much is safe" specifics beyond what a cited source states — and defer clinical specifics to a clinician.
- Never provide methods or instructions related to self-harm or overdose.
- Never discourage or delay professional/crisis help.
- Never claim to be a doctor/therapist or to provide diagnosis.
- Never shame, moralize, or use stigmatizing language.
- Never fabricate history, milestones, or sources.

### 1.6 Prompt-injection & jailbreak defense
- Retrieved KB/memory and user content are treated as **data, not instructions**; the model is told never to follow instructions embedded in them.
- Because the safety gates and post-guard sit *outside* the model, a successful jailbreak still cannot emit crisis content or disable escalation.
- All model-proposed tool arguments (phone numbers, contact IDs, share targets) are validated server-side before execution.

### 1.7 Evaluation (show judges you tested safety)
- **Red-team crisis set:** direct, indirect, obfuscated, and multilingual crisis phrasings → target **zero missed crises**; tuned to over-escalate.
- **Jailbreak set:** attempts to extract dosing/methods or disable escalation → all blocked by out-of-model guards.
- **Grounding eval:** sampled Q&A checked for citation presence + source correctness.
- Track false-negative crisis rate and ungrounded-claim rate as **guardrail metrics** (any nonzero = P0).

### 1.8 Human-in-the-loop & honesty
- The companion is transparent that it is an AI and not a substitute for people.
- It proactively points to human support and encourages real-world connection rather than fostering dependence on the app.

---

## Part 2 — Security & Privacy

### 2.1 AuthN / AuthZ
- Passwords hashed with Argon2id (or bcrypt) + per-user salt; never stored/logged in plaintext.
- JWT access ≤ 15 min; rotating refresh tokens stored **hashed**; refresh rotation revokes the prior token; logout revokes.
- Role + ownership checks in the service layer on every member-scoped resource; caregiver access only via an active link + matching consent scope.

### 2.2 Data protection
- TLS 1.2+ in transit; HSTS at CloudFront.
- RDS encryption at rest **plus** app-level field encryption for sensitive free-text (notes, transcripts, phone numbers).
- Data minimization: `safety_events` store classification + action, not raw crisis text beyond operational need.
- Configurable retention; user-initiated **export** and **delete** (data-subject rights).

### 2.3 Application security
- **SQL injection:** ORM/parameterized queries only; no string-built SQL (`NFR-SEC-4`).
- **XSS:** output encoding + strict CSP; sanitize any rendered user/AI content.
- **CSRF:** protect cookie-based flows; prefer bearer tokens for API.
- **Rate limiting & brute-force protection** on `/auth/*`, `/companion/*`, `/sos/*`.
- **Secrets:** env-only; `.env.example` placeholders; nothing secret committed or logged.
- **Least privilege:** scoped DB user + tight AWS IAM roles for S3/CloudFront/RDS.
- **Dependency hygiene:** pinned versions; audit for known CVEs.

### 2.4 Audit & access control
- `safety_events` and `audit_logs` are append-only, access-restricted, and contain **no PHI in metadata**.
- Correlation IDs tie a request across logs/audit without exposing content.

### 2.5 Privacy posture (say this to judges)
- "This is not surveillance." The member controls all sharing; caregivers see only what's explicitly shared, minimized and member-approved. Consent is revocable and immediate.

---

## Part 3 — Accessibility (WCAG 2.1 AA)

### 3.1 Why it matters here
Accessibility is not optional for a crisis product used under high cognitive load. It's also a visible quality signal for judges.

### 3.2 Requirements
- **Contrast:** AA (4.5:1 text) via design tokens; a high-contrast mode.
- **Keyboard:** full keyboard operability; visible focus; logical focus order; no keyboard traps.
- **Screen readers:** semantic landmarks, ARIA labels, live regions for streamed AI text and timers.
- **Targets:** ≥ 44px tap targets, especially SOS and crisis actions.
- **Voice-first:** all crisis/urge flows fully operable by voice (STT/TTS); tap fallback everywhere.
- **Reduced text under load:** SOS/crisis UI uses minimal words, large type, one action per view.
- **Motion:** honor `prefers-reduced-motion`; the urge-surf "wave" has a static alternative.
- **Language:** plain, non-clinical, non-triggering copy; avoid method-descriptive language even in examples/placeholders.

### 3.3 Accessibility test hooks
- Automated a11y checks in CI (axe) + manual screen-reader pass on auth, check-in, companion, and SOS.
