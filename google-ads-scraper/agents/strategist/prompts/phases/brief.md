# Final creative brief

Convert the evaluated angles into a machine-readable creative brief.

## Extracted brief

{{ understand_output }}

## Competitive gap

{{ competitive_gap_output }}

## Evaluated angles

{{ evaluate_output }}

## Keyword & demand plan

{{ keyword_plan_output }}

## Competitive intel summary

{{ competitive_intel_summary }}

## Required JSON output

Output **ONLY** valid JSON. No markdown code fences, no commentary.

```json
{
  "campaign": "<short campaign name>",
  "objective": "<campaign objective>",
  "audience": "<primary ICP>",
  "success_metric": "<success metric>",
  "competitive_intel": "<2-3 sentences summarizing crowded angles and ownable gaps>",
  "keyword_data_status": "<provided | provisional>",
  "variants": [
    {
      "id": "v1",
      "angle": "<messaging angle name>",
      "persona": "<ICP>",
      "hook_direction": "<one-line direction for the writer>",
      "cta": "<call to action>",
      "claim_refs": ["Section X.Y", "Safe-to-Claim row"],
      "formats": ["google_rsa", "linkedin"]
    }
  ],
  "keyword_plan": {
    "ad_groups": [
      {
        "name": "<ad group name>",
        "maps_to_variant": "<variant id>",
        "budget_share_pct": <number>,
        "keywords": ["[exact] kw", "\"phrase\" kw"],
        "provisional": <true|false>
      }
    ],
    "negative_themes": ["<theme>"],
    "education_play_angles": ["<angles with zero search demand>"]
  },
  "campaign_settings": {
    "network": "<e.g. Search only — Display OFF>",
    "location": "<geo + presence-only>",
    "language": "<languages>",
    "initial_bidding": "<per playbook sequencing>",
    "daily_budget_inr": <number or null>
  }
}
```

Generate 3–5 variants, one per top angle. Make sure every `claim_refs` entry maps to a real safe-to-claim row from the source of truth.

Rules:
- `keyword_data_status` is "provided" only if real demand data was available in this run; otherwise "provisional".
- If the keyword plan is provisional, every ad group gets `"provisional": true` and keywords are hypotheses, not finals. If demand data was provided, keywords MUST come from that data (volumes visible in it).
- Variants flagged as education plays in the keyword plan stay in `variants` (copy may still be written) but must also appear in `keyword_plan.education_play_angles`.
