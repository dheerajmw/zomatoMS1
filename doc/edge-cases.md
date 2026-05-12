# Edge Cases Catalog (Detailed)

This document lists **edge cases and failure modes** for the AI-powered restaurant recommendation system described in [problemStratement.md](./problemStratement.md) and phased in [phase-wise-architecture.md](./phase-wise-architecture.md). It is written for **design reviews, implementation checklists, and QA**.

---

## How to read this document

| Column / section | Meaning |
|------------------|---------|
| **Severity** | **P0** — wrong data or security; **P1** — broken core path; **P2** — degraded UX; **P3** — polish / rare |
| **Trigger** | What provokes the case |
| **Expected behavior** | Product + engineering outcome |
| **Phase** | Primary handling location in [phase-wise-architecture.md](./phase-wise-architecture.md) |
| **Acceptance criteria** | Testable bullets |
| **Example** | Concrete scenario where helpful |

Full architecture contracts (DTOs, sequence, token budgets) live in [phase-wise-architecture.md](./phase-wise-architecture.md) §§5–15.

---

## 1. Data plane (ingestion, schema, store) — Phase 1

| ID | Edge case | Severity | Trigger | Expected behavior | Phase |
|----|-----------|----------|---------|-------------------|-------|
| D1 | Dataset unavailable | P1 | Hugging Face down, TLS error, revoked revision | Fail with clear error; if local cache allowed, document freshness rules and log `dataset_revision` | 1 |
| D2 | Empty dataset | P1 | Zero rows after load | No LLM call; API returns `NO_MATCHES` / empty with message pointing to data config | 1 |
| D3 | Duplicate logical keys | P2 | Same name+location many times | Stable surrogate `id`; merge and filter never use name alone | 1 |
| D4 | Missing required fields | P1 | Null `name`, missing `rating` or `cost` | Document policy: drop row vs impute; rows excluded from filters must not appear in output | 1 |
| D5 | Malformed types | P2 | `"4.2★"`, non-numeric cost | Coerce or null; same as D4 downstream | 1 |
| D6 | Rating scale mismatch | P1 | Dataset 0–5 vs UI 0–10 | Single mapping in config; reject impossible `min_rating` at validation | 1, 2 |
| D7 | Cuisine encoding | P2 | Comma string vs array | Normalize to `string[]`, trim, case policy documented | 1 |
| D8 | Location ambiguity | P2 | Bengaluru vs Bangalore | Alias table or strict “unknown city” path | 1, 2 |
| D9 | Oversized text blobs | P3 | Multi-KB descriptions | Truncate for LLM payload; full text never required for filter | 1, 3, 4 |
| D10 | Stale cache | P2 | Cached Parquet older than hub | TTL or pinned revision; warn in logs / response `messages[]` | 1 |

### 1.1 Detailed notes — D1 / D2 (data availability)

**Example (D1):** Startup calls HF; receives HTTP 503. **Behavior:** process exits non-zero *or* health endpoint reports `data_ready=false` until cache path succeeds—pick one and document. **Acceptance:** No route returns 200 with fabricated restaurants.

**Example (D2):** ETL drops all rows due to strict validation. **Acceptance:** `load_restaurants()` fails fast; integration test asserts no empty silent success.

### 1.2 Detailed notes — D3 / D4 (identity and quality)

**D3 Example:** Three rows named “Cafe M” in Indiranagar. **Acceptance:** Three distinct `id`s; filter returns correct three or subset; LLM cannot collapse them without ids.

**D4 Example:** Row has `rating: null`. **Acceptance:** If policy is “exclude when `min_rating` set,” then `match_count` excludes that row; if policy is “treat as 0,” document and add test that user sees low-rated venue only when min_rating allows.

---

## 2. User preferences (input, validation, vocabulary) — Phase 2

| ID | Edge case | Severity | Trigger | Expected behavior | Phase |
|----|-----------|----------|---------|-------------------|-------|
| U1 | All fields empty / defaults | P2 | Blank submit | 400 or explicit “wide search” mode; never ambiguous implicit filters | 2 |
| U2 | Impossible combination | P2 | `min_rating` above dataset max | 400 or 200 empty with human-readable reason | 2 |
| U3 | Unknown city | P2 | `location: "Zzyzx"` | 400 with allowed samples, or empty with “not in catalog” | 2 |
| U4 | Budget label mismatch | P1 | UI sends token not in map | 400 `VALIDATION_ERROR`; never silent zero results | 2 |
| U5 | Multiple cuisines semantics | P2 | User selects Italian + Chinese | Document OR vs AND; same behavior in filter and in prompt restatement | 2, 3 |
| U6 | Free-text overflow | P3 | Notes 10k chars | 400 or truncate + log | 2 |
| U7 | Injection / abuse in free text | P0 | “Ignore previous instructions…” | Length cap; system prompt; no tool execution from notes; notes only in delimited user section | 2, 4 |
| U8 | Minimum rating boundary | P2 | `min_rating` equals row rating | Inclusive `>=` everywhere; unit test at boundary | 2, 3 |
| U9 | Conflicting soft preferences | P3 | “quiet” + “loud party” | Optional UI warning; LLM may mention trade-off; hard filters unchanged | 2, 4 |

