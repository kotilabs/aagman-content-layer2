# Signal Research Artifact: ai-power-semiconductor-wall

## 1. Signal restatement

AI data center buildouts are creating a shortage in power management integrated circuits (PMICs), baseboard management controllers (BMCs), and related power semiconductors that run on mature semiconductor process nodes. The bottleneck is no longer only GPU compute or high-bandwidth memory (HBM); it has shifted to the physical infrastructure of power conversion, cooling, grid interconnection, and electrical equipment. Hyperscalers are committing record capital to AI infrastructure, and that demand is pulling capacity away from general-purpose servers, automotive, industrial, and consumer electronics that share the same 8-inch / mature-node supply base. The result is a structural supply squeeze in which the marginal AI dollar increasingly funds power delivery, cooling, and grid infrastructure rather than additional logic chips.

## 2. Verified facts

- **NVIDIA Q4 FY2026 data center revenue was $62.3 billion, up 75% year over year; full-year FY2026 data center revenue was $193.7 billion, up 68%.** Source: NVIDIA Q4 and FY2026 earnings release, 25 February 2026. URL: https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-fourth-quarter-and-fiscal-2026
- **Global semiconductor sales reached $791.7 billion in 2025, an increase of 25.6% from $630.5 billion in 2024.** Source: Semiconductor Industry Association (SIA), 6 February 2026. URL: https://www.semiconductors.org/global-annual-semiconductor-sales-increase-25-6-to-791-7-billion-in-2025/
- **Electricity demand from data centers rose 17% in 2025; AI-focused data center demand grew even faster. Data center electricity consumption is projected to roughly double by 2030, and AI-focused data center power use is poised to triple.** Source: International Energy Agency (IEA), "Key Questions on Energy and AI," 16 April 2026. URL: https://www.iea.org/news/data-centre-electricity-use-surged-in-2025-even-with-tightening-bottlenecks-driving-a-scramble-for-solutions
- **Goldman Sachs Research forecasts global data center power demand will increase 50% by 2027 and as much as 165% by 2030 (vs. 2023). Global data center power demand is estimated at ~55 GW today and is projected to reach 84 GW by 2027.** Source: Goldman Sachs, "AI to Drive 165% Increase in Data Center Power Demand by 2030," 4 February 2025. URL: https://www.goldmansachs.com/insights/articles/ai-to-drive-165-increase-in-data-center-power-demand-by-2030
- **A shortage in power IC supplies is expected throughout 2026, driven by surging demand from AI data center servers. Lead times for PMICs have lengthened to 35–40 weeks and for BMC ICs to 21–26 weeks.** Source: The Register, "AI now gobbling up power and management chips for servers," 23 April 2026; TrendForce press release, "Extended Component Lead Times Weigh on General Server Growth," 15 April 2026. URLs: https://www.theregister.com/on-prem/2026/04/23/ai-now-gobbling-up-power-and-management-chips-for-servers/5229166 ; https://www.trendforce.com/presscenter/news/20260415-13013.html
- **TrendForce downgraded its 2026 general server shipment growth forecast from ~20% YoY to ~13% YoY because suppliers are prioritizing higher-margin AI server components. AI server shipments are still expected to grow ~28% YoY in 2026.** Source: TrendForce, 15 April 2026. URL: https://www.trendforce.com/presscenter/news/20260415-13013.html
- **Global 8-inch wafer foundry capacity is tightening in 2026 and is expected to fall by about 2.4% as TSMC and Samsung scale back output, while demand for mature-node products including power management chips used in AI systems remains steady.** Source: TrendForce via SemiMedia, "8-inch wafer foundry capacity tightens in 2026 as utilization rises," 16 January 2026. URL: https://www.semimedia.cc/20543.html
- **The top five hyperscalers are projected to spend $600 billion+ on infrastructure in 2026, roughly 75% of that on AI infrastructure; combined capex from Alphabet, Amazon, Meta, and Microsoft could surpass $700 billion in 2026, up from about $410 billion in 2025.** Source: Fortune, "Big Tech's $700 Billion AI Buildout," 30 April 2026; Accuris Tech analysis citing Fortune and Introl. URLs: https://fortune.com/2026/04/30/big-tech-hyperscalers-will-spend-700-billion-on-ai-infrastructure-this-year-with-no-clear-end-in-sight-eye-on-ai/ ; https://accuristech.com/blog/ai-data-center-electronic-component-supply/
- **McKinsey estimates global demand for data center capacity could grow 19–22% per year from 2023 to 2030, and that about 70% of total data center capacity demand will be for AI-ready facilities by 2030. McKinsey also estimates capital spending on the procurement and installation of mechanical and electrical systems for data centers will likely exceed $250 billion by 2030.** Source: McKinsey & Company, "AI power: Expanding data center capacity to meet growing demand," 29 October 2024. URL: https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights/ai-power-expanding-data-center-capacity-to-meet-growing-demand
- **Data centers are projected to consume 70% of memory chips produced in 2026; HBM now consumes 23% of total DRAM wafer capacity.** Source: Tom's Hardware, "Data centers will consume 70 percent of memory chips made in 2026," 18 January 2026; Tech Insider. URLs: https://www.tomshardware.com/pc-components/ram/data-centers-will-consume-70-percent-of-memory-chips-made-in-2026-supply-shortfall-will-cause-the-chip-shortage-to-spread-to-other-segments ; https://tech-insider.org/memory-chip-shortage-2026-ai-consumer-electronics/
- **The 2026 HBM market is estimated at $54.6 billion, a 58% increase year over year, with HBM3E expected to account for roughly two-thirds of shipments.** Source: SK hynix Newsroom, "2026 Market Outlook – Focus on the HBM-Led Memory Supercycle," 5 January 2026, citing Bank of America. URL: https://news.skhynix.com/2026-market-outlook-focus-on-the-hbm-led-memory-supercycle/
- **TSMC's monthly CoWoS advanced packaging capacity could reach 120,000–140,000 wafers in 2026, up from roughly 35,000 wafers per month in late 2024; total industry capacity including OSAT partners could approach 200,000 wafers per month.** Source: TrendForce, "TSMC CoWoS Supply-Demand Gap Reportedly Seen Narrowing from 20% to 10% by End-2026," 15 June 2026. URL: https://www.trendforce.com/news/2026/06/15/news-tsmc-cowos-supply-demand-gap-reportedly-seen-narrowing-from-20-to-10-by-end-2026-as-capacity-expands/
- **Infineon Technologies increased fiscal 2026 capex by €500 million to €2.7 billion to expand manufacturing capacity for power semiconductors used in AI data-center infrastructure. Infineon projects €1.5 billion in AI data-center revenue in FY2026 and €2.5 billion in FY2027.** Source: Astute Group, "Infineon expands manufacturing investment as AI data-centre demand reshapes power-chip supply," 13 March 2026, citing Reuters and Infineon. URL: https://www.astutegroup.com/news/general/infineon-expands-manufacturing-investment-as-ai-data-centre-demand-reshapes-power-chip-supply/
- **Gartner identified Infineon as "the company to beat" in AI data center power semiconductors as of May 2026, citing its comprehensive product portfolio, manufacturing capabilities, and early investment in wide-bandgap technologies.** Source: Infineon press release, 26 June 2026. URL: https://www.infineon.com/press-release/2026/infxx202606-117
- **AI infrastructure projects entering service in 2025 took an average of more than seven years to reach operational status in PJM territory; projects spent an average of more than three years reaching an interconnection service agreement and another four years waiting to come online after approval.** Source: Data Center Knowledge, "Why AI Data Center Projects Face Years of Delays After Approval," 12 May 2026, citing PJM Interconnection data. URL: https://www.datacenterknowledge.com/energy-power-supply/why-ai-data-center-projects-face-years-of-delays-after-approval
- **Wood Mackenzie projects the US data center electrical equipment market will grow from roughly $20 billion in 2026 to $65 billion by 2030. Lead times for critical components are already 18–36 months. Padmount transformer demand in hyperscale data centers is forecast to rise from 1,573 units in 2025 to 9,395 units by 2030.** Source: Wood Mackenzie press release, 28 April 2026. URL: https://www.woodmac.com/press-releases/data-center-demand-drives-us-electrical-equipment-market-to-$65b-reshaping-industry-dynamics/
- **Average power transformer lead times increased from roughly 50 weeks in 2021 to about 120 weeks in 2024, with some large substation and generator step-up transformers ranging from 80 to 210 weeks. Generator step-up transformer lead times surpassed 160 weeks by Q1 2026.** Source: Wood Mackenzie, "Supply shortages and an inflexible market give rise to high power transformer lead times," 2 April 2024; Data Center Knowledge, 12 May 2026. URLs: https://www.woodmac.com/news/opinion/supply-shortages-and-an-inflexible-market-give-rise-to-high-power-transformer-lead-times/ ; https://www.datacenterknowledge.com/energy-power-supply/why-ai-data-center-projects-face-years-of-delays-after-approval
- **BloombergNEF projects copper demand from AI-powered data centers will average about 400,000 tonnes per year over the next decade, peaking at 572,000 tonnes in 2028. Microsoft's 2009 Chicago data center used roughly 27 tonnes of copper per megawatt of power capacity.** Source: Carbon Credits, citing BloombergNEF and BHP, "Data Centers' Copper Hunger," 14 August 2025. URL: https://carboncredits.com/data-centers-copper-hunger-how-ai-is-driving-a-looming-supply-crunch/
- **Deloitte projects inference workloads will make up roughly two-thirds of AI compute in 2026, up from about one-third in 2023. Deloitte also estimates AI data center capex of $400–450 billion globally in 2026, with over half spent on chips inside devices.** Source: Deloitte, "More compute for AI, not less," 18 November 2025; Deloitte 2026 Semiconductor Industry Outlook. URLs: https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/compute-power-ai.html ; https://www.deloitte.com/us/en/insights/industry/technology/technology-media-telecom-outlooks/semiconductor-industry-outlook.html

