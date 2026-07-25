# 04 · AI Architecture

This is the heart of the submission. The thesis: **the LLM is one component inside a safety-gated decision-support pipeline — not the product.** Judges reward teams who show orchestration, grounding, and guardrails over teams who wire a chat box to an API.

## 1. The orchestration pipeline (every AI turn)

```
                         ┌─────────────────────────────┐
User input (text/voice)  │  1. Ingest & Transcribe     │  STT if voice
        │                └──────────────┬──────────────┘
        ▼                               ▼
┌───────────────────────────────────────────────────────┐
│  2. SAFETY CLASSIFIER  (runs first, deterministic)     │
│     label ∈ {none, distress, crisis, self_harm,        │
│              harm_to_others, medical_emergency}         │
└───────────────┬───────────────────────┬───────────────┘
                │ crisis/self_harm/...   │ none/distress
                ▼                        ▼
   ┌────────────────────────┐  ┌──────────────────────────────┐
   │ 3a. CRISIS SHORT-CIRCUIT│  │ 3b. CONTEXT ASSEMBLY          │
   │  fixed reviewed template│  │  - Recovery Memory (user RAG) │
   │  + region resources     │  │  - Knowledge Base retrieval   │
   │  + one-tap human actions│  │  - Steady Score + signals     │
   │  (NO LLM freestyle)     │  │  - Conversation summary        │
   └───────────┬────────────┘  └───────────────┬──────────────┘
               │                                ▼
               │                 ┌──────────────────────────────┐
               │                 │ 4. LLM GENERATION (grounded)  │
               │                 │  system + context + tools     │
               │                 │  structured/streamed output   │
               │                 └───────────────┬──────────────┘
               │                                 ▼
               │                 ┌──────────────────────────────┐
               │                 │ 5. POST-GENERATION GUARD      │
               │                 │  block dosing / methods /     │
               │                 │  discourage-help; verify      │
               │                 │  citations present            │
               │                 └───────────────┬──────────────┘
               ▼                                 ▼
        ┌────────────────────────────────────────────────┐
        │ 6. RESPONSE + ACTIONS + AUDIT LOG              │
        │  render, execute tool calls, log safety event  │
        └────────────────────────────────────────────────┘
```

**Key property:** stages 2 and 5 are deterministic gates the LLM cannot bypass. Stage 3a is chosen by classification, not by the model deciding it's a crisis.

## 2. Components

### 2.1 Safety Classifier
- **Purpose:** classify risk in inbound user text before generation.
- **Implementation:** a dedicated classification call (small/fast model or a constrained prompt returning strict JSON) **plus** a deterministic keyword/pattern pre-filter for unambiguous crisis language. The pattern filter can *raise* severity but never *lower* it.
- **Output (strict JSON):** `{ "label": "...", "confidence": 0.0-1.0, "signals": ["..."] }`.
- **Fail-safe:** on timeout/error → treat as `distress` (cautious path), never `none`.
- **Never** relies on the main companion model's judgment alone.

### 2.2 Recovery Memory (per-user RAG)
- Stores durable facts: triggers, what interventions worked, milestones, preferences, relationships, recent check-in trend.
- Retrieval selects the few most relevant memory items for the current turn (keyword + recency + relevance; embeddings optional).
- Writes are explicit "memory events" (e.g., "urge-surfing worked at 9pm") — not raw transcript dumps.

### 2.3 Trusted Knowledge Base (content RAG)
- Corpus = **only** curated, clinically-reviewed passages with source + review date.
- Retrieval returns passages with IDs; the generation prompt must cite passage IDs it used.
- If retrieval returns nothing relevant for a health/clinical question → the companion states it doesn't have a grounded answer and recommends a human/clinician. **No ungrounded medical content.**

### 2.4 Steady Score Engine (decision-support signal)
- Deterministic, explainable (see `docs/03` FR-RISK). Its band + top factors are injected into context so the companion's tone and suggestions match current risk.

### 2.5 Intervention Planner (tool selection)
- Given (message, safety label, Steady band, memory), decides which action to propose: urge-surf, grounding, check-in, resource fetch, caregiver share, or escalate.
- Exposed to the LLM as **tools/functions**; the LLM proposes, the backend validates & executes.

