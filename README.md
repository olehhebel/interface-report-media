# Interface Report

Independent media publication about AI products, agents, Human–AI interaction, product design, engineering, startups and SaaS.

Canonical domain: https://interfacereport.com/

## Technical publishing
- Static crawlable HTML and clean canonical URLs
- XML sitemap and RSS feed
- NewsMediaOrganization, WebSite, Person and Article structured data
- OAI-SearchBot allowed; GPTBot policy controlled separately
- Story-specific 1600×900 article images
- IndexNow support for newly published or materially changed URLs
- GitHub Actions publication QA on pushes and pull requests

Production source-of-truth is `main`; `launch` should mirror the same release commit.

The custom domain and HTTPS are live. Keep Google Search Console ownership verified, submit `/sitemap.xml`, and inspect representative canonical URLs. Submit IndexNow only while the published key file resolves publicly.

## Latest editorial publication

- 2026-10-30: [AI Product Discovery: Your Story Comes Before SEO Hype](https://interfacereport.com/analysis/ai-product-discovery-story-before-seo-hype/) — practical, source-backed framework for product narratives, AI search eligibility and transparent sponsored distribution.
- Updated homepage and advertising copy to emphasize the $9.99/month offer, its deliverables and review-before-payment terms.

- 2026-10-26: [Open Agent Standards Need a Portability Test](https://interfacereport.com/analysis/aaif-agent-standards-portability-test/) — original analysis of AAIF’s October 22 project additions and a product-focused portability review across skills, interfaces, environments and execution.
- 2026-10-25: [Claude on Google Cloud: Who Runs Your API?](https://interfacereport.com/analysis/claude-google-cloud-operator-choice/) — analysis of Anthropic’s October 22 Google Cloud launch, operator differences, feature access and product migration decisions.
- 2026-10-24: [TanStack AI 1.0: What Happens After Reload?](https://interfacereport.com/analysis/tanstack-ai-1-0-recovery-ux/) — analysis of the October 23 TanStack AI 1.0 release, stable-core boundaries and the product design of agent recovery.
- 2026-10-23: [Your AI Agent May Need Fewer Agents](https://interfacereport.com/analysis/single-agent-loop-fewer-subagents/) — evidence-led analysis of Anthropic’s October 22 single-agent loop guidance, migration limits and outcome evaluation.
- 2026-10-22: [Claude Duet Is Here. Your Attention Is the Interface.](https://interfacereport.com/analysis/claude-duet-proactive-agent-attention-ux/) — original analysis of Claude Duet, proactive-agent UX, attention and action approvals, based on verified Anthropic sources.
- Homepage rotation: new lead first; the previous lead remains visibly linked below. Published articles and permanent URLs are retained.
- Publication includes article metadata/schema, original 1600×900 editorial artwork, RSS, sitemap and topic/author listings. Validate with `python scripts/check_site.py` before release.
