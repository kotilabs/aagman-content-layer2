# āagman × Reddit Ads — Consolidated Research Playbook

**Date:** 2026-08-07 · **Owner:** founder-led paid experiments · **Status:** working doc, launch-ready
**For:** āagman — AI trading platform for Indian retail traders. SEBI-registered IA, NSE-empanelled algo provider. Target: Indian F&O/options traders + systematic retail investors.

**Evidence tags:** `[OFFICIAL]` Reddit's own docs/policy · `[PRACTITIONER]` agencies/experts with managed spend · `[ANECDOTAL]` redditor first-person claims · `[REGULATORY]` SEBI/legal. ⚠️ = contested or single-source.

---

## 1. How Reddit ads work (official mechanics, condensed) `[OFFICIAL]`

**Campaign structure:** Campaign → Ad groups → Ads. Budgets are set at the **ad-group level** (daily or lifetime); an optional campaign-level lifetime spend cap exists.

**Objectives (7):**
- Brand awareness & reach — CPM
- Traffic — CPC
- Conversions — oCPM lowest-cost or CPC cost-cap; note: no free-form post type on this objective
- Video views — CPV
- App installs — oCPM/CPC; separate ad groups per OS
- Catalog sales — CPC; needs a catalog
- Lead generation (beta) — CPC, on-Reddit forms

**Auction & billing:** real-time second-price-style auction (pay slightly above next bidder). Automated strategies are **lowest-cost and cost-cap only — no target-ROAS**. Manual bidding available. Billable actions count within 2h of placement. Ad groups may **overspend budgets up to 20%**; budget changes take up to 60 min to apply.

**Formats:** image, video, carousel (2–6 cards), free-form rich text (up to 20 images / 5 videos / 40k chars). Headline max 300 chars (recommend ≤100). Placements = **Feed + Conversation** (inside comment threads). Comments can be enabled per ad. ~20 standard CTA buttons.

**Targeting:** interest (IAB), community (subreddit visits/subscribes in last 28 days — not just members), keyword (English only), custom audiences (pixel/CAPI retargeting, customer lists, lookalikes, engagement retargeting 6 months), location/gender/language/device. **Device targeting is immutable after ad-group creation.** Interest/community/keyword combine with **OR** logic (they expand, not narrow); they combine **AND** vs custom audiences and geo.

**Review:** human review, typically ~1 day — submit ≥48h before start. Edits to copy/URL/creative/targeting trigger re-review. Finance/healthcare may need certifications.

**Measurement:** Reddit Pixel (JS/GTM/Shopify) + Conversions API (server-to-server, events within 7 days, dedupe required if both used). Click ID in URL recommended for attribution.

**Vs Google/Meta reflexes:** no target-ROAS, no granular self-serve frequency caps, budgets at ad group, targeting OR-logic, and community targeting reaches 28-day *visitors*, not just subscribers.

---

## 2. What practitioners say works `[PRACTITIONER]`

