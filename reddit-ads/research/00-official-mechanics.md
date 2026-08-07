# Reddit Ads — Official Mechanics (Reddit Help Center, condensed)

Source: business.reddithelp.com (Ads Help Center), pulled 2026-08-07.

## 1. Campaign objectives (7) — https://business.reddithelp.com/s/article/Ad-campaign-objectives
- **Brand awareness & reach**: optimize impressions, pay CPM. Post types: free-form, image, video, carousel.
- **Traffic**: optimize clicks, pay CPC. All four post types.
- **Conversions**: optimize conversions; lowest cost = oCPM, cost cap = CPC. Image/video/carousel (no free-form).
- **Video views**: optimize views, pay CPV; video only.
- **App installs**: separate ad groups for Android vs iOS, mobile-only; lowest cost = oCPM, cost cap = CPC.
- **Catalog sales**: requires product catalog; pay CPC.
- **Lead generation** (beta): on-Reddit lead forms, image/video only; optimize clicks, pay CPC.

## 2. Bidding & auction — https://business.reddithelp.com/s/article/How-much-do-Reddit-Ads-cost
- Real-time second-price-style auction; under-delivery possible (budget not guaranteed to spend).
- Billing events by objective: CPM (awareness), CPC (traffic, conversions cost-cap, app installs, catalog, leads), CPV (video views), oCPM (conversions/app installs lowest-cost).
- Billable actions count within 2 hours of ad placement.
- Automated strategies: **Lowest cost** (maximize volume for budget) and **Cost cap** (keep avg CPC/CPM at/below cap; may not spend full budget). Manual bidding available on any objective, automated recommended.
- Auto-bidding for awareness/reach in beta.

## 3. Budgets — same article
- Budgets live at **ad group** level: **daily** or **lifetime**.
- Optional **campaign spend cap** = hard lifetime max at campaign level; doesn't affect pacing.
- Ad groups may **overspend budget by up to 20%** (live auctions).
- Budget changes take up to 60 minutes.
- No stated minimum daily budget.

## 4. Ad formats & specs — https://business.reddithelp.com/s/article/Reddit-Ad-Unit-Specifications
- 4 self-serve types: **Image** (1), **Video** (1), **Carousel** (2–6 cards), **Free-form** (rich text: up to 20 images, 5 videos, 40,000 chars). Destination URL on all but free-form.
- Placements: **Feed** (Home/Popular/community feeds) and **Conversation** (thread pages); comments can be enabled.
- Headline: 300 chars max, recommend ≤100. Destination URL 268 chars; display URL 100 chars, must match domain.
- Image: JPG/PNG/GIF ≤3 MB (4:3 1440×1080 recommended). Video: MP4/MOV ≤1 GB, ≤30 FPS, 2s–15min (recommend 5–30s), autoplays. Carousel per-card caption 50 chars, per-card URL.
- Premium Takeovers (Reddit/Category/First View) are managed-only, CPM-based.
- ~20 standard CTA buttons.

## 5. Targeting — https://business.reddithelp.com/s/article/Overview-Reddit-Ads-Audience-and-Targeting
- **Reddit audiences**: interest (IAB), community (subreddits user subscribed/viewed/visited in last 28 days), keyword (English only).
- **Custom audiences**: website retargeting (Pixel/CAPI), customer lists (hashed emails/MAIDs), lookalikes, engagement retargeting (ad interaction, last 6 months).
- **Demographics**: location, gender, language. **Device & carrier** targeting (device targeting immutable after ad-group creation).
- Logic: interest/community/keyword OR each other, AND vs custom audiences; device/gender/language/location AND everything.
- Special ad categories (housing/employment/credit) cannot target gender, age, or postal codes.

## 6. Ad review — https://business.reddithelp.com/s/article/About-Reddits-ad-review-process
- Human review of copy, media, landing page, targeting. Typically within **1 day**; submit **≥48h** before planned start.
- Edits to copy/URL/creative/targeting trigger re-review; bid/schedule changes do not.
- Alcohol/gambling/pharma need sales-rep pre-approval; healthcare/finance may need certifications.

## 7. Pixel & measurement — https://business.reddithelp.com/s/article/reddit-pixel + /s/article/Conversions-API
- **Reddit Pixel**: JS snippet; manual, GTM, Shopify, or partner install; verify with Pixel Helper + Events Manager.
- **CAPI**: server-to-server; web/app/offline events; events within **7 days** (real-time recommended); batch ≤1,000/request.
- Pixel + CAPI together recommended; **deduplication required** when both used.
- Match keys (email, IP, click ID, user agent, MAID, external ID) improve attribution; click ID in URL recommended.

## vs Google/Meta: what's different
- Community (subreddit) targeting based on 28-day visit/subscribe behavior — unique to Reddit; keyword targeting is English-only.
- No stated minimum daily budget; ad groups can overspend budgets up to 20%.
- Only two automated bid strategies (lowest cost, cost cap); no target-ROAS/maximize-value equivalent.
- Review is explicitly human (~1 day) — slower than Meta/Google automated-first review.
- Billable actions only count within 2 hours of placement — much tighter attribution-to-billing window.
