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

CTA OVERRIDE: If the CTA above contains waitlist, queue, beta, pricing, card, or legacy-rate language, ignore that language. Replace it with a CTA that lets the user DO the thing the variant is about (build, test, describe, approve, deploy) rather than queue for access.

=== PRODUCT SYNOPSIS ===
{{ product_synopsis }}

=== SAFE CLAIMS FOR THIS VARIANT ===
{{ safe_claims }}

Use ONLY the capabilities listed above as "Yes" or "Partially" in your copy. Do not invent features. "No" rows are forbidden.
{% if cross_variant_proof_lines %}

=== TRUST & FRICTION-REMOVAL LINES (use across variants, not as standalone leads) ===
{% for line in cross_variant_proof_lines %}
- {{ line }}
{% endfor %}
{% endif %}
{% if competitive_intel %}

COMPETITIVE INTEL
{{ competitive_intel }}
{% endif %}
