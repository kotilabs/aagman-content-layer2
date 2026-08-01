# Analytics Agent — Product Requirements Document

## 1. Overview

The **Analytics Agent** is a data-collection and insight-generation module inside the Layer 2 content harness. It pulls performance data from every publishing surface the brand uses, normalizes it into a single schema, and runs an LLM analyst prompt to surface patterns, lessons, and ranked experiments.

It is designed to answer one question repeatedly: **“What content is working, on which surface, and what should we try next?”**

---

## 2. Goals

1. **Unified measurement.** Bring Buffer (social), Substack (long-form), and eventually GA4 (web) into one normalized dataset so performance can be compared across surfaces.
2. **Automated insight extraction.** Turn raw metrics into actionable, evidence-backed lessons without manual spreadsheet work.
3. **Closed-loop learning.** Feed approved lessons back into the harness memory so downstream agents (scout, research, writer, distributor) do not repeat failed variants and do capitalize on proven patterns.
4. **Experiment scaffolding.** Every analysis outputs a ranked list of falsifiable experiments the operator can run next.

---

## 3. Channel Coverage

| Surface | Status | Input | Metrics |
|---------|--------|-------|---------|
| **LinkedIn** | Live via Buffer MCP | Buffer `list_posts` + `get_aggregated_post_metrics` | impressions, reactions, comments, shares, clicks, engagement rate |
| **X / Twitter** | Live via Buffer MCP | Buffer posts | impressions, likes, retweets, replies, engagement rate |
| **Instagram** | Live via Buffer MCP | Buffer posts | reach, views, likes, comments, shares, saves, follows |
| **Facebook** | Live via Buffer MCP | Buffer posts | reach, reactions, comments, shares |
| **Substack** | Live via CSV export | Posts-export CSV, field-agnostic ingestion | email deliveries, opens, open rate, clicks, click rate, likes, comments, shares, subscriber deltas |
| **Google Analytics 4** | Planned / test harness ready | GA4 Data API via `google-analytics-mcp` | page views, sessions, users, engagement rate, average engagement time, page-level traffic |
| **Direct web / blog** | Planned | GA4 page-path breakdown | same as GA4, mapped to individual blog posts |

**Design principle:** every new channel is normalized into the same `NormalizedPost` schema. The analysis layer does not need to know the original API or CSV shape.

---

## 4. How It Works

### 4.1 High-level flow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Data sources   │────▶│  Normalization   │────▶│  Persist JSON   │
│ Buffer / CSV    │     │  NormalizedPost  │     │  metrics file   │
│ GA4 (planned)   │     │                  │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Memory store   │────▶│  LLM Analyst     │────▶│  Markdown       │
│  past lessons   │     │  analytics_agent │     │  report         │
└─────────────────┘     │  prompt          │     └─────────────────┘
                        └──────────────────┘
```

### 4.2 Components

#### 4.2.1 `BufferMCPClient`
- Speaks JSON-RPC to `https://mcp.buffer.com/mcp`.
- Handles MCP initialize handshake.
- Calls `get_account`, `list_channels`, `list_posts(includeMetrics=true)`, `get_aggregated_post_metrics`.
- Uses only stdlib so it can run standalone.

#### 4.2.2 `SubstackCSVCollector`
- Field-agnostic CSV reader.
- Auto-detects metadata columns (`id`, `title`, `subtitle`, `published_at`, `text`, `url`) by common aliases.
- Ingests **every numeric column** as a metric under its original name.
- Maps common columns to canonical names (`email_deliveries`, `email_opens`, `likes`, etc.) so the prompt can reason consistently.
- Supports an explicit JSON mapping file for non-standard headers.

#### 4.2.3 `CreativeDescriber` (optional)
- Downloads image/video assets from Buffer posts.
- Can describe them with a vision model (`gpt-4o` via litellm) when `OPENAI_API_KEY` is provided and `--describe-assets` is set.
- Falls back to type labels if vision is unavailable.

#### 4.2.4 `AnalyticsCollector`
- Orchestrates Buffer + Substack collection.
- Produces two artifacts per run:
  - `layer2_full_run/analytics/<date>-buffer-raw.json` — raw API/CSV payloads.
  - `layer2_full_run/analytics/<date>-buffer-metrics.json` — normalized, merged posts + aggregates.

#### 4.2.5 `AnalyticsAnalyzer`
- Reads the latest normalized metrics file.
- Recalls prior `content.publish` lessons from `AgentMemory`.
- Builds the prompt from `harness_content/prompts/analytics_agent.md` + context JSON.
- Calls `router.complete("complex_planning", ...)` with domain `content`, step `analytics`.
- Writes `layer2_full_run/analytics/<date>-analysis.md`.

---

## 5. Normalized Schema

Every post becomes a `NormalizedPost`:

