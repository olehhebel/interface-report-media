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
