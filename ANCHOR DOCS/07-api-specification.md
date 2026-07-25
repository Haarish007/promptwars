# 07 · API Specification

- **Base URL:** `https://<host>/promptwars/api/v1`
- **Auth:** `Authorization: Bearer <access_jwt>` on protected routes.
- **Content:** JSON; AI chat supports streamed responses (SSE/chunked).
- **Versioning:** `/api/v1`.
- All requests/responses validated by Pydantic schemas. All list endpoints paginated (`?limit`, `?cursor`).

## Standard error model
```json
{ "error": { "code": "string", "message": "human-safe message", "correlation_id": "uuid" } }
```
- Never leak stack traces or provider errors. Codes: `unauthorized`, `forbidden`, `validation_error`, `not_found`, `rate_limited`, `conflict`, `dependency_unavailable`, `safe_fallback`.

## Auth
| Method | Path | Body | Returns | Notes |
|---|---|---|---|---|
| POST | `/auth/register` | email, password, role | 201 user | password hashed; consent captured |
| POST | `/auth/login` | email, password | access + refresh | rate-limited |
| POST | `/auth/refresh` | refresh_token | new access + refresh | rotates + revokes old |
| POST | `/auth/logout` | refresh_token | 204 | revokes refresh |
| GET | `/auth/me` | — | current user | |

## Consent
| Method | Path | Body | Notes |
|---|---|---|---|
| POST | `/consents` | scope, version | grant consent |
| DELETE | `/consents/{scope}` | — | revoke (immediate) |
| GET | `/consents` | — | list active scopes |

## Onboarding / Profile
| Method | Path | Notes |
|---|---|---|
| POST | `/onboarding` | goal, substance_focus, start_date, triggers, preferences, region |
| GET/PUT | `/profile` | read/update profile & preferences |
| GET/POST/DELETE | `/emergency-contacts` | manage contacts + crisis resource prefs |
| GET/POST/DELETE | `/triggers` | manage known triggers |

## Check-in & Risk
| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/checkins` | mood, sleep_quality, craving, halt{...}, note?, source | check-in + **recomputed Steady Score w/ explanation** |
| GET | `/checkins?range=` | — | trend series |
| GET | `/risk/current` | — | `{ score, band, factors[] }` (explainable) |
| GET | `/risk/history` | — | score snapshots |

**POST /checkins → 201**
```json
{
  "checkin": { "id": "...", "mood": 2, "craving": 7, "halt": {"tired":true,"lonely":true} },
  "risk": { "score": 68, "band": "elevated",
    "factors": [
      {"factor":"craving_trend","impact":"+22","detail":"craving up 3 days"},
      {"factor":"sleep","impact":"+15","detail":"poor sleep"},
      {"factor":"halt","impact":"+12","detail":"Tired + Lonely"}
    ] },
  "suggested_action": { "type": "grounding", "label": "2-minute reset" }
}
```

## AI Companion (safety-gated)
| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/companion/message` | conversation_id?, content, source(text\|voice) | streamed grounded reply |
| GET | `/conversations` / `/conversations/{id}` | — | history |

**Response envelope (post-guard verified):**
```json
{
  "conversation_id": "...",
  "reply": "It makes sense you'd still feel cravings...",
  "citations": ["kb-142"],
  "safety_label": "distress",
  "tone_band": "supportive",
  "suggested_action": { "type": "urge_surf" }
}
```
- If `safety_label ∈ {crisis, self_harm, harm_to_others, medical_emergency}` → response is the **fixed crisis template** with resources + one-tap actions; generation is short-circuited (see Safety).

## Safety / SOS
| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/safety/classify` | content | `{ label, confidence, signals }` (internal/support) |
| POST | `/sos/start` | source | immediate first calming step + one-tap actions (pre-warmed, non-AI) |
| POST | `/sos/action` | action(call_guardian\|call_sponsor\|crisis_line\|share\|urge_surf) | executes/validates action |
| GET | `/resources?region=` | — | region-appropriate crisis resources |

**POST /sos/start → 200** (must be fast, no model dependency for step 1)
```json
{
  "session_id": "...",
  "first_step": { "type": "breathe", "voice_script": "I'm here with you. Let's breathe..." },
  "actions": [
    {"id":"urge_surf","label":"Ride it out with me"},
    {"id":"call_guardian","label":"Call David"},
    {"id":"crisis_line","label":"988 Lifeline","phone":"988"}
  ]
}
```

## Urge Surfing
| Method | Path | Body |
|---|---|---|
| POST | `/interventions/urge-surf/start` | craving_before |
| POST | `/interventions/{id}/complete` | craving_after → logs + updates score + memory |

## Caregiver / Guardian
| Method | Path | Notes |
|---|---|---|
| POST | `/caregiver/invite` | member invites guardian by email |
| POST | `/caregiver/accept` | guardian accepts (mutual consent) |
| DELETE | `/caregiver/link/{id}` | revoke (immediate, audited) |
| POST | `/caregiver/share` | member shares a moment (requires active consent) → creates share_event + Copilot suggestion |
| GET | `/caregiver/feed` | guardian's consented alerts + suggestions |
| GET | `/caregiver/copilot/{share_id}` | Copilot suggestion `{ suggested_message, avoid[], rationale }` |

## Knowledge Base
| Method | Path | Notes |
|---|---|---|
| GET | `/kb/articles` / `/kb/articles/{id}` | curated, cited content |
| GET | `/kb/search?q=` | search corpus |

## Tracking / Notifications
| Method | Path | Notes |
|---|---|---|
| GET/POST | `/milestones` | non-shaming milestones; relapse = reset |
| GET/POST | `/medications` + `/medications/{id}/log` | schedule + adherence |
| GET | `/notifications` / PUT `/notifications/{id}/ack` | nudge feed |

## Health
| Method | Path |
|---|---|
| GET | `/health` (liveness) · `/health/ready` (readiness incl. AI provider + DB) |

## Cross-cutting rules
- **Ownership enforcement:** every member-scoped resource checks `resource.user_id == current_user.id` (or an active caregiver link with matching consent) in the service layer.
- **Idempotency:** `/checkins`, `/caregiver/share`, `/interventions/*/complete` accept an `Idempotency-Key`.
- **Rate limits:** tighter on `/auth/*`, `/companion/*`, `/sos/*`.
- **Streaming:** `/companion/message` streams tokens; the post-guard runs on the assembled result before finalizing (or streams then reconciles with a guard pass).
