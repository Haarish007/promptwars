# Anchor — GenAI Recovery & Prevention Platform

> **Tagline:** *Your recovery, steadied — a proactive AI companion that acts before the moment gets hard.*
>
> **Challenge:** Google PromptWars · **Route:** `/promptwars` · **Port:** `8100`

This repository is the **engineering specification** for Anchor. It is documentation, not application code. It is written to be executed by Cursor: every document is concrete enough for an AI coding agent to build from without inventing product decisions.

---

## Why Anchor wins (the one-paragraph pitch)

Most teams build a *reactive motivational chatbot*. Anchor is an **explainable, safety-first recovery decision-support system**. It does three things no generic chatbot does: (1) it computes a live, **explainable relapse-risk score ("Steady Score")** from daily signals and nudges *before* a crisis; (2) it collapses to a **zero-typing, voice-first "I'm Struggling" flow** for the exact moments when cognitive load is highest; and (3) it treats recovery as a **dyad** — the person *and* a consented caregiver — with an AI "Caregiver Copilot" that coaches the supporter on what to say and what to avoid. Every AI response is grounded in a **curated clinical knowledge base** (RAG) and gated by a **deterministic safety layer** that never lets the model improvise during a crisis.

That combination — proactive, explainable, dyadic, evidence-grounded, and safety-gated — is what turns "impressive demo" into "responsible product a judge trusts."

---

## The 7 signature capabilities (map these to the judging rubric)

| # | Capability | What judges see | Rubric hit |
|---|-----------|-----------------|-----------|
| 1 | **Steady Score** | A live, *explainable* risk meter ("elevated because: poor sleep + evening + skipped meeting → HALT flag") | Innovation, Use of AI |
| 2 | **One-Tap "I'm Struggling"** | Zero-typing, voice-guided intervention. No search, no menus. | UX, Impact |
| 3 | **Urge-Surfing companion** | Timed, evidence-based craving ride-out (CBT/DBT technique) | Domain depth |
| 4 | **Caregiver Copilot** | AI coaches the supporter: "say this / avoid this," coordinated alerts | Innovation, Impact |
| 5 | **Recovery Memory (RAG)** | Remembers triggers, milestones, what worked — personalizes everything | Use of AI |
| 6 | **Guardian escalation ladder** | Deterministic tiered escalation; crisis → real human resources | Responsible AI |
| 7 | **Trusted Knowledge Base** | Answers grounded only in cited, clinically-reviewed sources | Trust, Accuracy |

---

## Document map (covers all 20 required deliverables)

| Required deliverable | Lives in |
|---|---|
| 1. Executive Summary | `docs/01-executive-summary-and-vision.md` |
| 5. Vision Statement | `docs/01-executive-summary-and-vision.md` |
| 2. PRD | `docs/02-prd.md` |
| 3. User Personas | `docs/02-prd.md` |
| 4. User Journey | `docs/02-prd.md` |
| Competitive Analysis | `docs/02-prd.md` |
| 6. Success Metrics (KPIs) | `docs/02-prd.md` |
| 5. Functional Requirements | `docs/03-functional-and-nonfunctional-requirements.md` |
| 6. Non-Functional Requirements | `docs/03-functional-and-nonfunctional-requirements.md` |
| 7. AI Architecture | `docs/04-ai-architecture.md` |
| 8. Backend Architecture | `docs/05-backend-and-frontend-architecture.md` |
| 9. Frontend Architecture | `docs/05-backend-and-frontend-architecture.md` |
| 10. Database Design | `docs/06-database-design.md` |
| 11. API Specification | `docs/07-api-specification.md` |
| 12. Security | `docs/08-safety-security-accessibility.md` |
| 13. Accessibility | `docs/08-safety-security-accessibility.md` |
| Responsible AI / Safety | `docs/08-safety-security-accessibility.md` |
| 14. Performance | `docs/09-performance-logging-deployment.md` |
| 15. Logging | `docs/09-performance-logging-deployment.md` |
| 16. Deployment | `docs/09-performance-logging-deployment.md` |
| 17. Testing (200+ cases) | `docs/10-testing.md` |
| 18. Demo Flow | `docs/11-demo-flow-and-judge-checklist.md` |
| 19. Judge Checklist | `docs/11-demo-flow-and-judge-checklist.md` |
| 20. Cursor Execution Plan | `CURSOR_EXECUTION_PLAN.md` |
| Env template | `.env.example` |

---

## Existing infrastructure (constraints Cursor must respect)

- **Frontend:** React + Vite + Tailwind → AWS S3 + CloudFront
- **Backend:** FastAPI on Ubuntu, served behind Nginx at route `/promptwars`, port `8100`, managed by `systemd`
- **Database:** existing AWS RDS (PostgreSQL) — **relational schema only**, no Firebase/Firestore
- **Standards:** SOLID, DRY, Clean Architecture, repository + service layers, strong typing (TS + Pydantic), JWT + refresh tokens, hashed passwords, parameterized queries, audit logs, `.env.example` placeholders only

---

## ⚠️ Non-negotiable: this is a support tool, not a medical device

Anchor **assists** recovery; it does not diagnose, treat, or replace clinicians. Every layer of this spec assumes:
- Clear "not medical advice" disclaimers at onboarding and in-context.
- Crisis and self-harm signals are handled by a **deterministic safety layer** that routes to **real human resources** (e.g., 988 Suicide & Crisis Lifeline and SAMHSA 1-800-662-HELP in the US; KIRAN 1800-599-0019, iCall, Vandrevala Foundation in India), configurable by region — **never** by improvised LLM output.
- Highly sensitive health data → strong encryption, consent, data minimization, and full audit trails (see `docs/08`).

Read `docs/08-safety-security-accessibility.md` **first** if you read nothing else — it's both the ethical backbone and a scoring differentiator.

---

## How to build with Cursor

Open `CURSOR_EXECUTION_PLAN.md` and run the phases in order. Each phase has a copy-paste prompt and a "definition of done" checklist. Do **not** skip Phase 0 (safety scaffolding) — it must exist before any AI feature is wired up.