| Field | Description |
|-------|-------------|
| `id` | Stable post identifier |
| `title` | First line or headline, max 120 chars |
| `surface` | Canonical surface key: `linkedin`, `twitter`, `instagram`, `facebook`, `substack`, `ga4` |
| `surface_label` | Human label: LinkedIn, X, Instagram, Facebook, Substack, Web |
| `publish_date` | `YYYY-MM-DD` |
| `topic_bucket` | India macro, global macro, policy, earnings, crypto, ai/tech, other |
| `creative_description` | Format label: text-only, single image, carousel, video, short/medium/long newsletter |
| `text` | Post body / newsletter text |
| `link_in_post` | Boolean |
| `link_location` | `body`, `first_comment`, or empty |
| `metrics` | Dict of numeric metrics (surface-specific) |
| `assets` | Downloaded asset records (Buffer only) |
| `asset_descriptions` | One-sentence visual descriptions (optional) |
| `raw` | Original API response or CSV row |

---

## 6. Analysis Output

The LLM analyst produces a markdown report with the following sections:

1. **Executive summary** — pieces analyzed, surfaces, top-level observation.
2. **Performance by surface** — median impressions/engagement per surface.
3. **Performance by topic bucket** — which themes over/under-index.
4. **Patterns (with confidence)** — correlations, outliers, format/topic/hook effects.
5. **Candidate lessons** — actionable directives tagged by role (scout, research, write, distribute) and confidence (low/medium/high).
6. **What we cannot conclude yet** — small samples, confounders, missing data.
7. **Proposed experiments (ranked)** — hypothesis, variant A/B, surface, primary metric, min sample, effort, expected impact.

---

## 7. Configuration

Set in the repo `.env`:

```bash
# Buffer (required for social data)
BUFFER_MCP_TOKEN=
BUFFER_ORGANIZATION_ID=          # optional; auto-detected
BUFFER_CHANNEL_IDS=              # optional; defaults to all connected channels

# Substack CSV (optional)
SUBSTACK_CSV_PATH=
SUBSTACK_CSV_MAPPING=            # optional JSON mapping file

# Vision descriptions (optional)
OPENAI_API_KEY=

# GA4 MCP (planned)
GOOGLE_APPLICATION_CREDENTIALS=
GOOGLE_CLOUD_PROJECT=
GA_PROPERTY_ID=
```

CLI invocation:

```bash
python harness/run_layer2_full.py analytics --analytics-days 30
python harness/run_layer2_full.py analytics --substack-csv /path/to/substack.csv
python harness/run_layer2_full.py analytics --describe-assets
```

---

## 8. Key Features

| Feature | Status | Notes |
|---------|--------|-------|
| Buffer social collection | ✅ Live | All connected channels |
| Substack CSV ingestion | ✅ Live | Field-agnostic, mapping config supported |
| Asset download | ✅ Live | Images/videos saved locally |
| Vision asset descriptions | ✅ Live | Optional, requires OpenAI key |
| Cross-surface normalization | ✅ Live | Single schema |
| LLM-generated analysis report | ✅ Live | Markdown output |
| Memory recall of past lessons | ✅ Live | Avoids contradicting stored lessons |
| Conversational analytics | ✅ Live | REPL over latest metrics; natural-language Q&A |
| GA4 MCP connection | 🧪 Test harness | `harness/test_ga_mcp.py` ready |
| Experiment knowledge base | 📋 Planned | Queryable KB of experiments and results |
| Autonomous experiment agent | 📋 Planned | Posts variants, observes, writes lessons |
| Random writer agent | 📋 Planned | One-shot idea → publish-ready package |

---

## 9. Success Metrics

1. **Coverage:** Every published post in the lookback window appears in the report.
2. **Latency:** Full collection + analysis completes in under 5 minutes for a 30-day window.
3. **Insight quality:** Each report contains at least one lesson the operator agrees is actionable.
4. **Experiment velocity:** At least one ranked experiment is run per week based on the report.
5. **Memory closure:** Proven lessons are written back to `AgentMemory` and referenced by downstream agents.

---

## 10. Future Work

1. **GA4 integration:** Pull web/blog traffic per page path and merge into the normalized dataset.
2. **Experiment knowledge base:** Structured store of hypotheses, variants, surfaces, sample sizes, results, and confidence.
3. **Autonomous experiment agent:** Read open experiment log → design next variant → publish → observe → write lesson.
4. **Image-assessment model:** Evaluate creatives on chart readability, headline prominence, data-to-noise ratio.
5. **Random writer agent:** Single-entry creative agent that takes an idea and calls downstream agents automatically.

---

## 11. Open Questions

1. Should GA4 data be merged per page path as a `NormalizedPost` with `surface=web`, or kept as a separate web-traffic section?
2. Should the experiment knowledge base be a separate SQLite DB, a JSON file, or reuse the existing `AgentMemory` store?
3. What is the minimum sample size threshold before a lesson is automatically written to memory?
