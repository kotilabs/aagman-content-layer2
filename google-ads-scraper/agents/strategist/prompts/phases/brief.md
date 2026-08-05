# Final creative brief

Convert the evaluated angles into a machine-readable creative brief.

## Extracted brief

{{ understand_output }}

## Competitive gap

{{ competitive_gap_output }}

## Evaluated angles

{{ evaluate_output }}

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
  ]
}
```

Generate 3–5 variants, one per top angle. Make sure every `claim_refs` entry maps to a real safe-to-claim row from the source of truth.