## 3. Key data table

| Metric | Value | Date / period | Source | Why it matters |
|---|---|---|---|---|
| NVIDIA Q4 FY2026 data center revenue | $62.3 B (+75% YoY) | Q4 FY2026 (ended Jan 25, 2026) | NVIDIA earnings release, Feb 2026 | Confirms scale of AI compute demand pulling downstream infrastructure |
| NVIDIA FY2026 data center revenue | $193.7 B (+68% YoY) | FY2026 | NVIDIA earnings release, Feb 2026 | Full-year AI compute revenue baseline; note some secondary sources cite ~$197 B |
| Global semiconductor sales | $791.7 B (+25.6% YoY) | 2025 | SIA, Feb 2026 | Industry-wide demand surge led by AI infrastructure |
| Data center electricity demand growth | +17% YoY | 2025 | IEA, Apr 2026 | Rate of demand growth is outpacing total electricity demand growth (~3%) |
| Data center power demand forecast | +50% by 2027, +165% by 2030 (vs. 2023) | 2025–2030 | Goldman Sachs, Feb 2025 | Quantifies the power infrastructure challenge |
| Global data center power demand | ~55 GW current, 84 GW by 2027 | 2025–2027 | Goldman Sachs, Feb 2025 | Baseline for grid and generation investment needs |
| PMIC lead times | 35–40 weeks | 2026 | TrendForce / The Register, Apr 2026 | Evidence of power IC shortage |
| BMC IC lead times | 21–26 weeks | 2026 | TrendForce, Apr 2026 | Management-controller shortage hits general servers |
| General server shipment growth | ~13% YoY (downgraded from ~20%) | 2026 | TrendForce, Apr 2026 | Capacity diversion to AI servers is constraining general-purpose supply |
| AI server shipment growth | ~28% YoY | 2026 | TrendForce, Apr 2026 | AI-specific demand remains strong |
| Global 8-inch wafer capacity change | -2.4% | 2026 | TrendForce via SemiMedia, Jan 2026 | Mature-node supply is shrinking just as power-IC demand rises |
| Hyperscaler AI infrastructure capex | $600 B+ (top 5); ~$700 B (top 4 US hyperscalers) | 2026 | Fortune / Accuris, Apr 2026 | Scale of demand driving component shortages |
| Data center share of memory chips | ~70% | 2026 | Tom's Hardware, Jan 2026 | Memory capacity reallocation away from consumer/automotive/industrial |
| HBM share of DRAM wafer capacity | 23% | 2026 | Tech Insider / Accuris, 2026 | HBM production crowds out commodity DRAM wafer starts |
| 2026 HBM market size | $54.6 B (+58% YoY) | 2026 | SK hynix, citing BofA, Jan 2026 | Size of the premium memory bottleneck |
| TSMC CoWoS capacity | 120,000–140,000 wafers/month | 2026 | TrendForce, Jun 2026 | Advanced packaging remains a key GPU/HBM constraint |
| Infineon fiscal 2026 capex | €2.7 B (+€500 M increase) | FY2026 | Astute Group / Reuters, Mar 2026 | Major power-semiconductor supplier expanding for AI demand |
| Infineon AI data-center revenue target | €1.5 B (FY2026), €2.5 B (FY2027) | FY2026–FY2027 | Astute Group / Reuters, Mar 2026 | Power-semiconductor revenue directly tied to AI buildout |
| PJM AI project time to operation | >7 years average | Projects entering service in 2025 | Data Center Knowledge / PJM, May 2026 | Grid interconnection and downstream equipment are the binding constraint |
| US data center electrical equipment market | $20 B (2026) → $65 B (2030) | 2026–2030 | Wood Mackenzie, Apr 2026 | Scale of electrical infrastructure spend required |
| Power transformer lead times | ~120 weeks average in 2024, >160 weeks for GSUs by Q1 2026 | 2021–2026 | Wood Mackenzie / Data Center Knowledge | Grid equipment is a multi-year bottleneck |
| Data center copper demand | ~400 kt/year average, peak 572 kt in 2028 | 2025–2035 | BloombergNEF via Carbon Credits, Aug 2025 | AI data centers add material demand to an already tight copper market |
| Copper intensity | ~27 tonnes per MW | Case study: Microsoft Chicago DC, 2009 | BloombergNEF / BHP via Carbon Credits | Benchmark for physical copper content per MW of capacity |
| AI data center capex | $400–450 B globally | 2026 | Deloitte, Nov 2025 | Over half is chips; the rest is land, construction, power, cooling |
| Inference share of AI compute | ~66% | 2026 | Deloitte, Nov 2025 | Workload mix is shifting toward inference, which still requires heavy infrastructure |

