const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const LEADS_CHAT_ID = process.env.TELEGRAM_LEADS_CHAT_ID || '';

const PACKAGES = {
  sponsored: { title: 'Sponsored Story', price: 99 },
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
  const company = clean(body.company, 160);
  const url = clean(body.url, 300);
  const goal = clean(body.goal, 1200);
  const email = clean(body.email, 254).toLowerCase();
  const telegram = clean(body.telegram, 80);
  const consent = body.consent === true || body.consent === 'true' || body.consent === 'on';

  if (!plan || company.length < 2 || goal.length < 8 || !validEmail(email) || !consent) {
    return res.status(400).json({ ok: false, error: 'invalid_submission' });
  }

  const applicationId = `IR-WEB-${Date.now().toString(36).toUpperCase()}`;
  const record = {
    applicationId,
    package: packageId,
    price: plan.price,
    company,
    url,
    goal,
    email,
    telegram,
    source: clean(body.source || 'advertise-page', 80),
    createdAt: new Date().toISOString()
  };

  console.log('IR_WEB_LEAD', JSON.stringify(record));

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
          '<i>Review fit before sending any PayPal payment link.</i>'
      });
    } catch (error) {
      console.error('web-lead-forward-failed', error?.message || error);
    }
  }

  return res.status(200).json({ ok: true, applicationId });
};