**Platform context.** Reddit ad revenue $2.1B in 2025 (+74% YoY); eCPM $2.29 vs Meta $11.73; CPC ~$0.59 vs Meta $1.33, Google $4–5. Consensus: structurally underpriced, arbitrage window ~12–24 months. [Shnoco stats](https://www.shno.co/marketing-statistics/reddit-ads-statistics), [Bunny Honey Club](https://blog.bunnyhoneyclub.com/posts/reddit-ads-small-business-2026). India: ~58.9–64.1M monthly unique visitors (Dec 2024). [Shnoco](https://www.shno.co/marketing-statistics/reddit-ads-statistics)

**Campaign structure — the #1 lever is community targeting.**
- Interest targeting underperforms community targeting **2–4x on CTR**; 1.8x per daily.dev. [Bunny Honey](https://blog.bunnyhoneyclub.com/posts/reddit-ads-small-business-2026), [daily.dev](https://business.daily.dev/resources/reddit-ads-for-developer-tools-subreddits-targeting-creative-convert/)
- Cluster size: **3–8 subreddits per ad group**. Subs of 5K–50K members often deliver lowest CPAs; a 20K exact-fit sub can beat a 2M sub 5–10x on CVR. Don't trust "low forecast" warnings. [Stackmatix](https://www.stackmatix.com/blog/are-reddit-ads-worth-it). ⚠️ Contested by InterTeam's Cole Furrh: intent of the community matters more than size. [InterTeam AMA](https://www.interteammarketing.com/blog/reddit-ads-faqs-from-ama)
- Keep community, keyword, and interest targeting in **separate ad groups**. Recommended 2026 structure: 1 campaign → 3 ad groups (broad interest / subreddit / retargeting), 3–5 creatives each. [Stackmatix](https://www.stackmatix.com/blog/are-reddit-ads-worth-it)
- **Expansion targeting OFF for the first 2–4 weeks**; enable only after baseline CPA is known; if CPA rises >30%, disable. [Stackmatix](https://www.stackmatix.com/blog/are-reddit-ads-worth-it)
- Design creative **per subreddit cluster**, not one generic ad. [Bunny Honey](https://blog.bunnyhoneyclub.com/posts/reddit-ads-small-business-2026)
- Finding subs (InterTeam, 3 methods): (1) Ads Manager community search/suggestions; (2) Google your highest-intent keyword + "reddit", target the subs that dominate results; (3) retarget first, then target cold the communities your converters come from. [InterTeam AMA](https://www.interteammarketing.com/blog/reddit-ads-faqs-from-ama)
- Scale in ~20% budget increments; jumping $50→$500/day typically raises CPA 2–3x and resets learning. [Stackmatix](https://www.stackmatix.com/blog/are-reddit-ads-worth-it)

**Placements.** Conversation placement outperforms Feed on intent/conversion (InterTeam: "significantly higher conversion rates"; daily.dev: 0.41% CTR, 2.1x home-feed), but Feed has the reach. Reddit's own test: feed+conversation together ≈12% lower CPA. Build creative differently per placement — Conversation ads render tiny; text in images becomes unreadable. [InterTeam](https://www.interteammarketing.com/blog/reddit-ads-best-practices), [daily.dev](https://business.daily.dev/resources/reddit-ads-for-developer-tools-subreddits-targeting-creative-convert/), [Foundation Inc](https://foundationinc.co/lab/reddit-paid-marketing)

**Creative that survives Reddit.**
- Core law: polish = inauthenticity. Test = "would a user upvote this?" [Stackmatix creative guide](https://www.stackmatix.com/blog/reddit-ads-creative-best-practices)
- Text/free-form ads written like a user comment: 2–3x better CTR than brand-voice. Lead with the problem, not the product. Screenshot-style visuals beat stock. Reference the subreddit in copy. [Bunny Honey](https://blog.bunnyhoneyclub.com/posts/reddit-ads-small-business-2026), [Stackmatix](https://www.stackmatix.com/blog/reddit-ads-creative-best-practices), [daily.dev](https://business.daily.dev/resources/reddit-ads-for-developer-tools-subreddits-targeting-creative-convert/)
- Worked example: product-announcement style → 0.3% CTR, $3.20 CPC, net-negative votes; data-insight style ("We scanned 2,000 Docker images…") → 1.8% CTR, $0.90 CPC, 87 upvotes, 23 genuine comments. [Stackmatix](https://www.stackmatix.com/blog/reddit-promoted-posts-best-practices)
- Kills: marketing buzzwords, press-release tone, repurposed Meta/Google creative (2–4x worse), pushy CTAs. Soft CTAs ("Read the docs", "Try free") beat "Book a demo" cold. [Stackmatix](https://www.stackmatix.com/blog/are-reddit-ads-worth-it), [InterTeam](https://www.interteammarketing.com/blog/reddit-ads-best-practices)
- Headlines 80–150 chars (InterTeam); Reddit official: short copy, name the brand, clear CTA. [InterTeam](https://www.interteammarketing.com/blog/reddit-ads-best-practices), [Reddit Creative Best Practices](https://business.reddithelp.com/s/article/Creative-Best-Practices) `[OFFICIAL]`
- Formats: carousels best-converting (esp. Conversation); video most volatile, often underwhelms; free-form holds attention 41s avg vs 9s image; official free-form tip: open with a TL;DR. [InterTeam AMA](https://www.interteammarketing.com/blog/reddit-ads-faqs-from-ama), [daily.dev](https://business.daily.dev/resources/reddit-ads-for-developer-tools-subreddits-targeting-creative-convert/), [Reddit Free-form Ads](https://business.reddithelp.com/s/article/Free-form-Ads) `[OFFICIAL]`
- Brand profile hygiene: branded username, logo avatar, bio, pinned CTA post — users click through to check. [InterTeam](https://www.interteammarketing.com/blog/reddit-ads-best-practices)

**Comments on vs off — 2025–26 consensus: ON, actively managed.**
- Managed comments: +25–35% CTR; unanswered negativity: CTR drops 40–60% within 48h. Reply within ~2h in the first 4–6h; never engage trolls; hide abusive comments. Pin a brand reply pre-empting objections. [Stackmatix](https://www.stackmatix.com/blog/are-reddit-ads-worth-it), [daily.dev](https://business.daily.dev/resources/reddit-ads-for-developer-tools-subreddits-targeting-creative-convert/)
- ⚠️ Counter: some operators disable comments and succeed (older advice, pre-2025). [MarTech 2021](https://martech.org/is-it-time-to-pay-more-attention-to-reddit-for-advertisers-focused-on-niche-audiences-the-answer-is-yes/) `[ANECDOTAL]`
- ⚠️ Claims that disabled comments = negative auction signal and that downvotes raise CPCs are practitioner-asserted (daily.dev, Stackmatix), not confirmed in official docs.

**Frequency & fatigue.** Small subreddit audiences saturate fast: swap creative every 2–3 weeks (30–50% monthly decay on stale ads); daily.dev says 7–14 days. No Meta-style self-serve frequency caps — manage via rotation, exclusions, and the Frequency metric. Since March 2025, users can hide all ads from an advertiser for a year+ — annoyance has account-level consequences. [Stackmatix](https://www.stackmatix.com/blog/are-reddit-ads-worth-it), [daily.dev](https://business.daily.dev/resources/reddit-ads-for-developer-tools-subreddits-targeting-creative-convert/), [PPC Land](https://ppc.land/reddits-frequency-cap-restrictions-a-persistent-hurdle-for-small-advertisers-2/), [Marketing-Interactive](https://www.marketing-interactive.com/reddit-to-let-users-hide-ads-from-specific-advertisers)

**Benchmarks (2025–26, USD, US/EU-weighted).**
- Platform: CPM $2–6 consumer / $4–8 financial services; CPC $0.10–0.80 consumer, $0.50–2.00 narrow; CTR 0.2–0.3% baseline, 0.5–1.0% high-interest. [AdBacklog](https://adbacklog.com/blog/reddit-ads-benchmarks-per-industry-2025)
- Finance vertical: CTR 0.2–0.4%; CPC $0.50–1.00; CPM $4–8; signup CPA $10–30; CPL $40–100 typical. Real campaign row: finance newsletter via r/investing + r/stockmarket — CPC $0.78, CPM $6.10, CPA $11.50. [AdBacklog](https://adbacklog.com/blog/reddit-ads-benchmarks-per-industry-2025), [Stackmatix](https://www.stackmatix.com/blog/reddit-ads-benchmarks-cost-per-click), [Web Tonic](https://www.webtonic.io/blog/fintech-reddit-ads-statistics)
- Finance is ~19% of Reddit ad revenue (#2 vertical) and its most expensive interest category — yet 3–10x cheaper than LinkedIn/Google finance CPCs. [Web Tonic](https://www.webtonic.io/blog/fintech-reddit-ads-statistics), [AdControlCenter](https://www.adcontrolcenter.com/learn/reddit-ads-cost-benchmarks-q2-2026)

**Budgets & learning phase.**
- Official minimums: $5/day per ad group; learning phase needs ~50 conversion events/week per ad group; 14 days of stability after creation or major edits. `[OFFICIAL-derived]` [Stackmatix](https://www.stackmatix.com/blog/reddit-ads-minimum-spend), [Reddit help](https://business.reddithelp.com/s/article/app-event-optimization)
- Practical minimums: $5/day "guarantees you learn nothing" — start $50–150/day for 7 days; meaningful test $500–2,000 over 7–14 days; fintech $2,000–5,000/month for 4–6 weeks. Daily budget ≥ 10x target CPA. Time-to-truth: 6 weeks, not 2. [Stackmatix](https://www.stackmatix.com/blog/reddit-ads-minimum-spend), [Bunny Honey](https://blog.bunnyhoneyclub.com/posts/reddit-ads-small-business-2026), [Web Tonic](https://www.webtonic.io/blog/fintech-reddit-ads-statistics)

**Bidding & measurement.**
- Start Lowest Cost; add cost caps only after ~15–50 conversions. Attribution: optimize on 7d-click/1d-view, judge on 28d-click/7d-view — switching view-through 1d→7d reveals 30–40% more conversions. [InterTeam](https://www.interteammarketing.com/blog/reddit-ads-best-practices), [Stackmatix](https://www.stackmatix.com/blog/are-reddit-ads-worth-it)
- Desktop targeting skews higher-intent with less bot traffic (but Reddit is 70–85% mobile — a filter, not a default). [InterTeam AMA](https://www.interteammarketing.com/blog/reddit-ads-faqs-from-ama)
- Retargeting pays disproportionately: 63% lower cost per signup, 77% lower CPL in one case; tiered 7/15/30/60/90-day windows, exclude converters. Lookalikes need 50K–100K seeds — skip early. [InterTeam](https://www.interteammarketing.com/blog/reddit-ads-best-practices), [daily.dev](https://business.daily.dev/resources/reddit-ads-for-developer-tools-subreddits-targeting-creative-convert/)
- Reddit is a research channel: avg click-to-conversion delay 5.4 days; finance products 14–45 days. Last-click under-credits Reddit 30–50%. Wire Pixel + CAPI + UTMs + Enhanced Conversions + "how did you hear about us" before spending. [daily.dev](https://business.daily.dev/resources/reddit-ads-for-developer-tools-subreddits-targeting-creative-convert/), [Stackmatix finance](https://www.stackmatix.com/blog/reddit-ads-for-finance), [Bunny Honey](https://blog.bunnyhoneyclub.com/posts/reddit-ads-small-business-2026)

**Top mistakes:** repurposed Meta/Google creative; interest instead of community targeting; expansion ON from day 1; ignoring/disabling comments; clicks to a generic homepage; judging <2 weeks on last-click; too many bid caps; no creative rotation; scaling too fast; zero-history brand account; enabling Reddit MAX before clean conversion data. [Stackmatix](https://www.stackmatix.com/blog/are-reddit-ads-worth-it), [Bunny Honey](https://blog.bunnyhoneyclub.com/posts/reddit-ads-small-business-2026), [InterTeam](https://www.interteammarketing.com/blog/reddit-ads-best-practices), [WOLF Financial](https://wolf.financial/blog/reddit-advertising-fintech-community-strategy)

---

## 3. What redditors themselves say (war stories) `[ANECDOTAL unless noted]`

Method note: threads located via the Arctic Shift Reddit archive; dates mostly 2025-11 → 2026-07.

**Headline sentiment: deep skepticism, narrow "works if…" minority.**
- "Reddit ads are trash, reddit users are notoriously anti ads, treat it as top of the funnel" (r/PPC, score 23, 2026-07). https://reddit.com/r/PPC/comments/1v7anmf/is_reddit_ads_worth_it_in_2026/
- "Near universal opinion Reddit Ads are a complete waste of money… 80%+ bot clicks" (r/marketing, score 19). https://reddit.com/r/marketing/comments/1qnczsl/issues_with_reddit_ads/
- The consistent minority pattern: niche products, SaaS/dev tools/gaming/**finance**, community targeting, native creative, retargeting, patience. "Probably the best value in terms of cost per click… particular success with retargeting and high intent communities." (SaaS PPC specialist) https://reddit.com/r/PPC/comments/1jpf3e4/best_ad_platforms_for_saas/ `[PRACTITIONER]`

**The bot-traffic war (biggest controversy).**
- Self-described bot-detection pro spent $400 and measured **80.7% bot traffic**; his cross-platform reads: Google 14.3%, Facebook 39.7%, normal ≈10%. Traffic-goal campaigns were worse than CPC/conversion campaigns. https://reddit.com/r/advertising/comments/1tpqpn9/i_spend_400_on_reddit_ads_to_find_that_807_was/ `[ANECDOTAL — methodologically detailed]`
- Counter-theory: much of it is **mobile misclicks** — ads blend into the feed, Reddit logs the click but GA never loads. https://reddit.com/r/advertising/comments/1uxtegb/is_reddit_advertising_a_scam/
- Support refuses refunds ("Reddit does not have any bot clicks"); community remedy is bank chargebacks. Claim: below a certain daily spend "you're buying logged-out and misclick traffic… the auction quietly serves you the cheapest impressions, which skew botward." https://reddit.com/r/advertising/comments/1u3fyfk/psa_under_no_circumstances_should_you_advertise/
- Practitioner rebuttal (2+ year advertiser): "not much more than other socials — 25–30%… control exclusions, control subreddit targeting, use third-party click-fraud systems." https://reddit.com/r/marketing/comments/1qnczsl/issues_with_reddit_ads/ `[PRACTITIONER]`

**Hard numbers from threads.**
- 1.5% CTR, $0.40 CPC, ~1% post-click conversion, real sales (single subreddit + expansion). https://reddit.com/r/PPC/comments/1kvf4x2/i_tried_reddit_ads_and_got_a_sale_now_i_want_to/
- $1.39/click, 45 clicks → only 8 real visitors (the misclick gap). https://reddit.com/r/advertising/comments/1u3fyfk/psa_under_no_circumstances_should_you_advertise/
- ~$25 CPM / $7+ CPC flagged as too high for narrow US B2B. https://reddit.com/r/PPC/comments/1qsb6cd/should_i_stop_the_500_reddit_ad_experiment_here/
- InterTeam AMA `[PRACTITIONER]`: CPCs "usually less than $2, almost never over $5"; retargeting clicks <$2. https://www.interteammarketing.com/blog/reddit-ads-faqs-from-ama

**The placement experiment (best single data point).** Agency split test, B2B SaaS: Conversation — 217 conversions, $61.92 CPA, 3.34% CVR · Feed — 91 conversions, $156.96 CPA, 1.24% CVR → ~54% lower CPA, 2.7x CVR for Conversation. Caveat: intent win, not placement win — thread visitors arrive problem-aware from Google/AI search. Split placements at ad-group level. ⚠️ Directly contested: "for cold audience remove 'conversation' placement." Resolution: Conversation wins when thread intent matches the offer; Feed for broad cold reach. https://reddit.com/r/PPC/comments/1qb96wv/reddit_conversation_vs_feed_ads/ `[PRACTITIONER]`, https://reddit.com/r/PPC/comments/1qsb6cd/should_i_stop_the_500_reddit_ad_experiment_here/

**Targeting tricks (u/ksaize's most-cited r/RedditforBusiness guide + InterTeam AMA).**
- Targeting is **OR, not AND** — communities + interests silently expands the audience. One targeting type per ad group. https://reddit.com/r/RedditforBusiness/comments/1qlv509/your_reddit_ads_test_didnt_work_out_check_if_you/ `[PRACTITIONER]`
- Turn off "Expand Audience" — blamed for junk clicks. https://reddit.com/r/marketing/comments/1qnczsl/issues_with_reddit_ads/
- Branded/comparison keywords ("X alternative", "X reviews") convert best. Keep keyword ad groups separate. [InterTeam AMA](https://www.interteammarketing.com/blog/reddit-ads-faqs-from-ama) `[PRACTITIONER]`
- Desktop = higher intent, fewer bots. [InterTeam AMA](https://www.interteammarketing.com/blog/reddit-ads-faqs-from-ama) `[PRACTITIONER]`
- **Geo discipline:** a worldwide campaign got clicks almost exclusively from India/Pakistan — the algorithm chases the cheapest clicks. After excluding them, "there are no more views or clicks." https://reddit.com/r/digital_marketing/comments/1t6rxpo/clicks_from_asia_only_reddit_ads/ — double-edged for āagman: India is our market AND the canonical cheap-click region; validate with on-site behavior, never clicks.
- Choose countries by conversion data, not CPM. https://reddit.com/r/RedditforBusiness/comments/1vhwacx/guide_how_to_create_reddit_max_campaigns_that_get/ `[PRACTITIONER]`

**Objectives & structure.**
- "If you choose campaign goal as traffic, you will get exactly that and not sales" — Traffic optimizes toward accidental clickers. https://reddit.com/r/RedditforBusiness/comments/1qlv509/your_reddit_ads_test_didnt_work_out_check_if_you/ `[PRACTITIONER]`
- Pixel + CAPI non-negotiable, yet "Reddit is terrible at attributing its own conversions… find other ways" — branded-search lift, surveys. https://reddit.com/r/PPC/comments/1qsb6cd/should_i_stop_the_500_reddit_ad_experiment_here/ `[PRACTITIONER]`
- Retargeting = highest-consensus tactic: "~80% of sales come from remarketing… website visitors only, no layered targeting, ≤10–20% of budget, 30-day frequency ~8–10, exclude buyers." [ksaize guide](https://reddit.com/r/RedditforBusiness/comments/1qlv509/your_reddit_ads_test_didnt_work_out_check_if_you/) `[PRACTITIONER]`
- Minimum viable test: 100–200 clicks before judging; "don't look at it for two weeks." https://reddit.com/r/PPC/comments/1qsb6cd/should_i_stop_the_500_reddit_ad_experiment_here/
- Reddit MAX (beta Jan 2026): 17% lower CPA reported, but r/PPC skepticism — "it defaults to engagement, and on here engagement means sarcasm, outrage, and memes." https://ppc.land/hubspot-and-reddit-reveal-why-b2b-buyers-bypass-your-website/ `[OFFICIAL-adjacent]`, https://reddit.com/r/PPC/comments/1q7i4hw/reddit_ads_worth_it_seems_different_than_say/

**Creative & comments.**
- "Lead with a discussion or question instead of a direct offer." https://reddit.com/r/digital_marketing/comments/1stagf9/feels_like_reddit_is_still_massively_underused_in/
- Fintech copy rules (Skip the Noise): name the pain with a specific number ("Most SMBs lose $2,400/year to fees. Here's the math"); avoid vague superiority, selective rate promotion, "trusted by 1M users", urgency tactics, named-competitor comparisons. https://skipthenoisemedia.com/blog/reddit-ads-fintech `[PRACTITIONER]`
- "If your ads have upvotes and positive comments, you'll see better results." https://reddit.com/r/marketing/comments/1qnczsl/issues_with_reddit_ads/
- `[OFFICIAL]` Comments are **disabled by default** on new ads; you opt in per ad. https://business.reddithelp.com/s/article/Managing-ads-with-comments-on
- Moderation mechanics: you must be a moderator of the ad profile to remove comments; your Reddit rep can enable "auto-mod" (comments require approval); there is no comment notification. https://reddit.com/r/RedditforBusiness/comments/1vfwch8/what_people_fear_will_happen_when_you_leave/ `[PRACTITIONER]`

**What killed campaigns:** Traffic objective; worldwide geo; stacked OR-targeting; judging at <$500/<1 week; aggressive cold CTAs; polished creative; expecting last-click ROAS; broad DTC e-commerce (most consistently failed vertical). [Threads above]

**The compounding angle:** Reddit threads rank on Google and feed ChatGPT/Perplexity answers (Reddit organic traffic +53% post-Google deal; #2 AI-referral source). Paid + organic presence keeps delivering after spend stops. https://reddit.com/r/digital_marketing/comments/1stagf9/feels_like_reddit_is_still_massively_underused_in/, [InterTeam AMA](https://www.interteammarketing.com/blog/reddit-ads-faqs-from-ama)

---

## 4. Finance vertical + India specifics

**Reddit policy on financial products.**
- Financial products are **restricted, not prohibited**: "Reddit restricts ads related to financial products and services, including… cryptocurrencies." `[OFFICIAL]` [Reddit policy page](https://business.reddithelp.com/s/article/financial-cryptocurrency-products-and-services-policy)
- Requirements: licensed/regulated entity, fee/rate disclosures, **no unrealistic ROI promises or guaranteed returns**, compliance with local financial advertising law in the targeted geo. Prohibited outright: pyramid schemes, unlicensed advisory, "get rich quick." [AuditSocials](https://www.auditsocials.com/blog/reddit-advertising-policy-compliance-guide-2026), [Stackmatix policy guide](https://www.stackmatix.com/blog/reddit-advertising-policy) `[PRACTITIONER]`
- Restricted categories get extra scrutiny and can take longer than the standard 24–48h. Enforcement is graduated: rejection → spend cap/manual review → suspension → ban. [Stackmatix](https://www.stackmatix.com/blog/reddit-advertising-policy), [AuditSocials](https://www.auditsocials.com/blog/reddit-advertising-policy-compliance-guide-2026) `[PRACTITIONER]`
- Crypto vs fintech: crypto advertisers were managed-service-only with licensing proof (2022 interview with Reddit's crypto-ads lead); conventional fintech runs self-serve. ⚠️ One tracker lists crypto ads "Prohibited in: India (partial)" — single source, but signals India-specific finance gating may exist. āagman is equities/F&O, not crypto. [Marketing Brew](https://www.marketingbrew.com/stories/2022/04/07/the-dos-and-don-ts-of-running-crypto-ads-on-reddit), [AuditSocials](https://www.auditsocials.com/blog/reddit-advertising-policy-compliance-guide-2026)

**The SEBI layer — binds āagman regardless of platform.** `[REGULATORY]`
- SEBI Advertisement Code for IAs/RAs (Apr 5, 2023): no past-performance references, no assured/guaranteed returns, no superlatives without independently verified awards; standard risk disclosures required. [TaxGuru](https://taxguru.in/sebi/sebis-advertisement-code-guide-investment-advisers-research-analysts.html), [Daanik](https://www.daanik.com/public/blog/the-truth-behind-investment-ads-what-they-won-t-tell-you)
- **BASL pre-approval before any ad** (incl. digital/social): submit draft → verification ID in ~2–5 working days → publish carrying verification ID + SEBI registration number + disclaimer → archive 5 years. [Aktai](https://www.aktai.app/blog/sebi-advertisement-code-research-analysts-2026), [TaxGuru](https://taxguru.in/sebi/sebis-advertisement-code-guide-investment-advisers-research-analysts.html)
- **Finfluencer association ban** (notified Aug 29, 2024, enforced Oct 2024): SEBI-regulated entities may not have any monetary *or non-monetary* association with unregistered advice-givers — no referral fees, paid collabs, or lead-sharing. Zerodha shut Zero1 as a consequence. On Reddit: no paying subreddit figures/influencers. [DealPlexus](https://www.dealplexus.com/blog/sebi-finfluencer-rules), [StartupFeed](https://startupfeed.in/zerodha-zero1-shutdown-amid-regulatory-concerns/)
- Enforcement is real: 15,000+ websites and 8,890 social accounts taken down (Aug 2024); 70,000+ misleading posts removed (Mar 2025). June 2026: SEBI proposed a common ad code adding dark-pattern bans. [Kofluence](https://www.kofluence.com/blog/influencer-marketing-regulations-2026/), [TaxGuru](https://taxguru.in/sebi/sebi-proposes-common-advertisement-code-regulated-entities.html)
- Net: Reddit's finance rules are a *subset* of SEBI's. A BASL-approved ad will almost certainly pass Reddit review; a Reddit-compliant ad can still violate SEBI. SEBI is the binding constraint.

**India audience & communities.**
- India is Reddit's #3 country: ~26.8M users (2024), ~30.8M (2025), ~5.2% of global traffic — small, urban, English-speaking slice (~2.1% population penetration). Sachin Tendulkar named global brand ambassador June 2025 to grow India; agencies report 40% YoY engagement growth in Indian subs. [DemandSage](https://www.demandsage.com/reddit-statistics/), [Interteam](https://www.interteammarketing.com/blog/reddit-statistics-2026), [PitchOnnet](https://www.pitchonnet.com/pitch-feature/reddits-growing-ad-appeal-for-indian-brands-37662.html) `[PRACTITIONER]`

**Targetable Indian finance communities (tracker estimates; verify live in Ads Manager):**

| Subreddit | Approx. size | Source |
|---|---|---|
| r/IndiaInvestments | ~921k, high activity | [GummySearch](https://gummysearch.com/r/IndiaInvestments/) |
| r/personalfinanceindia | ~570–599k | [RedPulse](https://redpulse.io/subreddit-search/r/personalfinanceindia/), [Nichory](https://nichory.com/r/personalfinanceindia) |
| r/IndianStreetBets | ~559k, +12.9%/yr — the real F&O/retail-trading hub | [GummySearch](https://gummysearch.com/r/cryptocurrency777/) |
| r/mutualfunds | ~147k | [GummySearch](https://gummysearch.com/r/mutualfunds/) |
| r/FIRE_Ind | ~80–90k (sources conflict) | [GummySearch](https://gummysearch.com/r/FIRE_Ind/), [RedPulse](https://redpulse.io/subreddit-search/r/fire_ind/) |
| r/DalalStreetBets | **only ~22.5k** — too small to matter despite name recognition | [Wayback, Feb 2025](https://web.archive.org/web/20250220120928/https://www.reddit.com/r/dalalstreetbets/) |
| r/IndianFIRE | ~279 members — effectively nonexistent | [GummySearch](https://gummysearch.com/r/IndiaFIRE/) |

Combined realistic pool ≈ 2.2–2.4M members (with overlap), plus 28-day visitors multiplying effective reach. `[PRACTITIONER]`. Note: these subs skew MF/SIP/long-term; the hardcore F&O crowd concentrates in r/IndianStreetBets; no large dedicated Indian options-trading sub surfaced — check Ads Manager community search.

**India benchmarks & proof.**
- **CoinDCX (Indian crypto exchange) spends 3–5% of digital budget on Reddit and plans to increase**: "better-qualified traffic" than Meta/Google for niche audiences; measures CTR, sign-ups, deposits, CPA, AVPU. The single most relevant data point — an Indian trading-platform advertiser profitably running Reddit in India. [PitchOnnet, Aug 2025](https://www.pitchonnet.com/pitch-feature/reddits-growing-ad-appeal-for-indian-brands-37662.html) `[ANECDOTAL — named exec interview]`
- India cost benchmarks (⚠️ single agency source): **CPC ₹8–20 (~$0.10–0.24), CPM ₹50–120 (~$0.60–1.45)** — 5–10x cheaper than global fintech benchmarks; min ~₹400–500/day, typical tests ₹500–2,000/day. Tier-1 city targeting and festival seasons push costs up. [Trilokana](https://trilokana.com/blog/reddit-advertising-cost-in-india-2025-guide/) `[PRACTITIONER]`
- <10% of large Indian consumer brands have activated Reddit; finance is among verticals with "disproportionate success." [PitchOnnet](https://www.pitchonnet.com/pitch-feature/reddits-growing-ad-appeal-for-indian-brands-37662.html) `[PRACTITIONER]`
- Ops quirks: USD billing needs internationally-enabled card/forex card/PayPal (RuPay often rejected); currency conversion + taxes add effective cost; Indian city-level targeting available. [Trilokana funding](https://trilokana.com/blog/how-to-add-funds-to-your-reddit-ads-account-from-india-trilokana-marketing/), [Trilokana step-by-step](https://trilokana.com/blog/advertising-on-reddit-from-india-a-step-by-step-guide-trilokana-marketing/) `[PRACTITIONER]`

---

## 5. The āagman playbook — recommended first campaign

**Pre-flight (weeks −4 to 0).**
1. Install Reddit Pixel + Conversions API + UTMs + GA4/PostHog + "how did you hear about us" field. Nothing spends until this is live. [Stackmatix](https://www.stackmatix.com/blog/are-reddit-ads-worth-it)
2. Warm the founder/brand account organically in r/IndianStreetBets and r/IndiaInvestments for 4–8 weeks (answer F&O/systematic-trading questions, no links). Users check profiles; an empty one tanks ad credibility. [WOLF Financial](https://wolf.financial/blog/reddit-advertising-fintech-community-strategy), [InterTeam AMA](https://www.interteammarketing.com/blog/reddit-ads-faqs-from-ama)
3. Route all creative through BASL pre-approval (2–5 working days per batch); build a compliance-approved comment-reply library covering the 10 predictable attacks ("algo trading is a scam", "show audited returns", "SEBI reg means nothing"). [Aktai](https://www.aktai.app/blog/sebi-advertisement-code-research-analysts-2026), [WOLF Financial](https://wolf.financial/blog/reddit-advertising-fintech-community-strategy)
4. Payment: internationally-enabled card or forex card; budget is billed in USD. [Trilokana](https://trilokana.com/blog/how-to-add-funds-to-your-reddit-ads-account-from-india-trilokana-marketing/)

**Campaign 1 setup.**
- **Objective: Conversions** (oCPM lowest-cost). Never Traffic — it optimizes toward accidental clickers and bots. https://reddit.com/r/RedditforBusiness/comments/1qlv509/your_reddit_ads_test_didnt_work_out_check_if_you/
- **Geo: India only.** Never worldwide — the algorithm will chase the cheapest clicks. https://reddit.com/r/digital_marketing/comments/1t6rxpo/clicks_from_asia_only_reddit_ads/
- **Expansion targeting: OFF** for the first 2–4 weeks. [Stackmatix](https://www.stackmatix.com/blog/are-reddit-ads-worth-it)
- **Three ad groups (one targeting type each):**
  - AG1 — Community, trading cluster: **r/IndianStreetBets** (+ any options-trading subs found in Ads Manager community search). Founder-voice creative.
  - AG2 — Community, investing cluster: **r/IndiaInvestments, r/personalfinanceindia, r/mutualfunds, r/FIRE_Ind**. Education-first creative. Skip r/DalalStreetBets (too small) and r/IndianFIRE (nonexistent).
  - AG3 — Keyword only: "algo trading", "options selling", "algorithmic trading India", competitor terms ("Sensibull alternative", "Opstra vs", "Streak review") — branded/comparison keywords reportedly convert best. [InterTeam AMA](https://www.interteammarketing.com/blog/reddit-ads-faqs-from-ama)
- **Placements:** split Feed vs Conversation at the ad-group level if budget allows (Conversation showed ~54% lower CPA / 2.7x CVR for lead-gen); otherwise start Conversation-weighted in AG1/AG3, Feed for AG2. https://reddit.com/r/PPC/comments/1qb96wv/reddit_conversation_vs_feed_ads/
- **Add AG4 — Retargeting** in week 2–3 once pixel has traffic: site visitors only, no layered targeting, ~10–20% of budget, exclude converters. Aggressive CTAs ("open account", "book demo") live here, not in cold. [ksaize guide](https://reddit.com/r/RedditforBusiness/comments/1qlv509/your_reddit_ads_test_didnt_work_out_check_if_you/), [InterTeam](https://www.interteammarketing.com/blog/reddit-ads-best-practices)

**Budget split (total ~₹1–2 lakh/month, ~$1,200–2,400 — inside the fintech minimum-viable window).**
- AG1 trading cluster: 40% · AG2 investing cluster: 25% · AG3 keywords: 20% · AG4 retargeting (from week 2–3): 15%. Floor: ₹400–500/day/ad group; target ₹1,500–2,500/day total. Scale in ~20% weekly increments only.
- 6–8 week commitment before verdict. [Stackmatix](https://www.stackmatix.com/blog/reddit-ads-minimum-spend), [Web Tonic](https://www.webtonic.io/blog/fintech-reddit-ads-statistics)

**Creative approach.**
- āagman's founder-voice post style is native to Reddit — lean in. Free-form/text + carousel; avoid polished video (most volatile format on Reddit). [InterTeam AMA](https://www.interteammarketing.com/blog/reddit-ads-faqs-from-ama)
- Lead with the SEBI registration + NSE empanelment as the trust hook — the differentiator vs tip-sellers and forex gurus this audience hates. [Stackmatix finance](https://www.stackmatix.com/blog/reddit-ads-for-finance)
- Specific numbers, not hype: "How our momentum algo handled the Feb expiry-day spike" > "AI-powered trading platform." Never imply returns — Reddit policy and SEBI both prohibit it, and the community publicly executes overclaims. Position as "systematic, disciplined execution." [WOLF Financial](https://wolf.financial/blog/reddit-advertising-fintech-community-strategy), [Skip the Noise](https://skipthenoisemedia.com/blog/reddit-ads-fintech)
- Write per-cluster: meme-literate trader voice for r/IndianStreetBets; transparent fee/feature explainers for the investing cluster. 3–5 variants per ad group; soft CTAs cold ("See the platform", "Read how it works").
- Open free-form ads with a TL;DR. [Reddit Free-form Ads](https://business.reddithelp.com/s/article/Free-form-Ads) `[OFFICIAL]`
- **Comments ON** (they're off by default — opt in per ad), with a product-fluent human replying within ~2h in the first 6h; get made moderator of the ad profile and ask the Reddit rep for comment pre-approval ("auto-mod") since there's no comment notification. https://business.reddithelp.com/s/article/Managing-ads-with-comments-on `[OFFICIAL]`, https://reddit.com/r/RedditforBusiness/comments/1vfwch8/what_people_fear_will_happen_when_you_leave/
- Rotate creative every 2 weeks — Indian niche pools saturate fast and there are no self-serve frequency caps. [Stackmatix](https://www.stackmatix.com/blog/are-reddit-ads-worth-it), [PPC Land](https://ppc.land/reddits-frequency-cap-restrictions-a-persistent-hurdle-for-small-advertisers-2/)

**What to measure (never clicks).**
- Primary: landing-page-view rate, session duration, sign-up CPA, qualified-lead CPA. Reddit fintech CTR of 0.2–0.5% is normal — judge on CPA.
- Guardrails: upvote ratio per ad (negative → pull and rebuild, don't push harder), comment sentiment, frequency per community, branded-search lift, GA4 assisted conversions. Assume 25–30% invalid traffic and a ~2:1 clicks-to-sessions ratio even when healthy. [Stackmatix creative](https://www.stackmatix.com/blog/reddit-ads-creative-best-practices), https://reddit.com/r/advertising/comments/1uxtegb/is_reddit_advertising_a_scam/
- Attribution: optimize on 7d-click/1d-view; judge on 28-day assisted conversions + surveys. Expect 14–45 day click-to-funded-account lag. [Stackmatix finance](https://www.stackmatix.com/blog/reddit-ads-for-finance)

**Kill / scale thresholds (set before launch; India economics are unproven).**
- Don't touch anything for the first 14 days (learning phase; budget/targeting edits reset it).
- Kill a creative: negative upvote ratio after ~5k impressions, or CTR below ad-group median after 100+ clicks.
- Kill an ad group: no qualified sign-up after ~₹25–30k spend (~2x target CPA × 10), or landing-page-view rate <40% of clicks persistently (junk traffic signature).
- Scale an ad group (+20%/week): CPA ≤ blended Google/Meta lead CPA for 2 consecutive weeks.
- Verdict at week 6–8 on the whole channel: keep if blended qualified-lead CPA ≤ 1.5x Meta/Google blended *and* branded-search lift is visible. [Threshold logic from [Stackmatix](https://www.stackmatix.com/blog/are-reddit-ads-worth-it), [Bunny Honey](https://blog.bunnyhoneyclub.com/posts/reddit-ads-small-business-2026)]

---

## 6. Open questions / what we still don't know

1. **No published India-geo CPC/CPM benchmarks** beyond one Indian agency (Trilokana: CPC ₹8–20, CPM ₹50–120). āagman's first 6 weeks IS the benchmark study.
2. **No case study from an Indian equities/F&O platform** — CoinDCX (crypto) is the closest. No practitioner data on regulated IA/algo products anywhere.
3. **Whether Reddit applies extra finance-ad gating for India** (the "India (partial)" crypto restriction is single-sourced). First submission will tell us — expect longer review and possible documentation requests.
4. **Bot/invalid-traffic rate in Indian finance subs specifically** — claims range 25–30% to 80%+ globally; the r/IndianStreetBets pool is small and cheap, which cuts both ways. Validate with on-site behavior.
5. **Live audience sizes and ad-eligibility of Indian trading subs** — tracker numbers are estimates and some conflict (r/fireindia); Ads Manager's audience estimates at setup are authoritative. Also whether any targetable Indian options-trading subs exist beyond r/IndianStreetBets.
6. **Whether BASL verification IDs in ad creative affect Reddit review or CTR** — untested anywhere.
7. **Reddit MAX campaigns for India** — beta (Jan 2026), promising beta stats, practitioner skepticism; only worth testing after clean conversion data exists.
8. **Comment pre-approval ("auto-mod") availability for small self-serve accounts** — described as rep-enabled; confirm at setup.

---

*Sources consolidated from three research streams (practitioner best practices; Reddit community threads via Arctic Shift archive; finance vertical + India) plus Reddit's official Ads Help Center. Agent reports dated 2026-08-07.*