## 4. Mechanism

AI data centers consume semiconductors at two levels: the headline compute layer (GPUs, custom ASICs, HBM, advanced packaging) and the enabling infrastructure layer (power conversion, management controllers, cooling, electrical equipment, grid interconnection). The signal centers on the second layer.

Power management ICs and BMCs are manufactured mainly on mature process nodes—often 8-inch / 200-mm wafer fabs using Bipolar-CMOS-DMOS (BCD) processes. These nodes have not received the investment that leading-edge logic or memory have received. Meanwhile:

1. **AI servers use more and higher-density power components.** A GPU rack can draw 100+ kW, requiring high-current voltage regulators, power converters, gate drivers, and current sensors. Suppliers prioritize these higher-margin AI orders.
2. **Mature-node capacity is shrinking.** TSMC and Samsung are reducing 8-inch output; global 8-inch capacity is forecast to contract ~2.4% in 2026 even as power-IC demand rises.
3. **Memory reallocation tightens adjacent supply.** HBM now takes 23% of DRAM wafer starts, and data centers consume ~70% of memory output. Foundries and OSATs steer capacity toward AI-linked products, leaving less for general servers, automotive, industrial, and consumer.
4. **Downstream infrastructure cannot scale as fast as chips.** Grid interconnection, substations, transformers, switchgear, and transmission buildouts face 3–7+ year timelines. Even when GPUs are available, data centers cannot always be energized.
5. **The result is a feedback loop.** Physical power/cooling constraints delay data center completions; delayed projects extend the period over which component demand stays elevated; and the same components are needed by non-AI industries, creating cross-sector competition for a shrinking pool of mature-node supply.

