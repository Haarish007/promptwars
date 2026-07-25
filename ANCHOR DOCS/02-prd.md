# 02 · Product Requirements Document (PRD)

## 1. Product overview

Anchor is a dyadic (patient + caregiver), multi-modal, AI-driven recovery and prevention platform. It combines proactive risk sensing, zero-typing crisis support, evidence-based micro-interventions, caregiver coaching, and a grounded clinical knowledge base — all wrapped in a deterministic safety layer.

**Primary users:** individuals in SUD recovery (the "Member").
**Secondary users:** consented caregivers/family/sponsors (the "Guardian").
**Tertiary (roadmap):** counselors/clinicians (read-only shared summaries, out of hackathon scope).

## 2. Goals & non-goals

**Goals**
- G1. Detect rising relapse risk from lightweight daily signals and nudge proactively.
- G2. Deliver support in <1 tap / <5 seconds during a high-cognitive-load moment.
- G3. Ground all guidance in cited, trusted clinical sources.
- G4. Coach caregivers to help effectively without increasing harm.
- G5. Route every crisis to real human help deterministically.

**Non-goals**
- N1. Diagnose or treat SUD or any mental health condition.
- N2. Replace clinicians, sponsors, or crisis services.
- N3. Provide medical/dosing advice beyond what a cited source states.
- N4. Store more personal data than each feature strictly requires.

## 3. Personas

### Persona A — Maya, 29 — the Member (primary)
- **Context:** 8 months into recovery from alcohol use disorder. Works a stressful job. Lives alone. Attends a weekly support group.
- **Triggers:** evenings, work stress, loneliness, passing her old bar on the commute.
- **Behavior under stress:** overwhelmed, can't focus, won't read long text, sometimes can't articulate what's wrong.
- **Needs:** something that notices when she's slipping, guides her through a craving without effort, and connects her to a person fast.
- **Quote:** *"When it's bad, I can't even find the app I need. I need it to just... be there."*
- **Success looks like:** she taps once, is talked through a 4-minute urge-surf, logs it, and the craving passes.

### Persona B — David, 58 — the Guardian (secondary)
- **Context:** Maya's father. Wants to help but is terrified of saying the wrong thing and pushing her away.
- **Pain:** doesn't know if a behavior is "normal," when to step in, or when it's an emergency.
- **Needs:** clear, situation-specific coaching; a heads-up when Maya *chooses* to share a hard moment; reassurance he's not alone.
- **Quote:** *"I lie awake wondering if I should call her or if that'll make it worse."*
- **Success looks like:** he gets a gentle, opt-in alert and an AI-suggested message he can send that actually helps.

### Persona C — Priya, 34 — the Newly-Discharged Member (edge/onboarding)
- **Context:** just out of a 30-day program, highest-risk window (first 90 days). Motivated but fragile, low trust in apps.
- **Needs:** frictionless onboarding, immediate value, strong privacy assurance, and clear "this is not surveillance" framing.

### Persona D — Sam, 41 — the Counselor (roadmap, read-only)
- **Context:** manages 40+ clients. Wants a consented weekly summary, not another dashboard to babysit.
- **Note:** out of hackathon scope; mention as roadmap to show product maturity.

## 4. User journeys

### Journey 1 — Proactive nudge (the differentiator)
1. Maya does a 20-second morning check-in (mood, sleep, craving level, any triggers). Voice or taps.
2. Steady Score engine combines today's signals with her history → **risk: elevated**.
3. Anchor sends a *gentle, explained* nudge: *"Rough sleep + a stressful calendar today. Want a 2-minute grounding reset before your 10am?"* — with the **why** visible.
4. She taps yes → guided reset → logged → score updates.

### Journey 2 — Zero-typing crisis (the wow)
1. Craving spikes at 9pm. Maya opens Anchor → one giant button: **"I'm Struggling."**
2. One tap → voice-first flow: *"I'm here. Let's ride this out together. Breathe with me."*
3. Anchor runs urge-surfing + HALT check by voice. Offers: call Guardian, call sponsor, or crisis line — one tap each.
4. If the safety classifier detects self-harm language → **immediate** crisis-resource card + human handoff, bypassing normal flow.
5. Afterward: one-tap log, optional share-with-Guardian.

### Journey 3 — Caregiver coaching
1. Maya opts to share "I had a hard night" with David.
2. David gets a calm alert (not alarming): *"Maya shared a hard moment. She's safe and used her tools."*
3. Caregiver Copilot suggests: *"A good message right now: 'Thinking of you, proud of you, here whenever you want to talk.' Avoid: asking for details or 'are you okay??'"*
4. David sends the suggested message with one tap or edits it.

