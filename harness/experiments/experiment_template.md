# Experiment Log Template — UNDER CONSTRUCTION

This is a rough template. The experiment loop, matching logic, and handoff from analytics to experiment log still need to be designed properly.

Copy this file for each experiment: `experiments/YYYY-MM-DD-<short-hypothesis>.md`

---

## Experiment metadata

| Field | Value |
|-------|-------|
| **id** | `exp-001` |
| **created_at** | YYYY-MM-DD |
| **status** | proposed / running / completed / cancelled |
| **priority** | 1 (highest) / 2 / 3 |
| **surface** | LinkedIn single image / LinkedIn carousel / Substack / X thread / etc. |
| **primary_metric** | impressions / engagement_rate / clicks / saves / shares / signups |
| **minimum_sample** | e.g., 4 posts per variant |
| **effort** | low / medium / high |
| **expected_impact** | low / medium / high |

---

## Hypothesis

What do we believe, and why?

> Example: On a sub-100-follower LinkedIn page, single-image data-visualization posts with an India-specific hook will reach 3–5× more impressions than text-first posts.

---

## Variants

### Variant A (control / current default)
- Description:
- Example post(s):

### Variant B (test)
- Description:
- Example post(s):

---

## Posts in experiment

| date | variant | post_title / topic | impressions | engagement_rate | clicks | likes | comments | reposts | status |
|------|---------|--------------------|-------------|-----------------|--------|-------|----------|---------|--------|
| ... | A | ... | ... | ... | ... | ... | ... | ... | ... |
| ... | B | ... | ... | ... | ... | ... | ... | ... | ... |

---

## Result

| Field | Value |
|-------|-------|
| **completed_at** | YYYY-MM-DD |
| **winner** | A / B / inconclusive |
| **confidence** | low / medium / high |
| **effect_size** | e.g., +340% impressions |

### Summary

What happened?

### Caveats

What could have distorted the result?

---

## Decision

- [ ] Promote to lesson — write to `AgentMemory`
- [ ] Rerun with larger sample
- [ ] Cancel / reject hypothesis

### Lesson (if approved)

> 1–2 sentence directive for scout/research/write/distribute agents.

### Evidence

> Reference specific posts and metrics.