## 5. Competing interpretations

### Interpretation A: A structural, multi-year infrastructure supercycle
- **Who makes it:** Accuris, TrendForce, Wood Mackenzie, Goldman Sachs, McKinsey, Infineon.
- **Supporting evidence:** Hyperscaler capex is scaling to $600–700 B annually; data center power demand is projected to grow 165% by 2030; transformer lead times exceed 160 weeks; mature-node capacity is shrinking while AI demand rises.
- **Contradicting evidence:** Some AI models (e.g., DeepSeek-style efficiency gains) could reduce training compute intensity; a demand slowdown or capex pause would soften the bottleneck.
- **Why it might be wrong:** It assumes sustained exponential AI demand and no major efficiency breakthrough. If inference shifts rapidly to cheaper edge hardware or if macro conditions curtail hyperscaler spending, the infrastructure overbuild thesis could replace the shortage thesis.

### Interpretation B: A supply-chain dislocation that will ease as capacity ramps
- **Who makes it:** TSMC, some equipment suppliers, TrendForce (in its CoWoS analysis).
- **Supporting evidence:** TSMC is expanding CoWoS capacity at a >80% CAGR through 2027; OSAT partners are adding capacity; Infineon and others are raising capex; the CoWoS supply-demand gap is expected to narrow from ~20% to ~10% by end-2026.
- **Contradicting evidence:** Grid and electrical equipment lead times are much longer than chip lead times; land, permitting, and transmission are not solved by additional semiconductor capacity.
- **Why it might be wrong:** It treats the problem as a chip/packaging problem. Even if chip supply improves, power delivery and grid interconnection may remain binding constraints for years.

