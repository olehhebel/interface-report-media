# Interface Report — Direct Advertiser Pipeline

Operational schema for direct advertiser sales. This repository is public: **do not store real prospect email addresses, private notes, payment data or other personal lead data here.** Use this document only as the structure for a private CRM/Sheet.

## Pipeline stages

1. `PROSPECT` — relevant company identified, no outreach yet.
2. `TRIGGER_VERIFIED` — a concrete reason to contact the company has been verified.
3. `CONTACTED` — first personalized outreach sent.
4. `REPLIED` — prospect responded.
5. `QUALIFIED` — topic, product and campaign fit the publication.
6. `OFFER_SENT` — package/scope/launch price sent.
7. `APPLICATION_RECEIVED` — advertiser submitted the brief.
8. `EDITORIAL_REVIEW` — fit/evidence/reputation review in progress.
9. `APPROVED_FOR_PAYMENT` — accepted; PayPal link may now be sent.
10. `PAID` — payment confirmed.
11. `IN_PRODUCTION` — editorial production/review underway.
12. `APPROVAL` — final commercial/editorial review.
13. `PUBLISHED` — live URL delivered.
14. `REPORTED` — campaign report delivered when applicable.
15. `REPEAT_OPPORTUNITY` — follow-up date/trigger recorded.
16. `DECLINED` — rejected by Interface Report.
17. `LOST` — qualified opportunity did not proceed.

Never move directly from prospecting to payment. `EDITORIAL_REVIEW` must precede `APPROVED_FOR_PAYMENT`.

## Private CRM fields

### Identity
- Company
- Product
- Domain
- Industry/category
- Country / primary market
- Contact name
- Contact role
- Contact email
- LinkedIn/profile URL

### Fit
- Interface Report topic cluster
- Audience-fit note
- Verified trigger
- Trigger source URL
- Trigger date
- Why now
- Proposed angle

### Sales
- Pipeline stage
- First outreach date
- Last touch date
- Next action date
- Outreach channel
- Offer/package
- Quoted price
- Discount reason, if any
- Response status
- Objection / blocker

### Commercial review
- Application ID
- Editorial fit status
- Evidence status
- Reputation-risk status
- Sponsor disclosure required
- Link treatment confirmed
- Approval owner
- Approval date

### Payment / delivery
- Payment requested date
- Payment status
- Payment provider
- Payment reference (non-sensitive identifier only)
- Production start
- Draft/review status
- Publication date
- Live URL
- Distribution delivered
- Report delivered

### Retention
- Repeat advertiser
- Next relevant trigger
- Renewal/follow-up date
- Lifetime orders
- Lifetime revenue

## Prospect priority score

Use a simple 0–10 score before outreach:

- +2: strong topical fit with AI products, agents, UX/design, engineering, SaaS or startups.
- +2: recent verified launch/funding/product-change trigger.
- +2: likely buyer role/contact can be identified.
- +2: clear editorial angle that benefits readers independently of the sponsor.
- +1: company has active content/PR/launch marketing.
- +1: plausible repeat sponsorship potential.

Prioritize 8–10 first. Avoid low-fit volume outreach.

## Outreach rule

Every first message must contain one verifiable company-specific observation. Do not send generic "buy a post" copy.

Recommended message structure:

1. Specific trigger/observation.
2. Why it fits Interface Report readers.
3. One concrete editorial opportunity.
4. One low-friction CTA.
5. Interface Report / Advertise link.

Do not promise traffic numbers that are not verified. Do not sell ranking influence or dofollow links.

## Launch offer mapping

- Sponsored Story — from $99.
- Founder / Product Feature — from $149.
- Feature + Distribution — from $199, only using distribution inventory that is actually active at campaign time.

Treat these as launch validation prices. Raise pricing when verified demand, readership, newsletter reach, repeat advertiser rate and campaign value increase.

## Weekly revenue metrics

Track privately:

- new qualified prospects
- personalized outreach sent
- replies
- positive replies
- applications
- approved applications
- payments
- published campaigns
- revenue
- average order value
- lead-to-sale conversion
- outreach-to-reply rate
- repeat advertiser count
- average days from first contact to payment

## Data handling

Keep the live CRM private. Do not commit prospect PII to this public repository.

Payment credentials never belong in the CRM. Store only non-sensitive payment status/reference fields.

If a prospect asks to stop being contacted, record the suppression status in the private CRM and do not continue outreach.
