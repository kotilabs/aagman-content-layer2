:# Layer 2 Operational Configuration

## Automation depth

**Full gates** — operator approval required at:
1. Signal identifier output (macro + realtime digests)
2. Research artifact completion
3. Each writer output (blog, carousels, thread, infographic concepts)
4. Markets reviewer output
5. SEO/AEO audit output
6. Final approval of all surfaces together

Recommendation: run full gates for the first 2 weeks, then review whether intermediate gates can be dropped.

## Cadence

**Signal-driven** — publish only when signals are strong enough.

No fixed weekly quota. Editorial quality and signal strength determine output, not schedule pressure.

## File conventions

- Signal digests: `signals/{date}-digest.md` (both macro and realtime lenses in one file)
- Operator tickets: `state/tickets/{date}-{signal-id}.md`

## Trigger style

**Explicit chat trigger.** Operator says "run next" (or equivalent) after each approval. The setup agent does not auto-advance on file edits.

## Approval surface

**This chat.** The setup agent shows outputs here; operator approves, requests changes, or rejects inline.

## First test

Run a real current signal end-to-end.