### Interpretation C: A demand bubble driven by speculative AI capex that risks overbuild
- **Who makes it:** Skeptical equity analysts, some investors quoted in Fortune and other financial media.
- **Supporting evidence:** Hyperscaler spending has tripled in two years; AI monetization remains uneven; fast-depreciating hardware raises the cost of misjudging demand; Meta's stock fell after revealing large AI capex plans.
- **Contradicting evidence:** Cloud revenue is growing strongly; AI workloads are shifting from training to inference, which implies sustained recurring compute demand; long-term power purchase agreements and grid commitments suggest capex is not purely speculative.
- **Why it might be wrong:** It conflates valuation risk with physical demand. Even if returns disappoint, the installed capacity and component orders are real and will have already tightened supply chains.

### Interpretation D: A sectoral reallocation that benefits infrastructure enablers over chip designers
- **Who makes it:** Operators and research firms emphasizing the "infrastructure lag" narrative.
- **Supporting evidence:** The AI bottleneck has moved from GPUs to power, cooling, and grid; power semiconductors, transformers, liquid cooling, and utilities are becoming strategic; Gartner flags power semiconductors as a distinct competitive battleground.
- **Contradicting evidence:** NVIDIA and TSMC still capture the majority of AI semiconductor economics; without compute demand, there is no power-infrastructure demand.
- **Why it might be wrong:** It understates the continued centrality of compute. Power semiconductors are a derivative demand; if AI compute growth stalls, the infrastructure enabler story stalls with it.

## 6. Cross-asset implications

- **Equities:** Semiconductor sector exposure is bifurcating. Companies with heavy exposure to AI data center power delivery (power semiconductors, PMICs, SiC/GaN, voltage regulators) are seeing demand inflections and capex increases. General-purpose server, automotive, industrial, and consumer semiconductor suppliers face longer lead times and allocation pressure. Data center REITs and colocation providers benefit from tight capacity and rising rents, but only if they can secure power.
- **Power and utilities:** Utilities with excess generation and transmission capacity, or those located near planned AI campuses, are seeing large load additions. PJM forecasts summer peak demand rising from ~154 GW in 2025 to nearly 210 GW by 2036. Power prices and capacity costs are rising in constrained markets.
- **Commodities:** Copper demand from AI data centers is a new structural demand pillar (~400 kt/year average, peaking at 572 kt in 2028). Electrical steel (grain-oriented) and transformer materials are also tightening. Uranium/nuclear, natural gas, and renewable energy offtake are being pulled by hyperscaler power procurement.
- **Credit / rates:** Multi-year capex commitments by hyperscalers and utilities increase corporate bond issuance and long-duration infrastructure debt demand. Rising power demand can support higher real rates in affected regions.
- **FX:** Regions with abundant power and fast permitting (parts of the US, Middle East, Nordic countries) may attract capital inflows. Countries with constrained grids (Ireland, parts of Europe) face capital allocation trade-offs.
- **Derivatives:** Power and natural gas forward curves in data center hotspots are likely pricing in demand growth. Equipment suppliers with long backlogs may have pricing power and lower cyclical risk near term.

## 7. Historical analogues or structural memory