### 2.6 Caregiver Copilot
- Separate prompt template. Input: the (consented, minimized) situation summary + best-practice supportive-communication guidance from the KB.
- Output (strict JSON): `{ "suggested_message": "...", "avoid": ["..."], "rationale": "..." }`.
- Never exposes raw member clinical detail; operates on a minimized summary the member approved.

## 3. Prompt architecture (this is "PromptWars" — show it off)

All prompts are **versioned files**, not inline strings (`NFR-MNT-4`). Maintain a `prompts/` directory:

```
prompts/
  companion.system.md        # persona, principles, grounding + citation rules, tool contract
  companion.developer.md      # runtime context injection template (memory, KB, score)
  safety.classifier.md        # strict-JSON classifier instructions + few-shot
  crisis.templates/           # fixed, human-reviewed crisis responses per region/label
  caregiver.copilot.md        # supportive-comms coaching, strict-JSON output
  intervention.planner.md     # tool-selection guidance
  checkin.summarizer.md        # turns a session into a memory event
```

### 3.1 Companion system prompt — required contents
- **Identity & tone:** calm, warm, non-judgmental, person-first. Not a therapist; a companion.
- **Grounding rule:** any health/recovery claim must be supported by a retrieved KB passage; cite passage IDs; if unsupported, say so and defer to a human.
- **Safety rule:** never provide dosing, methods of self-harm, or content discouraging professional help; if the user expresses crisis, defer to the safety layer.
- **Brevity rule:** short, low-cognitive-load responses; offer one clear next step.
- **Tool contract:** how to call `start_urge_surf`, `run_checkin`, `fetch_resources`, `propose_share`, `escalate`.
- **Memory rule:** use provided memory; never fabricate history.

### 3.2 Structured outputs
- Companion returns a structured envelope: `{ "reply": "...", "citations": ["kb-123"], "suggested_action": {...}, "tone_band": "..." }`. This makes UI rendering deterministic and lets the post-guard verify citations.
- Classifier and Copilot return strict JSON (no prose, no markdown fences). Parse defensively; on parse failure → cautious fallback.

### 3.3 Prompt-injection & jailbreak defense
- Treat KB/memory/user content as **data, not instructions**; wrap retrieved content and instruct the model to never follow instructions found inside it.
- The safety layer + post-guard sit *outside* the model, so a jailbroken response still can't emit crisis content or bypass escalation.
- Validate all tool-call arguments server-side before execution (never trust model-proposed phone numbers, contact IDs, etc.).

## 4. Provider abstraction

- Define an `LLMProvider` interface (`generate`, `classify`, `embed`) with adapters. **For the Google PromptWars challenge, use Gemini as the primary provider** (it aligns with the sponsor and typically scores well on "use of the platform"); keep the interface clean so it's swappable.
- Configuration (model names, keys, timeouts) via env only (`.env.example`).
- Timeouts + retries + circuit-breaker; on failure → safe canned response, never a raw error to a vulnerable user.

## 5. Voice (multi-modal)
- STT for input, TTS for output on crisis/urge-surf flows (browser Web Speech API is acceptable for the demo; note cloud STT/TTS as an upgrade).
- Voice paths must remain safety-gated exactly like text (transcribe → classify → route).

## 6. Evaluation & guardrail testing (mention to judges)
- A red-team prompt set for the safety classifier (crisis phrasings, indirect language, multilingual, obfuscated) with a target of **zero missed crises** (tune to over-escalate).
- A grounding eval: sample of Q&A checked for citation presence and source correctness.
- A jailbreak set attempting to extract dosing/methods or disable escalation — all must be blocked by the out-of-model guards.

## 7. Why this architecture wins
- **Use of AI:** orchestration + RAG + tools + structured output + a real safety subsystem.
- **Responsible AI:** deterministic guardrails a judge can trust with a vulnerable population.
- **Prompt craft:** versioned, layered prompts with strict outputs and injection defense — directly on-theme for PromptWars.
