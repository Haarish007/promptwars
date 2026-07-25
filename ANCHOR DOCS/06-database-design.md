# 06 · Database Design (AWS RDS / PostgreSQL — relational)

Relational schema only. No Firebase/Firestore. All access via the repository layer using parameterized/ORM queries. Migrations via Alembic. Sensitive free-text (notes, transcripts) is app-level encrypted; store ciphertext, not plaintext.

## Conventions
- All tables: `id UUID PK DEFAULT gen_random_uuid()`, `created_at timestamptz`, `updated_at timestamptz`.
- Soft-delete via `deleted_at timestamptz NULL` where user data deletion must be recoverable/auditable; hard-delete supported for data-subject deletion requests.
- FKs `ON DELETE` chosen per relationship (restrict for audit-linked rows).
- Enums implemented as Postgres enums or `varchar + CHECK`.

## Entity list & purpose

| Table | Purpose |
|---|---|
| `users` | Account, role, auth |
| `refresh_tokens` | Rotating refresh tokens |
| `consents` | Versioned, scoped, revocable consent records |
| `member_profiles` | Recovery goal, start date, substance focus, preferences |
| `emergency_contacts` | User's contacts + crisis-resource preferences |
| `triggers` | Known triggers (type, label, time/location metadata) |
| `check_ins` | Daily mood/sleep/craving/HALT + note (encrypted) |
| `risk_scores` | Computed Steady Score snapshots + explanation |
| `risk_config` | Externalized weighting config (tunable) |
| `conversations` | Companion chat sessions |
| `messages` | Per-turn messages (role, content encrypted, citations, tone_band) |
| `safety_events` | Every classification + action (audit-critical) |
| `interventions` | Urge-surf/grounding/etc. sessions + outcomes |
| `memory_events` | Recovery Memory items for per-user RAG |
| `kb_articles` | Curated knowledge-base content |
| `kb_chunks` | Retrievable passages (+ optional embedding) |
| `caregiver_links` | Member↔Guardian relationship + status |
| `share_events` | Consented shares from Member to Guardian |
| `caregiver_suggestions` | Copilot outputs shown to Guardian |
| `milestones` | Streaks/milestones (non-shaming) |
| `medications` + `medication_logs` | Schedule + adherence |
| `notifications` | Scheduled/sent nudges |
| `audit_logs` | Tamper-evident system audit trail |

## Key table sketches (columns → notes)

**users**
`id, email (unique, citext), password_hash, role (member|guardian), status, last_login_at`. Never store plaintext passwords; Argon2id/bcrypt.

**refresh_tokens**
`id, user_id FK, token_hash, expires_at, revoked_at, replaced_by FK NULL`. Store hash, not raw token. Rotation = create new + set `replaced_by` + revoke old.

**consents**
`id, user_id FK, scope (data_processing|share_with_guardian|voice_processing|...), version, granted_at, revoked_at NULL`. A row per grant; revocation sets `revoked_at`. Enforce "no share without active consent" in service layer.

**member_profiles**
`id, user_id FK unique, recovery_goal, substance_focus, recovery_start_date, voice_first bool, nudge_frequency, quiet_hours_start, quiet_hours_end, region (for crisis resources)`.

**emergency_contacts**
`id, user_id FK, name, relationship, phone (encrypted), is_sponsor bool, priority int`. Plus per-region default crisis resources resolved at runtime.

**check_ins**
`id, user_id FK, mood smallint (1-5), sleep_quality smallint, craving smallint (0-10), halt_hungry/angry/lonely/tired bool, note_ciphertext, source (voice|tap), created_at`. Index `(user_id, created_at desc)`.

**risk_scores**
`id, user_id FK, score smallint (0-100), band (low|guarded|elevated|high), factors jsonb (top contributing factors + weights), checkin_id FK NULL, created_at`. `factors` powers the explanation UI.

**risk_config**
`id, key, weights jsonb, active bool, version`. Lets you tune the engine without code changes (`FR-RISK-3`).

**conversations / messages**
`conversations(id, user_id FK, started_at, summary_ciphertext)`.
`messages(id, conversation_id FK, role (user|assistant|system), content_ciphertext, safety_label, citations jsonb, tone_band, created_at)`.

**safety_events** (audit-critical, minimize free-text)
`id, user_id FK, conversation_id FK NULL, label, confidence, action_taken (template_shown|escalated_guardian|crisis_resources|blocked_output|...), resource_shown, tier, created_at`. **Do not** store the raw crisis text beyond what's operationally required; store the classification + action. Access-controlled.

**interventions**
`id, user_id FK, type (urge_surf|grounding|breathing|halt|...), started_at, completed_at, craving_before, craving_after, outcome`. Feeds Steady Score + memory.

**memory_events** (per-user RAG)
`id, user_id FK, kind (trigger|worked_intervention|milestone|preference|relationship), content, salience float, source_ref, created_at`. Retrieved by recency+relevance.

**kb_articles / kb_chunks**
`kb_articles(id, title, body, source_name, source_url, review_date, tags[])`.
`kb_chunks(id, article_id FK, chunk_text, embedding vector NULL, ord)`. Only curated content is retrievable for RAG. (`pgvector` optional; keyword retrieval acceptable for the build.)

**caregiver_links**
`id, member_id FK, guardian_id FK, status (invited|active|revoked), invited_at, accepted_at, revoked_at`. Unique active pair constraint. Both-party consent required.

**share_events**
`id, member_id FK, guardian_id FK, kind (hard_moment|milestone|checkin_summary), summary_ciphertext (member-approved, minimized), created_at`. Nothing here without an active `share_with_guardian` consent.

**caregiver_suggestions**
`id, share_event_id FK, suggested_message, avoid jsonb, rationale, created_at`.

**milestones**
`id, user_id FK, kind, achieved_at, reset_at NULL, note`. Relapse = a reset with encouragement; **history preserved**, never a shameful zero.

**medications / medication_logs**
`medications(id, user_id FK, name, schedule jsonb, active bool)`.
`medication_logs(id, medication_id FK, taken_at, status (taken|missed|skipped))`. Adherence → Steady Score.

**notifications**
`id, user_id FK, type (nudge|reminder|share_alert), scheduled_for, sent_at NULL, payload jsonb, status`.

**audit_logs**
`id, actor_user_id FK NULL, action, entity, entity_id, metadata jsonb, correlation_id, created_at`. Append-only; no PHI in metadata; access-controlled.

## Relationships (ERD summary)
- `users 1—1 member_profiles`, `users 1—* check_ins/risk_scores/conversations/interventions/memory_events/milestones/medications/emergency_contacts/consents`.
- `conversations 1—* messages`; `conversations 1—* safety_events`.
- `caregiver_links` connects two `users` (member ↔ guardian); `share_events 1—1 caregiver_suggestions`.
- `kb_articles 1—* kb_chunks`.

## Indexing & integrity
- Hot indexes: `check_ins(user_id, created_at desc)`, `risk_scores(user_id, created_at desc)`, `messages(conversation_id, created_at)`, `safety_events(user_id, created_at)`, `caregiver_links(member_id, status)`.
- Constraints: unique active caregiver pair; CHECK on score/mood/craving ranges; FK integrity for all audit-linked rows.

## Privacy & retention
- Field-level encryption for notes/transcripts/phone numbers.
- Configurable retention windows per data class; user-initiated export and delete flows (`NFR-SEC-8`).
- `safety_events` and `audit_logs` retained per policy and access-restricted.