### Analogue 1: The 1999–2000 telecom fiber and optical buildout
- **Key similarity:** Massive capital deployment into physical infrastructure ahead of revenue certainty; shortages in optical components, power systems, and specialty materials; prices and lead times rose sharply.
- **Key difference:** AI demand is currently more concentrated among a small number of well-capitalized hyperscalers, and the end-use applications are broader than a single telecom customer base.
- **Use for perspective:** Shows how infrastructure buildouts can overshoot and create lasting supply-chain scarring, even if final demand eventually absorbs the capacity.

### Analogue 2: The 2020–2022 pandemic semiconductor shortage
- **Key similarity:** Mature-node automotive, industrial, and consumer chips faced acute shortages because capacity had been reallocated to high-margin electronics; lead times stretched to 40+ weeks; allocation favored large customers.
- **Key difference:** The pandemic shortage was triggered by a temporary demand spike and supply disruption; the AI-driven shortage is linked to a sustained, multi-year capex cycle.
- **Use for perspective:** Demonstrates that the most constrained nodes are not the most advanced ones, but the mature nodes where investment lagged. It also shows how shortages can last years, not quarters.

## 8. What is known, unknown, and unknowable

### Known
- Hyperscalers are committing $600–700 B to AI infrastructure in 2026.
- Data center power demand is growing faster than overall electricity demand and is projected to double by 2030.
- PMICs, BMCs, and power semiconductors for AI servers are in shortage; lead times have extended sharply.
- Mature-node / 8-inch capacity is shrinking in 2026 while demand rises.
- Grid interconnection, transformers, and electrical equipment are multi-year bottlenecks.
- NVIDIA's official FY2026 data center revenue was $193.7 B, not the $197.3 B figure repeated in some secondary roundups.

### Unknown
- The exact magnitude of the power IC shortage by volume and revenue; most figures are directional or based on supplier lead-time estimates.
- Whether hyperscaler capex will keep rising, plateau, or contract in 2027–2028.
- The pace at which efficiency gains (model compression, better chips, liquid cooling) will offset power demand growth.
- Whether mature-node capacity expansions (SMIC, Vanguard, others) will be sufficient to relieve pressure.

### Unknowable
- Whether a breakthrough in AI algorithms or hardware architecture will suddenly reduce the need for large-scale data center buildouts.
- The exact timing and location of grid failures, permitting reversals, or political/regulatory limits on data center power use.
- The ultimate return on AI infrastructure spending and whether it justifies the current capex trajectory.

## 9. Open questions

1. Will the power-semiconductor shortage spread from AI servers into automotive, industrial, and medical power electronics, as it did in 2020–2022?
2. Can grid operators and utilities shorten interconnection timelines, or will data center deployments remain gated by 3–7 year waits for power?
3. Will hyperscalers begin building more on-site generation (gas, nuclear SMRs, geothermal) to bypass grid constraints, and on what timeline?
4. How will the shift from training to inference change the power-semiconductor content per dollar of AI capex?
5. Will mature-node foundries respond with sufficient capacity expansion, or will the power-IC bottleneck persist through 2027–2028?

## 10. Source list

