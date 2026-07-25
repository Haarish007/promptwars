# 11 · Demo Flow & Judge Checklist

## Part 1 — The 5-minute demo script (rehearse this exactly)

**Golden rule:** show the *differentiators*, not the CRUD. Every second on screen should demonstrate proactivity, zero-typing crisis, caregiver dyad, grounding, or safety. Pre-seed data so nothing is typed live.

**0:00 — Hook (20s).**
"Most recovery apps wait for you to ask for help. But the hardest moments are exactly when you *can't* ask. Meet Anchor — a proactive recovery companion that acts before the moment gets hard, and brings your support person with you." Show the home screen with the **Steady Score** meter and the giant **I'm Struggling** button.

**0:20 — Proactive Steady Score (50s).**
Do a 15-second check-in (mostly pre-filled). Watch the score move to **Elevated** and — crucially — tap the **"why?"** to reveal the explanation: *"poor sleep + evening + skipped meeting → HALT flag."* Say: "This isn't a black box. Maya can see *why*, and so can we." Anchor sends a gentle nudge.

**1:10 — Grounded companion (45s).**
Ask: "Is it normal to still crave after 8 months?" Show the answer **with a citation** to the trusted knowledge base. Then ask a clinical/dosing question and show Anchor **declining to invent specifics** and recommending a clinician. Say: "It only speaks when it can cite a trusted source. That's how you make AI safe for health."

**1:55 — Zero-typing crisis (70s) — the centerpiece.**
Tap **I'm Struggling** once. It instantly (<1.5s) opens a calm, voice-guided flow — no typing, huge buttons. Ride a 20-second **urge-surf**. Then type/say a line with clear crisis language and show the **safety layer short-circuit**: a fixed, reviewed crisis card with **988 / regional resources** and one-tap human actions. Say: "The AI never freestyles a crisis. Classification and routing are deterministic. This is the difference between a demo and a product you'd trust with a real person."

**3:05 — Caregiver dyad (60s).**
Maya taps **share this moment**. Switch to David's (guardian) view: a *calm* alert plus **Caregiver Copilot** — a suggested supportive message and an explicit "avoid" list. Send it in one tap. Say: "We're the only recovery product that coaches the *supporter*, because recovery is a team sport."

**4:05 — Close (55s).**
Recap the four differentiators on one slide (proactive · zero-typing crisis · grounded+gated AI · caregiver dyad). State impact + KPIs + responsible-AI stance. End on the vision line: *"No one should face a high-risk moment alone or unprepared."*

### Backup / failure plan
- Pre-record a 90-second screen capture of the crisis + caregiver flows in case live AI/network fails.
- Have a "safe mode" toggle that uses canned grounded responses if the provider is down (still demonstrates the pipeline + guards).

## Part 2 — Judge checklist (map to typical rubric)

| Rubric dimension | What we show | Where |
|---|---|---|
| **Innovation** | Explainable Steady Score, Caregiver Copilot, zero-typing crisis | Demo 0:20, 1:55, 3:05 |
| **Use of AI** | Orchestration + RAG + tools + structured output + safety classifier | `docs/04`; Demo 1:10, 1:55 |
| **Technical depth** | Clean Architecture, relational schema, deterministic safety subsystem | `docs/05,06,08` |
| **Responsible AI** | Out-of-model guards, crisis short-circuit, grounding, consent | `docs/08`; Demo 1:55 |
| **Impact** | Proactive support + caregiver dyad for a high-stakes population | `docs/02` KPIs |
| **UX / Design** | Voice-first, ≤1-tap crisis, AA accessibility, non-shaming | `docs/08 Part 3`; Demo 1:55 |
| **Domain understanding** | HALT, urge-surfing, escalation ladder, non-shaming relapse | `docs/02,03,04` |
| **Presentation** | Tight 5-min script + backup recording | this doc |
| **Use of Google platform** | Gemini as primary provider via clean adapter | `docs/04 §4` |

## Part 3 — Anticipated judge questions (have answers ready)

- **"How do you prevent the AI from giving harmful advice?"** → Two deterministic gates outside the model + grounded-only health claims + crisis short-circuit. Walk the pipeline diagram.
- **"Isn't a risk score dangerous / stigmatizing?"** → It's explainable, supportive-toned, never diagnostic, and drives *offers* of help, not judgments. Non-shaming relapse model.
- **"What about privacy?"** → Consent gates every share; field-level encryption; data minimization; export/delete; "not surveillance."
- **"Is this a medical device?"** → No — explicitly a support tool with disclaimers and human-handoff; we designed the boundaries in, not around.
- **"What's real vs. mocked?"** → Full pipeline, RAG, safety layer, caregiver dyad are real; wearable HRV signal and ML risk model are roadmap (we ship an explainable rules engine).
- **"How would you validate it clinically?"** → Roadmap: clinician advisory review of prompts/templates, red-team safety evals (already built), and a supervised pilot.

## Part 4 — Pre-demo checklist (T-minus 30 min)
- [ ] Seeded member (Maya) + guardian (David) accounts logged in on two windows.
- [ ] Curated KB loaded; citations resolve.
- [ ] Region set so crisis resources show correctly.
- [ ] Safety classifier red-team line rehearsed; template renders.
- [ ] SOS first-step renders < 1.5s on the demo network.
- [ ] Backup recording queued; safe-mode toggle tested.
- [ ] One-slide differentiator recap ready.
- [ ] Disclaimer visible (shows responsibility, not weakness).
