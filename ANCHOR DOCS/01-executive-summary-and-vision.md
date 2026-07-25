# 01 · Executive Summary & Vision

## Executive Summary

Anchor is a multi-modal, AI-powered recovery and prevention platform for people living with Substance Use Disorder (SUD) and the caregivers who support them. Unlike existing recovery apps — which are largely static content libraries, habit trackers, or generic chatbots — Anchor functions as an **explainable decision-support system** that anticipates high-risk moments, intervenes with evidence-based micro-interventions, and coordinates a trusted human support network.

The platform is built on three product pillars:

1. **Proactive, not reactive.** A live, explainable *Steady Score* estimates near-term relapse risk from lightweight daily signals (mood, sleep, cravings, HALT states, triggers, adherence, context) and nudges the user *before* a crisis, instead of waiting to be asked.

2. **Lowest possible cognitive load at the worst possible moment.** A single tap on **"I'm Struggling"** launches a zero-typing, voice-first intervention flow. During cravings and distress, users don't search articles or type paragraphs — Anchor talks them through it.

3. **Recovery is a dyad.** With explicit consent, a caregiver is linked and supported by a **Caregiver Copilot** that generates situation-specific, non-judgmental guidance ("what to say / what to avoid") and coordinates alerts only when the user chooses to share.

Every AI response is grounded in a **curated, cited clinical knowledge base** (Retrieval-Augmented Generation) and passed through a **deterministic safety layer**. Crisis and self-harm signals never depend on model improvisation — they route to real human resources through a fixed escalation ladder.

Anchor is delivered as a React (Vite + Tailwind) web app on S3/CloudFront and a FastAPI backend on Ubuntu (Nginx `/promptwars`, port `8100`, systemd), backed by AWS RDS (PostgreSQL). It is engineered to be demonstrable in a five-minute hackathon slot while remaining a credible foundation for a real product.

## The problem in one sentence

People recovering from SUD spend most of their lives outside clinical settings, where personalized, timely support is unavailable exactly when cognitive capacity is lowest — and their caregivers are left guessing how to help.

## Why now

Generative AI finally makes it feasible to combine (a) natural-language understanding of a person's emotional state, (b) long-term personalized memory, (c) retrieval over trusted clinical content, and (d) structured, tool-driven action — into a single companion that behaves less like a search box and more like a calm, informed guide. The opportunity is not "a chatbot for addiction." It is an **orchestrated support system** where the language model is one component inside a safety-gated decision engine.

## Vision Statement

> **We envision a world where no one faces a high-risk recovery moment alone or unprepared.**
>
> Anchor's vision is to be the always-present, always-calm companion that understands each person's unique recovery journey, recognizes rising risk before it becomes a crisis, and — with a single tap or spoken word — delivers the right evidence-based support and the right human connection at the right time. We extend that circle of care to the family members and caregivers who love them, giving supporters the confidence to help without harm. Anchor exists to turn isolated, high-cognitive-load moments into guided, supported, survivable ones — and to make proactive, personalized, human-centered recovery support available to anyone, anywhere.

## Design principles (the north star for every decision)

1. **Safety over cleverness.** When in doubt, escalate to a human. The model never gates a crisis.
2. **Lower the effort, not the stakes.** Assume the user has minimal cognitive capacity in the moments that matter most.
3. **Explain the machine.** Risk scores and recommendations always show their reasoning. No black boxes with vulnerable people.
4. **Ground every claim.** Health-adjacent statements are retrieved from cited, reviewed sources — never free-form generation.
5. **Consent is the product.** Nothing is shared with caregivers, clinicians, or logs without explicit, revocable consent.
6. **Dignity first.** Non-judgmental, person-first language. Relapse is a data point, not a failure.

## Scope for the hackathon build (what "done" means)

**In scope (demo-ready):** auth + onboarding, daily check-in, Steady Score with explanation, AI companion chat (RAG-grounded), one-tap Struggling/SOS voice flow, urge-surfing timer, safety classifier + escalation ladder, caregiver linking + Caregiver Copilot + consented alerts, trusted knowledge base browse/search, medication & milestone tracking, notifications, audit logging, and a scripted demo path.

**Out of scope (state explicitly to judges as roadmap):** real clinical integration/EHR, wearable HRV ingestion (mock the signal), native mobile apps, insurance/billing, production-grade ML risk model (ship an explainable rules+heuristic engine, note ML as roadmap).