### 2.1 Detailed notes — U4 / U3 (vocabulary)

**Example (U4):** Request `budget: "HIGH"` but map only has `low|medium|high`. **Acceptance:** Normalize case **or** return 400 with `allowed: ["low","medium","high"]`.

**Example (U3):** City valid in real world but absent in dataset. **Acceptance:** User sees message that catalog has no rows for that label; no LLM hallucination of city-specific venues.

### 2.2 Detailed notes — U7 (prompt injection)

**Acceptance:** Red-team fixture: notes contain instruction to reveal system prompt. **Expected:** Model may still misbehave, but **no** secret keys in prompts; **no** server-side execution of user text; logs do not store full prompts if they contain PII policy—your choice, but document.

---

## 3. Filtering and candidate selection — Phase 3

| ID | Edge case | Severity | Trigger | Expected behavior | Phase |
|----|-----------|----------|---------|-------------------|-------|
| F1 | **No matches** | P1 | Over-constrained filters | 200 empty + suggestions (relax rating, cuisine, area); optional diagnostics `match_count: 0` | 3, 5 |
| F2 | **Too many matches** | P2 | Thousands pass | Pre-rank cap to *K*; response shows `match_count` vs `capped_to` (see architecture §6) | 3 |
| F3 | Cuisine partial match | P2 | “Chinese” vs “Indo-Chinese” | Document token/substring rules; add regression tests | 3 |
| F4 | Missing filter field on row | P1 | No `cost_band` when budget set | Exclude or “unknown” policy—must be consistent and documented | 3 |
| F5 | Tie on pre-rank | P3 | Identical rating/cost | Stable secondary sort by `id` | 3 |
| F6 | Soft keyword filter | P3 | No description column | Skip keyword step; no error | 3 |
| F7 | Only one candidate | P3 | Single row | LLM optional per cost policy; if skipped, template explanation | 3, 4 |
| F8 | Token budget exceeded | P1 | *K* compact rows still too large | Reduce *K* or strip `description`; log `sent_to_llm` | 3, 4 |

### 3.1 Detailed notes — F1 (no matches)

**Example:** Bangalore + Italian + `min_rating: 4.8` yields 0 rows. **Acceptance:** Response includes `results: []`, `match_count: 0`, and `messages` such as “Try lowering minimum rating or adding cuisines.” No call to LLM with empty candidates (saves cost and avoids nonsense).

### 3.2 Detailed notes — F2 / F8 (scale)

**Example:** 8,000 matches. **Acceptance:** `capped_to` = 25 (config), `sent_to_llm` ≤ 25; p95 filter time within budget per architecture §8.

---

## 4. LLM integration (prompt, API, grounding) — Phase 4

| ID | Edge case | Severity | Trigger | Expected behavior | Phase |
|----|-----------|----------|---------|-------------------|-------|
| L1 | LLM timeout / 5xx | P1 | Slow provider | Backoff retries then **degraded** deterministic ranking + placeholder explanation | 4, 6 |
| L2 | Rate limit / quota | P2 | HTTP 429 | Backoff; user-facing “try again”; optional queue | 4, 6 |
| L3 | Invalid JSON / schema drift | P1 | Prose or wrong keys | One repair retry; then fallback like L1 | 4 |
| L4 | **Hallucinated restaurant** | P0 | id not in candidate set | Grounding guard drops id; order from valid ids only | 4 |
| L5 | Duplicate IDs in output | P2 | Same id twice | Deduplicate; single explanation (merge or first wins) | 4 |
| L6 | Partial coverage | P2 | Fewer explanations than `limit` | Template for gaps or return fewer items with honesty | 4, 5 |
| L7 | Contradictory explanation | P1 | Text conflicts with store facts | Strip bad explanation or show facts-only | 4, 5 |
| L8 | Empty LLM content | P2 | Zero tokens usable | Fallback path | 4 |
| L9 | Non-determinism | P3 | Different order same input | Log model + temperature; optional seed | 6 |
| L10 | Prompt leakage attempts | P1 | Jailbreak strings | No change to grounding rules; output still validated | 4 |

### 4.1 Detailed notes — L4 (grounding)

**Example:** Model returns `ordered_ids: ["r_999", "r_1"]` but `r_999` ∉ candidates. **Acceptance:** Response contains only `r_1` from LLM order then remaining ids appended per policy; **no** `r_999` in JSON; metric `orphan_ids_dropped` increment in logs.

### 4.2 Detailed notes — L1 / L3 (degradation)

