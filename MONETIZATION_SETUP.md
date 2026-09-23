# Interface Report — Monetization Activation Checklist

This file documents the runtime configuration required by the Growth & Monetization OS implementation. Do not place real secrets or private payment credentials in the repository.

## Activation order

1. Keep the commercial flow in **review-before-payment** mode.
2. Verify Telegram lead delivery and admin approval actions.
3. Verify the owner's PayPal account can receive the intended commercial payments.
4. Create verified PayPal checkout/payment URLs for each accepted package and add them as environment variables.
5. Create/configure the newsletter publication and add the Beehiiv API credentials.
6. Test advertiser intake, approval, payment handoff, newsletter double opt-in and analytics events on preview.
7. Only then merge and deploy to production.

## Existing Telegram environment variables

- `SITE_URL=https://interfacereport.com`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_BOT_USERNAME` — optional fallback optimization; the API can resolve the username from the bot token.
- `TELEGRAM_WEBHOOK_SECRET`
- `TELEGRAM_LEADS_CHAT_ID`

The website's sponsored-story form emails each accepted application to
`drgebel@gmail.com` before presenting the payment step. Configure
`RESEND_API_KEY` for this Vercel project and verify `interfacereport.com` as a
sending domain with Resend. The default sender is
`Interface Report <leads@interfacereport.com>`; set `IR_LEADS_FROM` only if
another verified sender is required. The applicant's email is set as Reply-To.
If the key is missing or the provider rejects the message, the form reports
an error and does not claim that the application was received. Telegram is a
secondary copy after successful email delivery.

The leads chat receives new Telegram and web commercial applications. Telegram applications expose admin **Approve → PayPal** and **Decline** actions. A PayPal link is not shown to the applicant before approval.

## PayPal environment variables

Configure these only after commercial receiving capability and each destination URL have been tested:

- `PAYPAL_SPONSORED_URL` — Sponsored Story, launch price $99.
- `PAYPAL_FEATURE_URL` — Founder / Product Feature, launch price $149.
- `PAYPAL_DISTRIBUTION_URL` — Feature + Distribution, launch price $199.

Rules:

- Do not use Friends & Family for commercial orders.
- Do not hard-code PayPal credentials or private account data into source files.
- Payment does not bypass editorial policy.
- If a payment URL is absent, an approved applicant receives a message that payment instructions will follow manually.

## Beehiiv newsletter environment variables

- `BEEHIIV_API_KEY`
- `BEEHIIV_PUBLICATION_ID`

The website posts subscriptions through `/api/newsletter` and requests email confirmation. UTM source, medium, campaign, content and referring site are passed to the newsletter provider for attribution.

Until both variables are configured, the endpoint deliberately returns `newsletter_not_configured` rather than pretending a subscriber was stored.

## Advertiser intake

Website endpoint: `/api/advertiser-lead`

Required fields:

- package
- company
- campaign goal / proposed angle
- contact email
- policy consent

Optional fields:

- product URL
- Telegram username

The endpoint creates an `IR-WEB-*` application ID, logs a structured lead, and forwards the application to `TELEGRAM_LEADS_CHAT_ID` when Telegram runtime variables are available.

## Growth analytics events

The browser runtime emits events through `gtag` when present, otherwise through `dataLayer`:

- `newsletter_signup_start`
- `newsletter_signup_complete`
- `newsletter_signup_error`
- `advertiser_lead_start`
- `advertiser_lead_complete`
- `advertiser_lead_error`

Do not claim analytics are active until the site's production analytics container is verified to receive these events.

## Google Preferred Sources

Editorial pages load Google's Preferred Sources publisher button and provide the deep-link fallback for `interfacereport.com`.

Do not present Preferred Sources as a ranking guarantee. It is a reader preference / loyalty mechanism.

## Future ad-network readiness

Do not add fake IDs or placeholder sellers to `ads.txt`.

Before activating Google AdSense or another programmatic provider, verify current eligibility, privacy/CMP requirements, payout compatibility, and user-experience impact. Add real `ads.txt` entries only after an authorized seller relationship exists.

## Production gate

Do not merge solely because code compiles. Production activation requires:

- Publication QA green.
- Preview flow tested on mobile and desktop.
- No PayPal link exposed before editorial acceptance.
- PayPal links verified if configured.
- Newsletter double opt-in verified if configured.
- No invented audience metrics.
- Sponsor disclosures and `rel="sponsored"` policy preserved.