1. NVIDIA, "NVIDIA Announces Financial Results for Fourth Quarter and Fiscal 2026," 25 February 2026. https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-fourth-quarter-and-fiscal-2026
2. Semiconductor Industry Association (SIA), "Global Annual Semiconductor Sales Increase 25.6% to $791.7 Billion in 2025," 6 February 2026. https://www.semiconductors.org/global-annual-semiconductor-sales-increase-25-6-to-791-7-billion-in-2025/
3. International Energy Agency (IEA), "Data centre electricity use surged in 2025," 16 April 2026. https://www.iea.org/news/data-centre-electricity-use-surged-in-2025-even-with-tightening-bottlenecks-driving-a-scramble-for-solutions
4. Goldman Sachs, "AI to Drive 165% Increase in Data Center Power Demand by 2030," 4 February 2025. https://www.goldmansachs.com/insights/articles/ai-to-drive-165-increase-in-data-center-power-demand-by-2030
5. The Register, "AI now gobbling up power and management chips for servers," 23 April 2026. https://www.theregister.com/on-prem/2026/04/23/ai-now-gobbling-up-power-and-management-chips-for-servers/5229166
6. TrendForce, "Extended Component Lead Times Weigh on General Server Growth; 2026 Server Shipments Forecast to Grow 13% YoY," 15 April 2026. https://www.trendforce.com/presscenter/news/20260415-13013.html
7. SemiMedia, "8-inch wafer foundry capacity tightens in 2026 as utilization rises," 16 January 2026 (citing TrendForce). https://www.semimedia.cc/20543.html
8. Fortune, "Big Tech's $700 Billion AI Buildout: No Clear End in Sight," 30 April 2026. https://fortune.com/2026/04/30/big-tech-hyperscalers-will-spend-700-billion-on-ai-infrastructure-this-year-with-no-clear-end-in-sight-eye-on-ai/
9. Accuris Tech, "How AI Data Centers Are Reshaping Electronic Component Supply in 2026," 2026. https://accuristech.com/blog/ai-data-center-electronic-component-supply/
10. McKinsey & Company, "AI power: Expanding data center capacity to meet growing demand," 29 October 2024. https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights/ai-power-expanding-data-center-capacity-to-meet-growing-demand
11. Tom's Hardware, "Data centers will consume 70 percent of memory chips made in 2026," 18 January 2026. https://www.tomshardware.com/pc-components/ram/data-centers-will-consume-70-percent-of-memory-chips-made-in-2026-supply-shortfall-will-cause-the-chip-shortage-to-spread-to-other-segments
12. Tech Insider, "Memory Chip Shortage 2026: HBM Takes 23% of DRAM Wafers," April 2026. https://tech-insider.org/memory-chip-shortage-2026-ai-consumer-electronics/
13. SK hynix Newsroom, "2026 Market Outlook – Focus on the HBM-Led Memory Supercycle," 5 January 2026. https://news.skhynix.com/2026-market-outlook-focus-on-the-hbm-led-memory-supercycle/
14. TrendForce, "TSMC CoWoS Supply-Demand Gap Reportedly Seen Narrowing from 20% to 10% by End-2026," 15 June 2026. https://www.trendforce.com/news/2026/06/15/news-tsmc-cowos-supply-demand-gap-reportedly-seen-narrowing-from-20-to-10-by-end-2026-as-capacity-expands/
15. Astute Group, "Infineon expands manufacturing investment as AI data-centre demand reshapes power-chip supply," 13 March 2026. https://www.astutegroup.com/news/general/infineon-expands-manufacturing-investment-as-ai-data-centre-demand-reshapes-power-chip-supply/
16. Infineon Technologies, "Infineon named as the Company to Beat in AI Data Center Power Semiconductors by Gartner," 26 June 2026. https://www.infineon.com/press-release/2026/infxx202606-117
17. Data Center Knowledge, "Why AI Data Center Projects Face Years of Delays After Approval," 12 May 2026. https://www.datacenterknowledge.com/energy-power-supply/why-ai-data-center-projects-face-years-of-delays-after-approval
18. Wood Mackenzie, "The US data center electrical equipment market is projected to surge to $65 billion by 2030," 28 April 2026. https://www.woodmac.com/press-releases/data-center-demand-drives-us-electrical-equipment-market-to-$65b-reshaping-industry-dynamics/
19. Wood Mackenzie, "Supply shortages and an inflexible market give rise to high power transformer lead times," 2 April 2024. https://www.woodmac.com/news/opinion/supply-shortages-and-an-inflexible-market-give-rise-to-high-power-transformer-lead-times/
20. Carbon Credits, "Data Centers' Copper Hunger: How AI is Driving a Looming Supply Crunch?" 14 August 2025 (citing BloombergNEF and BHP). https://carboncredits.com/data-centers-copper-hunger-how-ai-is-driving-a-looming-supply-crunch/
21. Deloitte, "More compute for AI, not less," 18 November 2025. https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/compute-power-ai.html
22. Deloitte, "2026 Global Semiconductor Industry Outlook," 5 February 2026. https://www.deloitte.com/us/en/insights/industry/technology/technology-media-telecom-outlooks/semiconductor-industry-outlook.html
23. TrendForce, "Breaking Through the AI Power Wall: Why SiC/GaN Matter in the HVDC Era," 20 May 2026. https://insights.trendforce.com/p/sic-and-gan-ai-power-wall