**Acceptance:** When LLM fails, HTTP 200 with `degraded: true`, explanations like “Automatic summary unavailable.” Rank matches deterministic pre-rank. UI shows badge.

---

## 5. Merge, response DTO, and presentation — Phase 5

| ID | Edge case | Severity | Trigger | Expected behavior | Phase |
|----|-----------|----------|---------|-------------------|-------|
| M1 | Stale id after reload | P2 | Data refresh mid-request | Merge uses snapshot from request; missing id omitted + log | 3, 5 |
| M2 | Partial display fields | P3 | Missing cuisine | Placeholder “—”; never fabricate | 5 |
| M3 | Long explanation | P3 | Paragraph | Truncate UI; tighten prompt max tokens | 4, 5 |
| M4 | XSS / special chars | P0 | `<script>` in name | Escape in HTML; JSON for API | 5 |
| M5 | Zero rows after merge | P1 | All ids invalid | Same as F1 empty state | 5 |
| M6 | Stale async response | P2 | User edits filters during fetch | Client ignores stale `request_id` or aborts fetch | 5 |

### 5.1 Detailed notes — M6 (client)

**Acceptance:** UI test: rapid double-submit; only latest `request_id` updates state.

---

## 6. Foundations, operations, and hardening — Phases 0 & 6

| ID | Edge case | Severity | Trigger | Expected behavior | Phase |
|----|-----------|----------|---------|-------------------|-------|
| O1 | Missing API key | P1 | Env unset | Fail startup for LLM mode or `degraded_only` filter mode | 0 |
| O2 | Trace gaps | P2 | Cannot debug bad rank | All logs include `request_id`, template version | 6 |
| O3 | Load spike | P2 | Many concurrent users | Rate limit + LLM concurrency cap | 0, 6 |
| O4 | Abuse / batch hammer | P2 | Scripted traffic | 429 / auth | 6 |

---

## 7. Cross-reference: problem statement success criteria

| Success criterion ([problemStratement.md](./problemStratement.md)) | Edge cases that exercise it |
|------------------------------------------------------------------|-----------------------------|
| End-to-end path dataset → filters → LLM → UI | D2, F1, L1, M5 |
| Recommendations traceable to filtered rows | L4, M1, D3 |
| Documented prompting / reproducibility | L9, O2 |
| Robustness: **no matches**, **too many matches**, **missing fields** | F1, F2, F4, D4 |

---

## 8. End-to-end scenarios (walkthroughs)

### 8.1 Happy path

User sends valid prefs → 200 rows match → cap 25 → LLM returns valid JSON → merge → 5 cards with explanations. **Checks:** `degraded: false`, `orphan_ids_dropped == 0`.

### 8.2 No matches (F1)

**Given** no row satisfies cuisine+location. **Then** `results: []`, `match_count: 0`, no LLM cost, helpful `messages`.

### 8.3 LLM down (L1)

**Given** provider 503 after retries. **Then** `degraded: true`, results ordered by pre-rank, placeholder explanations, `llm_retry_count` in logs.

### 8.4 Hallucinated id (L4)

**Given** mock LLM returns bad id. **Then** output ids ⊆ candidate ids; monitoring sees drop count ≥ 1.

---

## 9. Test matrix (expanded)

| Test ID | Edge ref | Intent | Key assertion |
|---------|----------|--------|-----------------|
| T-F1 | F1 | Zero matches | Empty results; no LLM invocation (mock spy) |
| T-F2 | F2 | Many matches | `match_count` large; `sent_to_llm` ≤ K |
| T-F4 | F4 | Missing cost | Row excluded when budget filter on |
| T-L4 | L4 | Bad id | Response ids subset of candidates |
| T-L1 | L1 | Provider error | `degraded: true`; order preserved |
| T-L3 | L3 | Bad JSON | Retry then fallback |
| T-U4 | U4 | Bad budget | HTTP 400 |
| T-U8 | U8 | Boundary rating | Row with rating == min included per policy |
| T-M4 | M4 | XSS name | Rendered escaped in HTML harness |
| T-M6 | M6 | Stale client | Only latest response applied (client test) |
| T-D1 | D1 | HF down | Clear failure / health red |

---

## 10. Severity summary (backlog triage)

| Severity | Count (approx) | Action |
|----------|----------------|--------|
| P0 | U7, L4, M4 | Block release until covered |
| P1 | D1, D2, D4, D6, U4, F1, F8, L1, L3, L7, M5, O1 | Core MVP hardening |
| P2 | Most others | Sprint n+1 |
| P3 | U6, F5, F6, F7, L9, M2, M3 | Polish |

---

## 11. Document map

| Artifact | Role |
|----------|------|
| [problemStratement.md](./problemStratement.md) | Product workflow and success criteria |
| [phase-wise-architecture.md](./phase-wise-architecture.md) | Phases, DTOs, sequence, budgets, prompts |
| **edge-cases.md** (this file) | Severity, examples, acceptance, test matrix |
