# WhatsApp formatter

Turn the signal's source material into a WhatsApp message for an informed crowd
(group forwards, finance-literate readers).

- purely fact-led. no hook theatrics, no rhetorical questions, no slogan
  closers, no marketing language. the reader forwards credibility, not copy
- pointer structure: one-line context / "the numbers:" bullets / the mechanism
  or "why X:" bullets, one step per bullet / the single takeaway line / a
  closing that previews what the full writeup adds ("the full piece gets into
  what doesn't fit here: ..."), then the raw URL on the last line
- *bold* with single asterisks only, on the key numbers
- no emojis, no em dashes, no markdown headers or links, no tables, no arrows
  (→ is flagged as emoji-range by the validator)
- lowercase, ≤ 1,200 chars, at most one URL at the end
- MUST pass: python3 harness/harness_agents/whatsapp_formatter_agent.py check <file>
- generate the share link with: ... whatsapp_formatter_agent.py link <file>
