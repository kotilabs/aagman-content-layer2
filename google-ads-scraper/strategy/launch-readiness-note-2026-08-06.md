# GCLID & Launch Readiness Note — 2026-08-06

## 1. How GCLID works

GCLID = Google Click ID. The thread that ties a verified signup back to the exact
keyword and ad that produced it.

### The journey of one click

1. **Someone clicks the ad.** Google auto-appends a unique ID to the URL:
   `aagman.ai/?gclid=TeSter-abc123xyz`
   (Auto-tagging is on by default — verify: Google Ads → Account settings → Auto-tagging.)

2. **They land on the page.** The `gclid` parameter is in the URL only at this
   moment. If they navigate around before signing up, it's gone unless stored.

3. **The page saves it.** JS reads `gclid` from the URL, cookies it (90-day), and
   fills a hidden form field:

```html
<input type="hidden" name="gclid" id="gclid-field">
<script>
(function() {
  function getGclid() {
    var fromUrl = new URLSearchParams(window.location.search).get('gclid');
    if (fromUrl) {
      document.cookie = 'gclid=' + fromUrl + '; max-age=7776000; path=/';
      return fromUrl;
    }
    var match = document.cookie.match(/gclid=([^;]+)/);
    return match ? match[1] : '';
  }
  document.getElementById('gclid-field').value = getGclid();
})();
</script>
```

4. **Form submit carries it.** Every lead row in the waitlist store now has
   `email | phone | gclid`.

5. **Lead gets verified.** Double opt-in via email or WhatsApp.

6. **Verified gclids go back to Google** (weekly CSV upload —
   Google Ads → Tools → Conversions → Uploads):

```
GCLID,Conversion Name,Conversion Time,Conversion Value,Conversion Currency
TeSter-abc123xyz,Verified Signup,2026-08-10 14:30:00,,INR
```

7. **Google matches backward.** It now knows which keyword/ad/auction produced a
   VERIFIED signup, not just a form fill.

### Why it's the whole game

- Without GCLID, Google optimizes toward form-fillers (junk), and per-angle CPA
  comparison is meaningless.
- With it: verified CPA per keyword/ad group (the sprint's core learning) AND the
  algorithm learns what a verified signup looks like — which is what makes
  Maximize Conversions / Target CPA safe to switch on later.
- Retrofitting after launch = every lead collected meanwhile is untrackable forever.

### Pre-launch test (mandatory)

1. Click the ad via Google Ads **Ad Preview** (never click the live ad — costs money).
2. Confirm the landing URL contains `?gclid=`.
3. Submit the form yourself.
4. Check the waitlist store — the gclid must be in that row.
5. Upload a test conversion; confirm it appears in Google Ads within ~24h.

---

## 2. What is DONE (committed in repo)

- Strategy & budget split (25/18.75×4, 2-week ₹20K sprint):
  `strategy/keyword-planner-analysis-2026-08-06.md`
- Click estimation model + validation checkpoints:
  `strategy/click-estimation-model-sprint-2026-08-06.md`
- Keywords (34, 5 ad groups, exact+phrase): `strategy/search-campaign-keywords-v2.csv`
- Negatives: `strategy/search-campaign-negatives-v1.md`
- Copy (5 RSAs): `copy/copy-pack-first_google_ads_test_v9.json` / `.md`
- Strategist agent: demand-data gate + PPC playbook knowledge
- Writer agent: all copy rules baked in (no trust fragments as headlines, no
  negative-only framings, no insider vocab, no Hindi-default, any-Indian-language)
- Pipeboard MCP (google-ads + meta-ads) configured and handshake-verified

## 3. What is LEFT (in order)

### A. Landing page (blocker — user's side)
- [ ] GCLID hidden field + cookie storage on the waitlist form (snippet above)
- [ ] Two thank-you states: "Form Submit" vs "Verified Signup"
- [ ] Hero copy fix: "English or Hindi" → "the language you think in"
- [ ] Mobile load check (<3s on mid-range Android/4G)

### B. Google Ads conversion setup (~15 min)
- [ ] Conversion action "Form Submit" (secondary — data only)
- [ ] Conversion action "Verified Signup" (primary — what we optimize for)
- [ ] Test both fire correctly (see test steps above)

### C. Campaign build (via pipeboard google-ads MCP after CLI restart)
- [ ] Campaign + 5 ad groups from `search-campaign-keywords-v2.csv`
- [ ] RSAs from v9 copy pack
- [ ] Negatives from `search-campaign-negatives-v1.md`
- [ ] Settings: Display Network OFF, Search partners OFF, India presence-only,
      English, manual CPC per-cluster starting bids
      (₹1–2 screener / ₹40–60 options / ₹5–10 backtest / ₹20–40 algo / ₹30–50 AI),
      ₹1,430/day total
- [ ] Sitelinks (Backtest / Screener / Docs / Pricing) + callouts
      (SEBI-registered IA, NSE-empanelled, No card required)

### D. Post-launch rituals
- [ ] Day 4: search terms review → junk negatives → day-4 IS check vs. click model
- [ ] Day 7: reallocate screener surplus to best-CTR expensive group;
      swap weak headlines (CTR <2% after 100+ impressions);
      pause keywords with ₹1,000+ spend & zero signups
- [ ] Weekly: GCLID offline conversion upload (verified signups only)
- [ ] Day 14: actuals vs. click model → credit-phase (₹20K Google credit)
      allocation: 70–80% into winning angle(s), 20% continued exploration

---

## Critical path

**Finish the page (A) → restart CLI (pipeboard tools load) → build campaign (C) → launch.**
The landing page is the only blocker between now and a live campaign.
