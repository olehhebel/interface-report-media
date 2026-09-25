const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const LEADS_CHAT_ID = process.env.TELEGRAM_LEADS_CHAT_ID || '';

const PACKAGES = {
  sponsored: { title: 'Sponsored Story', price: 99 },
  'launch-monthly': { title: 'Launch Offer · Monthly Sponsored Story', price: 9.99 },
  feature: { title: 'Founder / Product Feature', price: 149 },
  distribution: { title: 'Feature + Distribution', price: 199 }
};

function clean(value = '', max = 1200) {
  return String(value).replace(/[<>]/g, '').trim().slice(0, max);
}

function escapeHtml(value = '') {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;');
}

function validEmail(value = '') {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value).trim());
}

async function tg(method, payload) {
  if (!BOT_TOKEN) throw new Error('TELEGRAM_BOT_TOKEN is missing');
  const response = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/${method}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await response.json();
  if (!data.ok) throw new Error(data.description || 'Telegram API error');
  return data.result;
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'method_not_allowed' });

  const body = req.body || {};
  if (body.company_website) return res.status(200).json({ ok: true });

  const packageId = clean(body.package, 40);
  const plan = PACKAGES[packageId];
  const company = clean(packageId === 'launch-monthly' ? '$9.99/month offer · ' + String(body.goal || '') : body.company, 160);
  const url = clean(body.url, 300);
  const goal = clean(body.goal, 1200);
  const email = clean(body.email, 254).toLowerCase();
  const telegram = clean(body.telegram, 80);
  const consent = body.consent === true || body.consent === 'true' || body.consent === 'on';

  if (!plan || company.length < 2 || goal.length < 8 || !validEmail(email) || !consent) {
    return res.status(400).json({ ok: false, error: 'invalid_submission' });
  }

  const applicationId = `IR-WEB-${Date.now().toString(36).toUpperCase()}-${require('node:crypto').randomBytes(4).toString('hex').toUpperCase()}`;
  const record = {
    applicationId,
    // The existing Apps Script understands the sponsored package. The offer
    // is identified by source and price without requiring a script redeploy.
    package: packageId === 'launch-monthly' ? 'sponsored' : packageId,
    price: plan.price,
    company,
    url,
    goal,
    email,
    telegram,
    source: packageId === 'launch-monthly' ? 'homepage-launch-monthly-9.99' : clean(body.source || 'advertise-page', 80),
    createdAt: new Date().toISOString()
  };

  console.log('IR_WEB_LEAD', JSON.stringify(record));

  // Email is the primary notification channel. Google Apps Script executes
  // as the mailbox owner; no third-party email subscription or SMTP password.
  const mailUrl = process.env.GOOGLE_SCRIPT_WEBHOOK_URL;
  const mailSecret = process.env.GOOGLE_SCRIPT_WEBHOOK_SECRET;
  if (!mailUrl || !mailSecret) {
    console.error('web-lead-email-not-configured', applicationId);
    return res.status(503).json({ ok: false, error: 'email_not_configured' });
  }
  try {
    const endpoint = new URL(mailUrl);
    if (endpoint.protocol !== 'https:' || endpoint.hostname !== 'script.google.com' || !endpoint.pathname.startsWith('/macros/s/') || !endpoint.pathname.endsWith('/exec')) {
      throw new Error('invalid_google_script_url');
    }
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        secret: mailSecret,
        ...record
      }),
      signal: AbortSignal.timeout(15000)
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(`google_script_${response.status}_${String(result?.error || 'http_error').slice(0, 80)}`);
    if (result?.ok !== true || result?.applicationId !== applicationId) {
      throw new Error(`google_script_rejected_${String(result?.error || 'invalid_response').slice(0, 80)}`);
    }
  } catch (error) {
    console.error('web-lead-email-failed', applicationId, error?.message || error);
    return res.status(502).json({ ok: false, error: 'email_delivery_failed' });
  }

  if (BOT_TOKEN && LEADS_CHAT_ID) {
    try {
      await tg('sendMessage', {
        chat_id: LEADS_CHAT_ID,
        parse_mode: 'HTML',
        disable_web_page_preview: true,
        text:
          '<b>New Interface Report web application</b>\n' +
          `<b>ID:</b> ${escapeHtml(applicationId)}\n` +
          `<b>Package:</b> ${escapeHtml(plan.title)} · $${plan.price}\n` +
          `<b>Company:</b> ${escapeHtml(company)}\n` +
          `<b>URL:</b> ${escapeHtml(url || '—')}\n` +
          `<b>Email:</b> ${escapeHtml(email)}\n` +
          `<b>Telegram:</b> ${escapeHtml(telegram || '—')}\n` +
          `<b>Goal / angle:</b> ${escapeHtml(goal)}\n\n` +
          '<i>Review editorial fit. Payment status must be verified with the provider.</i>'
      });
    } catch (error) {
      console.error('web-lead-forward-failed', error?.message || error);
    }
  }

  // The launch offer is an application, not an automatically billed
  // subscription. Confirm editorial fit and payment terms by email first.
  if (packageId === 'launch-monthly') {
    return res.status(200).json({ ok: true, applicationId, reviewPending: true });
  }

  // Prices shown in USD are indicative. The merchant sets explicit UAH totals
  // in the environment; never calculate a charge from a client-supplied price.
  const checkoutAmount = Number(process.env[`MONO_PRICE_${packageId.toUpperCase()}_KOP`]);
  const token = process.env.MONO_ACQUIRING_TOKEN;
  if (token && Number.isSafeInteger(checkoutAmount) && checkoutAmount > 0) {
    try {
      const payment = await fetch('https://api.monobank.ua/api/merchant/invoice/create', {
        method: 'POST',
        headers: { 'X-Token': token, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount: checkoutAmount,
          ccy: 980,
          merchantPaymInfo: { reference: applicationId, destination: `Interface Report · ${plan.title}` },
          redirectUrl: `https://interfacereport.com/commercial-deck/?payment=returned&ref=${encodeURIComponent(applicationId)}`
        })
      });
      if (!payment.ok) throw new Error(`invoice_create_${payment.status}`);
      const invoice = await payment.json();
      const checkoutUrl = new URL(invoice.pageUrl);
      if (checkoutUrl.protocol !== 'https:' || !checkoutUrl.hostname.endsWith('.monobank.ua')) throw new Error('unexpected_checkout_host');
      console.log('IR_CHECKOUT_CREATED', JSON.stringify({ applicationId, invoiceId: invoice.invoiceId, amount: checkoutAmount, ccy: 980 }));
      return res.status(200).json({ ok: true, applicationId, checkoutUrl: checkoutUrl.toString(), checkoutAmountUAH: (checkoutAmount / 100).toFixed(2) });
    } catch (error) {
      console.error('checkout_create_failed', error?.message || error);
    }
  }
  return res.status(200).json({ ok: true, applicationId, checkoutPending: true });
};
