# Keyword & demand plan

Turn the evaluated angles into a concrete keyword/ad-group plan, grounded in demand data.

## Extracted brief

{{ understand_output }}

## Evaluated angles

{{ evaluate_output }}

## Keyword demand data

{{ keyword_data }}

## PPC playbook (excerpt of rules you must follow)

- Keywords are decided from demand data, never product language.
- Search campaigns: exact + phrase match, negatives in week one, Display OFF.
- Budget shares derived from volume × CPC, not split evenly.
- Kill keywords under ~50 monthly searches for short tests.
- An angle with zero search volume is an education play — say so, don't invent keywords.
- Bare generic terms with huge volume are usually navigational for an incumbent — flag, don't chase.
- Nobody searches our internal feature names; searchers use strategy names, tool names, broker names, "free X", "best X india".

## Your task

{% if keyword_data %}
Using the demand data above:

1. **Ad groups.** Cluster the evaluated angles into ad groups mapped to real keyword clusters from the data. One intent theme per ad group.
2. **Keywords.** For each ad group, list keywords with match types ([exact] / "phrase"). Only keywords that appear in the demand data. Include each keyword's monthly volume and bid range from the data.
3. **Budget shares.** Assign a % share to each ad group derived from volume × CPC economics. State the reasoning in one line per group.
4. **Zero-demand angles.** List any evaluated angle with no search demand and mark it "education play — route to video/landing content, not Search."
5. **Negative themes.** List negative keyword themes for the campaign level.
6. **Campaign settings.** Network (Search only, Display OFF), location, language, initial bidding strategy per the playbook's small-budget sequencing.
{% else %}
NO keyword demand data was provided for this run.

You must NOT invent final keyword lists. Instead:

1. **Provisional ad-group plan.** Map the evaluated angles to hypothesized ad groups (structure only — no final keywords).
2. **Research request.** Produce a seed keyword list (~30–50 terms across the angle themes) for the user to run through Google Ads Keyword Planner, plus 2–3 competitor/seed URLs for the "Discover new keywords" feature. Frame it as an explicit ask: "Run this through Keyword Planner (India targeting) and re-run the strategist with the export."
3. **Education-play flags.** Mark any angle you suspect has no search demand (based on the playbook's vendor-speak rules) as provisional-pending-data.
4. Mark the entire keyword plan: **PROVISIONAL — awaiting Keyword Planner data.**
{% endif %}
