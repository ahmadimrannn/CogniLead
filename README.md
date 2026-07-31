# CogniLead - Inbound Lead Qualification & CRM Enrichment Agent

An AI agent that ingests inbound leads, extracts and enriches them with company data, scores them against ICP criteria, and syncs qualified leads directly into HubSpot — with human-in-the-loop review for ambiguous cases and durable, crash-safe state.

Built with LangGraph, FastAPI, and HubSpot.

---

## What this actually does

A raw inbound lead (name, email, free-text message) comes in through a single API endpoint. The system:

1. **Extracts** structured information from the free text — name, role, company, stated need — including inferring implicit authority (e.g. "I run a consulting shop" → decision-maker), not just quoting explicit titles.
2. **Enriches** the company with real web data via search, and independently judges *whether the enrichment actually matches the right company* — a generic company name can return a confident, detailed profile for a completely unrelated business, and this system catches that instead of trusting it.
3. **Scores** the lead against ICP criteria, deliberately ignoring grammar, formality, and writing polish — verified with controlled tests using identical facts written formally vs. messily.
4. **Gates** every lead through a deterministic (non-LLM) checkpoint: auto-accept, auto-reject, or pause for human review — the one part of the pipeline designed to be 100% explainable and consistent, on purpose.
5. **Writes back to HubSpot** — creates or updates the contact and company, associates them, and logs the score and reasoning as a note — with automatic, idempotent retry on failure, and honest disclosure in the CRM whenever enrichment data was disregarded due to unresolved company identity.

State is checkpointed to Postgres at every step, so a process crash mid-write doesn't lose progress, corrupt a lead, or create duplicate CRM records on retry.

---

## Architecture

```
POST /leads
     │
     ▼
┌─────────────────┐
│ lead_extractor   │  → structured extraction (name, role, company, need)
└────────┬─────────┘
         ▼
┌─────────────────────┐
│ company_enrichment   │  → web search + identity/attribute confidence judgment
└────────┬─────────────┘
         ▼
┌─────────────────┐
│ lead_scorer      │  → ICP score (1–10) + reasoning
└────────┬─────────┘
         ▼
┌───────────────────────┐
│ human_review_gate      │  → deterministic Python logic, not an LLM call
└──────┬─────────┬───────┘
       │         │
  accept/reject  needs_human_review
       │         │
       │    (graph interrupts, waits for POST /leads/resume)
       │         │
       ▼         ▼
┌─────────────────┐
│ crm_writer       │  → create/update contact + company, associate, note
└────────┬─────────┘
         │ (on failure)
         ▼
┌─────────────────┐
│ crm_retrier      │  → resumes from the next incomplete write step
└──────────────────┘
```

This is a **fixed-topology workflow with LLM judgment inside individual nodes** — not a dynamic/autonomous agent. Control flow (which node runs next) is deterministic Python; only the *content* of extraction, enrichment judgment, and scoring is LLM-driven.

---

## Stack

- **LangGraph** — graph orchestration, `interrupt()`/`Command(resume=...)` for human-in-the-loop, `PostgresSaver` for durable checkpointing
- **FastAPI** — webhook ingestion (`/leads`, `/leads/resume`, `/leads/failed`)
- **HubSpot** — target CRM, auth via Service Key, scopes: `crm.objects.contacts.read/write`, `crm.objects.companies.read/write`
- **Tavily** (`langchain_tavily.TavilySearch`) — web search for company enrichment
- **Postgres** — durable checkpoint storage (`psycopg_pool` connection pool)
- **Pydantic** — structured schemas for every node's output

---

## Setup

### 1. Environment

```bash
cp .env
```

Required variables:

```
DB_URI=postgresql://postgres:<YOUR_POSTGRES_PASSWORD>@localhost:5432/<YOUR_DATABASE_NAME>
HUBSPOT_SERVICE_KEY=your_service_key_here
TAVILY_API_KEY=your_tavily_key_here
<LLM_PROVIDER>_API_KEY=your_llm_provider_key_here
```

### 2. Database

Requires a running Postgres instance. Checkpoint tables are created automatically on first run via `checkpointer.setup()` — no manual migration needed.

### 3. Install and run

