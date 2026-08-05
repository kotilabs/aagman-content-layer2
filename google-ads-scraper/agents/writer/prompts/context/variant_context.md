CAMPAIGN:
- Campaign: {{ campaign }}
- Objective: {{ objective }}
- Success metric: {{ success_metric }}

THIS VARIANT:
- ID: {{ variant_id }}
- Angle: {{ angle }}
- Persona: {{ persona }}
- Hook direction: {{ hook_direction }}
- CTA: {{ cta }}

CTA OVERRIDE: If the CTA above contains beta, pricing, card, or legacy-rate language, ignore that language and use a clean action CTA such as "Join the waitlist", "Get early access", "See how it works", or "Build your first backtest".

=== PRODUCT SYNOPSIS ===
{{ product_synopsis }}

=== SAFE CLAIMS FOR THIS VARIANT ===
{{ safe_claims }}

Use ONLY the capabilities listed above as "Yes" or "Partially" in your copy. Do not invent features. "No" rows are forbidden.
{% if competitive_intel %}

COMPETITIVE INTEL
{{ competitive_intel }}
{% endif %}
