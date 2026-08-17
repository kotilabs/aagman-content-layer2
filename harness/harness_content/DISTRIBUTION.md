# Distribution Pack — per-platform formatters

Runs AFTER the surfaces (blog / carousel / infographic) are generated. Before
running, ASK THE USER: "surfaces are done — also generate the distribution
pack?" Only run on a yes.

## Inputs (in priority order — source material is truth)

1. the approved blog / research artifact for the signal
2. the carousel or infographic copy if one exists

Fetch and read the source before writing. Every fact in every platform output
comes from the source, never from memory. If the published URL exists (substack
post, X post), capture it — distribution outputs point at it.

## Outputs (one file per platform, saved under the signal's run folder)

| File | Formatter prompt | Platform register |
|---|---|---|
| `*-instagram.txt` | `prompts/distribution_instagram.md` | scroller hook, save-CTA, keywords line |
| `*-linkedin.txt` | `prompts/distribution_linkedin.md` | condensed essay, document pointer |
| `*-substack-note.txt` | `prompts/distribution_substack_note.md` | think-in-public, intellectual |
| `*-x.txt` | `prompts/distribution_x.md` | feed punch, long-form if Premium |
| `*-whatsapp.txt` | `prompts/distribution_whatsapp.md` | fact pointers for an informed crowd |

## Universal rules (every platform)

- no em dashes, no emojis
- no AI tells: no filler openers, no "not X, it's Y", no rhetorical setups,
  no imperative crutches, varied rhythm (stop-slop pass before delivery)
- the hook line earns the click; the ending points at the source writeup by
  previewing what it adds, never a bare "read more"
- never invent a stat; numbers come from the source material only

## Validation

- WhatsApp output MUST pass `harness/harness_agents/whatsapp_formatter_agent.py check <file>`
  (char cap, formatting rules, one raw URL at the end) before delivery.
- Instagram: caption ≤ 2,200 chars, hook lands within the first ~125 chars.
- LinkedIn: ≤ 3,000 chars. X: ≤ 280 chars unless the account has Premium
  long-form (check with the user / post via browser for long-form).

## Presenting to the user

Show each platform output in chat for approval before anything is posted or
scheduled. Posting/scheduling (Buffer for IG/LinkedIn, browser for X long-form,
wa.me link for WhatsApp) happens only on explicit go-ahead.