```bash
uv add -r requirements.txt
cd src/cognilead
uv run python -m uvicorn api.main:app --reload
```

---

## API

### `POST /leads`

Submit a raw inbound lead.

```json
{
  "lead_text": "Hi, I'm the VP of Sales at Notion. We're evaluating tools to automate inbound lead scoring...",
  "email": "vp.sales@notion.so"
}
```

Two possible responses:

**Completed immediately** (auto-accepted or auto-rejected):
```json
{
  "status": "completed",
  "crm_write_status": "succeeded",
  "contact_id": "...",
  "company_id": "...",
  "...": "..."
}
```

**Paused for human review**:
```json
{
  "status": "interrupted",
  "thread_id": "...",
  "interrupt": {
    "message": "...",
    "lead_data": "...",
    "review_status_reason": "..."
  }
}
```

### `POST /leads/resume`

Resume a paused lead with a human decision.

```json
{
  "thread_id": "the-thread-id-from-the-interrupt",
  "action": "approve"
}
```

`action` must be `"approve"` or `"reject"`.

### `GET /leads/failed`

Lists `lead_id`s whose CRM write hit the retry ceiling and were marked `permanent_failed`, for manual inspection.

---

## Design decisions worth knowing about

These weren't obvious going in — they came out of real failure modes found through deliberate edge-case testing, not hypothetical review.

- **The human review gate is plain Python, not an LLM call.** Its entire value is being the one reliably explainable, consistent checkpoint in the pipeline. The inputs (score, enrichment status, name-match confidence) are already clean structured data — they don't need judgment, they need a rule.
- **Enrichment identity and attribute confidence are judged independently, and identity is decided first.** A generic company name can return a confident profile for the wrong company. Two separate fields — `enrichment_status` (attribute consistency) and `name_match_confidence` (identity) — catch this, and the prompt forces the model to commit to identity confidence *before* it sees whether the profile "looks right," so a well-documented wrong company can't talk the model into a false positive.
- **`NOT_FOUND` and `FAILED` enrichment are scored as neutral, not negative.** A legitimately new or small business can have zero web presence — that's a fact about visibility, not about lead quality, and shouldn't be penalized by a generic node whose behavior client-specific ICP rules should govern instead.
- **When enrichment is disregarded, the CRM note says so, explicitly.** If identity confidence is uncertain/contradicted or attributes mismatch, the scoring node falls back to self-reported data only — and the HubSpot note carries that disclosure forward, so a human reading the CRM later doesn't mistake unverified data for verified data.
- **Leads with no stated company name skip company creation entirely** rather than inventing a placeholder name or rejecting the lead at the door. The contact is still created, and the note explicitly flags that no company was stated — disclosure over fabrication.
- **CRM writes are step-aware, not call-aware, for retry purposes.** Each write step (company, contact, association, note) records its result into checkpointed state the moment it succeeds. A retry checks state first and only performs the next incomplete step — this is what prevents a network blip from creating a duplicate company on retry.
- **Internal `lead_id` and HubSpot's own object IDs are kept as separate concepts.** The former is a UUID generated once per run, used as the LangGraph `thread_id` and written into every CRM note for traceability. It is not, and cannot be, the same value as HubSpot's contact/company IDs — those are assigned independently by HubSpot and linked via the associations API.

---

## Known open questions

- Whether `uncertain` name-match confidence should be treated as neutral (like `NOT_FOUND`) or remain its own lower-confidence tier in scoring — currently the latter, meaning a legitimately good lead with a too-generic-to-verify company name can be penalized for something unrelated to lead quality.
- Company dedup on write-back currently treats more than one name match as "not found" rather than attempting disambiguation — acceptable for now, not hardened against high-volume real-world name collisions.

---

## Testing

A Postman collection (`Lead Qualifier Project Collection`) covers the full test matrix end to end:

1. Auto-accept — clean lead, verified enrichment, immediate CRM write
2. Ambiguous lead — triggers human review, resumed with approval
3. Enrichment mismatch — lead is written with the enrichment-disregarded disclosure note
4. Induced mid-write failure — company created, contact write fails, resumed via retry with no duplicate company created

---

## License

MIT