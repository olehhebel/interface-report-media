# Free Interface Report lead email

GitHub holds the code. Vercel already runs the site backend in `api/advertiser-lead.js`. This Google Apps Script sends the notification using your Gmail account; Resend, a paid subscription, and sender-domain DNS records are unnecessary.

1. In [script.google.com](https://script.google.com/), sign in to the Google account that will **send** the notification. Create a **New project** called `Interface Report lead mail` and replace `Code.gs` with this repository's `google-apps-script/Code.gs`. Save.
2. Under **Project Settings → Script properties**, create `IR_WEBHOOK_SECRET` with a random value of at least 32 characters. Generate it in a password manager. Do not put it in GitHub, a URL, or chat.
3. Use **Deploy → New deployment → Web app**. Set **Execute as: Me** and **Who has access: Anyone**. Deploy and authorize the script's mail-sending permission with your Google account. Copy the `/exec` web-app URL. Use `/exec`, not the `/dev` test URL.
4. In Vercel's `interface-report-media` project, open **Settings → Environment Variables**. Add `GOOGLE_SCRIPT_WEBHOOK_URL` = the `/exec` URL and `GOOGLE_SCRIPT_WEBHOOK_SECRET` = the exact same secret. Select Production (and Preview only if you intend to test it there). Save, then redeploy Production so its functions receive the variables.
5. Submit one real test through the site's **Book a sponsored story** form. The Vercel function calls the script, which sends an email to `drgebel@gmail.com`, with the applicant's email in Reply-To. Confirm delivery in that inbox; check Spam and the Apps Script **Executions** page if it fails.

The website sends the secret only from its server, never from the browser. The script keeps its recipient fixed, validates fields, checks the daily mail quota, and ignores repeated application IDs for six hours. The `/exec` endpoint is publicly reachable so the site can call it; the 32+ character shared secret is the access control. Rotate both copies if it is exposed. A consumer Gmail account currently has a limit of 100 email recipients per day via Apps Script; Google can change quotas.

References: [Google web app deployments](https://developers.google.com/apps-script/guides/web), [MailApp](https://developers.google.com/apps-script/reference/mail/mail-app), [Apps Script quotas](https://developers.google.com/apps-script/guides/services/quotas).
