# Project Atlas Discoverability Initiative

**Start:** 2026-11-28 (UTC) · **Budget:** $0 · **Public site:** https://randosy.github.io/project-atlas/atlas/

## Purpose

Increase qualified traffic from teachers, makers, engineers, and researchers. Promote working exhibits and transparent evidence, not unverified claims. Respect the estate's public/private boundaries: IAS is excluded from promotion.

## Technical foundation

The `atlas-web-preview` branch publishes the public site through `.github/workflows/atlas-pages.yml`. The build generates a project-wide sitemap, canonical URLs and search/social metadata for public HTML pages, preserving existing descriptions and using selected exhibit images. The existing local-link audit remains in place.

- Deployment: https://github.com/RandoSY/project-atlas/actions
- Sitemap after successful deployment: https://randosy.github.io/project-atlas/sitemap.xml
- The host-level robots.txt is outside this project site's control; submit the sitemap directly instead.
- For future changes, inspect the published HTML and sitemap, check the workflow logs, and review unresolved link warnings. Do not treat a successful deployment as proof of search indexing.

## First 30 days

| Week | Action | Success measure |
|---|---|---|
| 1 | Verify the URL-prefix property https://randosy.github.io/project-atlas/ in Google Search Console; submit sitemap.xml; register with Bing Webmaster Tools; optionally configure privacy-oriented analytics | Sitemap accepted, baseline recorded |
| 2 | Add website backlinks to public upstream repositories; update GitHub descriptions and relevant topics; evaluate Zenodo release archival and ORCID links | Relevant reciprocal links and documented archives |
| 3 | Share one relevant exhibit at a time with teacher, maker, research or robotics communities, following community rules | Referrals, comments, useful feedback |
| 4 | Review indexed pages, search impressions/clicks, referrals and exhibit popularity; revise outreach based on evidence | Weekly metrics and next action |

## Prioritized public entry points

| Exhibit | Audience | URL |
|---|---|---|
| Catalase Open Lab | Biology and STEM educators | https://randosy.github.io/project-atlas/atlas/catalase-fem/open-lab/ |
| Circuits to Genomes | Computational biology and computer architecture readers | https://randosy.github.io/project-atlas/atlas/circuits-to-genomes/ |
| CORE 10 | Inquiry-centered STEM educators | https://randosy.github.io/project-atlas/atlas/core-10/ |
| Virtual Instruments | Embedded systems and measurement enthusiasts | https://randosy.github.io/project-atlas/atlas/instruments/ |
| Lazy LiDAR | Educational robotics and makers | https://randosy.github.io/project-atlas/atlas/lazy-lidar/ |

## Outreach copy (draft; not posted)

**General launch:** Project Atlas is a public working exhibition of independent scientific inquiry, STEM teaching, low-cost instrumentation, robotics and research. Explore experiments, models, source repositories and the evidence behind the work: https://randosy.github.io/project-atlas/atlas/

**Educators:** Catalase Open Lab turns a familiar biochemical reaction into an inquiry-centered experiment, with teacher and student guides, data templates and analysis resources. Explore the open laboratory: https://randosy.github.io/project-atlas/atlas/catalase-fem/open-lab/

**Makers:** Project Atlas collects practical virtual instruments, embedded measurement experiments and educational robotics demonstrations. Browse the instruments and their associated resources: https://randosy.github.io/project-atlas/atlas/instruments/

**Researchers:** From Circuits to Genomes explores architectural economy, evolutionary functional continuity and AI-assisted inquiry. It is an evolving research portfolio rather than a claim of established biological proof: https://randosy.github.io/project-atlas/atlas/circuits-to-genomes/

## Account-dependent actions (not completed)

1. Sign into https://search.google.com/search-console/ with the owner's Google account. Add the URL-prefix property above, follow its verification instructions, then submit the sitemap. For HTML verification, place the exact verification file in the published project root, not just the source repository.
2. Sign into https://www.bing.com/webmasters/ and import the verified property if supported, or verify directly.
3. If using Cloudflare Web Analytics, create a site at https://www.cloudflare.com/web-analytics/ and obtain its site-specific beacon token. Add only the provided analytics snippet to the staged public site after approval. Do not invent a token.
4. Review Zenodo and ORCID links and archive specific, validated public releases. Do not assign a fictitious DOI or publish unreleased research.

## Measurement

Record weekly dates, indexed pages, impressions, clicks, top search queries, top exhibit pages, referring sites, and meaningful feedback. Treat absent analytics as unknown, not zero. No paid advertising, automated spam, or traffic guarantees.