### Journey 4 — Grounded question
1. Maya asks the companion: *"Is it normal to still crave after 8 months?"*
2. RAG retrieves from curated sources (e.g., NIDA/SMART Recovery content) → grounded, cited answer.
3. If she asks something clinical/dosing-related → Anchor gives the cited general info **and** recommends contacting her clinician; never invents specifics.

## 5. Feature list (prioritized)

| Priority | Feature | Persona | Notes |
|---|---|---|---|
| P0 | Auth + onboarding + consent | All | JWT + refresh; consent captured & versioned |
| P0 | Daily check-in (voice/tap) | Member | Feeds Steady Score |
| P0 | **Steady Score** + explanation | Member | Explainable rules/heuristic engine |
| P0 | AI companion chat (RAG) | Member | Grounded, cited |
| P0 | **Safety classifier + escalation ladder** | Member | Deterministic; blocks unsafe output |
| P0 | **One-tap "I'm Struggling"** voice flow | Member | Zero-typing |
| P0 | Urge-surfing timer | Member | Evidence-based |
| P1 | Caregiver linking + consent | Both | Revocable |
| P1 | **Caregiver Copilot** guidance | Guardian | "say this / avoid this" |
| P1 | Consented alerts | Both | Member controls each share |
| P1 | Trusted knowledge base | Member | Curated + cited |
| P1 | Milestones + streaks (non-shaming) | Member | Relapse = reset, not failure |
| P2 | Medication reminders + adherence | Member | Feeds score |
| P2 | Trigger map (locations/times) | Member | Feeds nudges |
| P2 | Notifications/scheduler | All | Proactive nudges |
| P3 | Counselor read-only summary | Counselor | Roadmap |

## 6. Competitive analysis

| Product | What it does | Gap Anchor fills |
|---|---|---|
| **Generic recovery trackers** (sober-day counters) | Streak counting, badges | No risk sensing, no in-the-moment help, shame on relapse |
| **Meditation/wellness apps** | Guided audio, generic calm | Not SUD-specific, not personalized to triggers, no caregiver, no crisis path |
| **Peer-support / meeting-finder apps** | Community + meeting schedules | Reactive; help only when the user seeks it; no proactive risk detection |
| **Generic AI chatbots** | Free-form supportive chat | Ungrounded (hallucination risk), no long-term memory, no deterministic safety, no caregiver, no structured intervention |
| **Clinical portals / EHR patient apps** | Appointments, messaging clinician | High friction, not real-time, not designed for a 9pm craving |

**Anchor's defensible wedge:** the *combination* — proactive explainable risk + zero-typing crisis flow + caregiver dyad + grounded RAG + deterministic safety. No single competitor combines even three of these.

## 7. Differentiators (say these on stage)

1. **Explainable Steady Score** — risk you can see the reasoning behind.
2. **Zero-typing crisis mode** — designed for the moment cognitive load peaks.
3. **Caregiver Copilot** — the only recovery product that coaches the *supporter*.
4. **Grounded + gated AI** — RAG for truth, safety layer for safety. The LLM never freestyles a crisis.
5. **Non-shaming model of relapse** — recovery as a journey, encoded into the UX (resets, not zeros).

## 8. Success metrics (KPIs)

**North-star metric:** *Supported high-risk moments* — count of elevated-risk moments where the user engaged an intervention or human before disengaging.

| Category | Metric | Target (demo/pilot framing) |
|---|---|---|
| Engagement | Daily check-in completion rate | ≥ 60% of active days |
| Proactivity | % of nudges sent *before* a user-reported craving | ≥ 50% |
| Crisis support | Median time from "I'm Struggling" tap → first intervention step | < 5 seconds |
| Safety | % of crisis-classified messages routed to human resources | 100% (hard requirement) |
| Grounding | % of AI health-claims with a cited source | 100% (hard requirement) |
| Caregiver | % of shared moments that produce a caregiver action | ≥ 40% |
| Retention | Week-4 retention | ≥ 35% |
| Trust | Post-session "I felt supported" rating | ≥ 4.2 / 5 |
| Safety UX | False-negative rate of safety classifier (missed crises) | Tracked, target → 0; tuned to over-escalate |

**Guardrail metrics (must not regress):** false-negative crisis rate, ungrounded-claim rate, unauthorized-share incidents — all monitored; any nonzero value is a P0 bug.
