# Technical Requirements Document (TRD)

**Project:** AI Growth Hacker / Marketing Ops Agent (Telegram MVP)

**Duration:** 2 Weeks

---

## 1. System Overview

A **Telegram bot interface** where users submit campaign requests. A **supervisor agent** (Python + FastAPI) orchestrates subtasks, routing to specialized tool functions. All **LLM-based jobs** run **locally via Ollama**. Images are generated via a **local Stable Diffusion API**. Campaign results (text + images) are persisted and returned to Telegram in structured responses.

---

## 2. System Architecture

### 2.1 High-Level Components

- **Telegram Gateway**
    - User interface via `python-telegram-bot`.
    - Forwards user requests to supervisor.
    - Renders campaign results (text, buttons, images).
- **Supervisor (FastAPI app)**
    - Orchestrates tasks → decides which tool function to call.
    - Enforces JSON schemas for tool outputs.
    - Handles retries and error reporting.
- **Tool Functions (Local Agents)**
    - **Audience Research Agent** – Local LLM (Ollama).
    - **Content Agent** – Local LLM (Ollama).
    - **Scheduler Agent** – Local LLM (Ollama).
    - **Creative Agent** – Local Stable Diffusion API.
    - **External API Connector** – Optional mock keyword/posting API.
- **Persistence**
    - Postgres database for campaign/task metadata.
    - Filesystem for generated images.
- **Logging & Error Handling**
    - Structured JSON logs (campaign_id, task_id, latency, errors).
    - Errors surfaced in Telegram (gracefully).

---

### 2.2 Technology Stack

- **Language:** Python 3.11+
- **Frameworks:** python-telegram-bot
- **Database:** Postgres
- **Models:**
    - Ollama (Mistral/Llama3) for text tasks
    - Stable Diffusion (Automatic1111) for images
- **APIs:** HTTP (requests/httpx)
- **Validation:** Pydantic schemas

---

## 3. Functional Requirements

| ID | Requirement | Component |
| --- | --- | --- |
| FR1 | Accept campaign request via Telegram text | Telegram Gateway |
| FR2 | Decompose request into subtasks | Supervisor |
| FR3 | Generate audience insights (keywords, interests) via Ollama | Audience Agent |
| FR4 | Generate campaign copy (ads, emails, posts) via Ollama | Content Agent |
| FR5 | Generate campaign schedule via Ollama | Scheduler Agent |
| FR6 | Generate 1–2 image creatives via local SD API | Creative Agent |
| FR7 | Store campaign outputs (JSON + images) | SQLite + Filesystem |
| FR8 | Send structured response (summary, copy, images, schedule) back to Telegram | Telegram Gateway |
| FR9 | Support regeneration/refinement (per-tool re-run) | Supervisor + Telegram |
| FR10 | Allow mock external API integration (keywords/posting) | API Connector |

---

## 4. Non-Functional Requirements

- **NFR1:** Must run on a single machine with Docker.
- **NFR2:** End-to-end campaign generation under **60s** (excluding image latency).
- **NFR3:** Supervisor and tools modularized for future microservice migration.
- **NFR4:** System must tolerate model/API failures gracefully (retries, error messages).
- **NFR5:** Logging must capture task outcomes for debugging.

---

## 5. Data Model (Postgres)

**Tables:**

1. **campaigns**
    - id (PK)
    - user_id
    - request_text
    - created_at
2. **tasks**
    - id (PK)
    - campaign_id (FK)
    - tool_name
    - status (pending/success/error)
    - output_json (validated schema)
    - created_at
3. **artifacts**
    - id (PK)
    - task_id (FK)
    - type (text/image)
    - file_path (nullable if text)
    - version (for regeneration history)

---

## 6. JSON Schemas (Contracts)

### Audience Research Output

```json
{
  "audience_profile": {
    "keywords": ["indie hackers", "bootstrapping"],
    "interests": ["SaaS tools", "AI automation"],
    "pain_points": ["time constraints", "growth challenges"]
  }
}

```

### Content Generation Output

```json
{
  "ads": ["Ad copy 1", "Ad copy 2"],
  "emails": ["Email draft 1", "Email draft 2"],
  "social_posts": ["Tweet 1", "LinkedIn post 1"]
}

```

### Schedule Output

```json
{
  "schedule": [
    {"platform": "Twitter", "datetime": "2025-08-25T10:00:00Z", "content_ref": "Tweet 1"},
    {"platform": "Email", "datetime": "2025-08-25T15:00:00Z", "content_ref": "Email draft 1"}
  ]
}

```

### Creative Output

```json
{
  "images": [
    {"prompt": "AI SaaS app targeting indie hackers", "file_path": "campaigns/123/images/img1.png"},
    {"prompt": "AI productivity visual", "file_path": "campaigns/123/images/img2.png"}
  ]
}

```

---

## 7. Sequence Flow (MVP)

1. User sends `/new_campaign "Launch AI SaaS for indie hackers"` in Telegram.
2. Telegram bot forwards request → Supervisor.
3. Supervisor creates campaign record in DB.
4. Supervisor executes tasks sequentially:
    - Audience Agent (Ollama → JSON schema).
    - Content Agent (Ollama → JSON schema).
    - Scheduler Agent (Ollama → JSON schema).
    - Creative Agent (Stable Diffusion API).
5. Outputs stored in DB/filesystem.
6. Supervisor compiles campaign package.
7. Telegram bot sends structured message (summary + copy + images + schedule).
8. User clicks “Regenerate Ads” → Supervisor reruns only Content Agent, updates campaign, returns updated results.

---

## 8. Timeline (Sprint Breakdown)

### Week 1

- **Day 1:** Project scaffold (Postgres + Telegram bot).
- **Day 2:** Ollama client + schema validation.
- **Day 3:** Supervisor orchestration (text tasks only).
- **Day 4:** Audience + Content + Scheduler Agents.
- **Day 5:** Telegram integration (structured text response).

### Week 2

- **Day 6:** Creative Agent (Stable Diffusion).
- **Day 7:** External API connector (mock keyword/posting).
- **Day 8:** Regeneration/refine flow.
- **Day 9:** Persistence polish, logging, error handling.
- **Day 10:** End-to-end demo polish.

---

## 9. Acceptance Criteria

- ✅ User can launch a campaign in Telegram and receive **summary + copy + schedule + creatives**.
- ✅ All LLM jobs handled locally by Ollama.
- ✅ Images generated locally via Stable Diffusion.
- ✅ Campaign artifacts stored in Postgres + filesystem.
- ✅ Regeneration/refinement works.
- ✅ End-to-end flow demo-ready within 2 weeks.