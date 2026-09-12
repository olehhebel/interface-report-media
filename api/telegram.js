const SITE_URL = process.env.SITE_URL || 'https://interfacereport.com';
const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const LEADS_CHAT_ID = process.env.TELEGRAM_LEADS_CHAT_ID || '';

const PLANS = {
  sponsored: {
    title: 'Sponsored Story',
    price: 99,
    paymentEnv: 'PAYPAL_SPONSORED_URL',
    description: 'Clearly labeled partner story, editorial review, permanent URL and standard publication metadata.'
  },
  feature: {
    title: 'Founder / Product Feature',
    price: 149,
    paymentEnv: 'PAYPAL_FEATURE_URL',
    description: 'Editor-led commercial feature built from supplied evidence and interviews, with clear sponsorship disclosure.'
  },
  distribution: {
    title: 'Feature + Distribution',
    price: 199,
    paymentEnv: 'PAYPAL_DISTRIBUTION_URL',
    description: 'Commercial feature plus selected homepage, newsletter or social distribution available at campaign time.'
  }
};

function esc(value = '') {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;');
}

async function tg(method, payload) {
  if (!BOT_TOKEN) throw new Error('TELEGRAM_BOT_TOKEN is missing');
  const r = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/${method}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await r.json();
  if (!data.ok) throw new Error(`${method}: ${data.description || 'Telegram API error'}`);
  return data.result;
}

function homeKeyboard() {
  return {
    inline_keyboard: [
      [{ text: 'Sponsored Story · $99', callback_data: 'plan:sponsored' }],
      [{ text: 'Founder / Product Feature · $149', callback_data: 'plan:feature' }],
      [{ text: 'Feature + Distribution · $199', callback_data: 'plan:distribution' }],
      [{ text: 'Editorial + sponsor policy ↗', url: `${SITE_URL}/sponsored-content-policy/` }],
      [{ text: 'Media Kit ↗', url: `${SITE_URL}/media-kit/` }]
    ]
  };
}

function paymentUrl(plan) {
  return process.env[plan.paymentEnv] || '';
}

function planKeyboard(slug) {
  const plan = PLANS[slug];
  const rows = [
    [{ text: 'Quick application', callback_data: `apply:${slug}` }]
  ];
  const pay = paymentUrl(plan);
  if (pay) rows.push([{ text: `Pay $${plan.price} with PayPal ↗`, url: pay }]);
  rows.push([{ text: '← All packages', callback_data: 'home' }]);
  return { inline_keyboard: rows };
}

async function sendHome(chatId) {
  return tg('sendMessage', {
    chat_id: chatId,
    parse_mode: 'HTML',
    disable_web_page_preview: true,
    text:
      '<b>Interface Report commercial desk</b>\n\n' +
      'Choose a publication package. Every paid placement is clearly disclosed and remains subject to editorial fit, evidence review and sponsor-link policy. Payment never guarantees a positive conclusion or search ranking.',
    reply_markup: homeKeyboard()
  });
}

async function sendPlan(chatId, slug) {
  const plan = PLANS[slug];
  if (!plan) return sendHome(chatId);
  return tg('sendMessage', {
    chat_id: chatId,
    parse_mode: 'HTML',
    disable_web_page_preview: true,
    text:
      `<b>${esc(plan.title)} · $${plan.price}</b>\n\n` +
      `${esc(plan.description)}\n\n` +
      '<b>Fast flow</b>\n1. Send one short application.\n2. We check fit and evidence.\n3. Pay securely with PayPal.\n4. Editorial production / review.\n5. Publish if accepted and send the live URL.\n\n' +
      '<i>Paid links are marked appropriately. Publication and rankings are never guaranteed.</i>',
    reply_markup: planKeyboard(slug)
  });
}

async function askApplication(chatId, slug) {
  const plan = PLANS[slug];
  if (!plan) return sendHome(chatId);
  return tg('sendMessage', {
    chat_id: chatId,
    parse_mode: 'HTML',
    text:
      `<b>${esc(plan.title)} — quick application</b>\n\n` +
      'Reply to this message with one compact line:\n\n' +
      '<code>company/product URL | campaign goal | contact email</code>\n\n' +
      'Example: <code>acme.ai | launch our agent workspace | founder@acme.ai</code>\n\n' +
      `<span class="tg-spoiler">[[IR_APPLY:${slug}]]</span>`,
    reply_markup: { force_reply: true, selective: true }
  });
}

async function handleApplication(msg, slug) {
  const plan = PLANS[slug];
  const raw = (msg.text || '').trim();
  if (!plan || raw.length < 8) {
    return tg('sendMessage', {
      chat_id: msg.chat.id,
      text: 'Please send a little more detail in the format: company/product URL | campaign goal | contact email.'
    });
  }

  const applicationId = `IR-${Date.now().toString(36).toUpperCase()}-${String(msg.chat.id).slice(-4)}`;
  const username = msg.from?.username ? `@${msg.from.username}` : '';
  const sender = [msg.from?.first_name, msg.from?.last_name].filter(Boolean).join(' ');
  const lead =
    `<b>New Interface Report application</b>\n` +
    `<b>ID:</b> ${esc(applicationId)}\n` +
    `<b>Package:</b> ${esc(plan.title)} · $${plan.price}\n` +
    `<b>Applicant:</b> ${esc(sender)} ${esc(username)}\n` +
    `<b>Telegram chat:</b> <code>${esc(msg.chat.id)}</code>\n` +
    `<b>Brief:</b> ${esc(raw)}`;

  console.log('IR_LEAD', JSON.stringify({
    applicationId,
    plan: slug,
    price: plan.price,
    chatId: msg.chat.id,
    username: msg.from?.username || '',
    name: sender,
    brief: raw,
    createdAt: new Date().toISOString()
  }));

  if (LEADS_CHAT_ID) {
    try {
      await tg('sendMessage', {
        chat_id: LEADS_CHAT_ID,
        parse_mode: 'HTML',
        disable_web_page_preview: true,
        text: lead
      });
    } catch (e) {
      console.error('lead-forward-failed', e.message);
    }
  }

  const rows = [];
  const pay = paymentUrl(plan);
  if (pay) rows.push([{ text: `Pay $${plan.price} with PayPal ↗`, url: pay }]);
  rows.push([{ text: 'Sponsor policy ↗', url: `${SITE_URL}/sponsored-content-policy/` }]);
  rows.push([{ text: 'Choose another package', callback_data: 'home' }]);

  return tg('sendMessage', {
    chat_id: msg.chat.id,
    parse_mode: 'HTML',
    disable_web_page_preview: true,
    text:
      `<b>Application received · ${esc(applicationId)}</b>\n\n` +
      `${esc(plan.title)} · $${plan.price}\n\n` +
      'We will review fit, evidence and the proposed angle. If you pay immediately, the payment is still subject to editorial acceptance; an unaccepted order must be refunded rather than published outside policy.\n\n' +
      (pay ? 'PayPal checkout is ready below.' : 'Payment link will be provided after fit review.'),
    reply_markup: { inline_keyboard: rows }
  });
}

async function handleCallback(q) {
  const chatId = q.message?.chat?.id;
  if (!chatId) return;
  await tg('answerCallbackQuery', { callback_query_id: q.id });
  const data = q.data || '';
  if (data === 'home') return sendHome(chatId);
  if (data.startsWith('plan:')) return sendPlan(chatId, data.split(':')[1]);
  if (data.startsWith('apply:')) return askApplication(chatId, data.split(':')[1]);
}

async function handleMessage(msg) {
  const text = (msg.text || '').trim();
  const replied = msg.reply_to_message?.text || '';
  const match = replied.match(/\[\[IR_APPLY:(sponsored|feature|distribution)\]\]/);
  if (match) return handleApplication(msg, match[1]);

  if (text.startsWith('/start')) {
    const slug = text.split(/\s+/)[1];
    if (PLANS[slug]) return sendPlan(msg.chat.id, slug);
    return sendHome(msg.chat.id);
  }
  if (text === '/plans' || text === '/apply' || text === '/pay') return sendHome(msg.chat.id);
  if (text === '/help') {
    return tg('sendMessage', {
      chat_id: msg.chat.id,
      parse_mode: 'HTML',
      disable_web_page_preview: true,
      text:
        `<b>Interface Report</b>\n${SITE_URL}\n\n` +
        `Advertise: ${SITE_URL}/advertise/\n` +
        `Sponsored-content policy: ${SITE_URL}/sponsored-content-policy/\n` +
        `Contact: ${SITE_URL}/contact/`
    });
  }

  return tg('sendMessage', {
    chat_id: msg.chat.id,
    text: 'Use /plans to choose a package or /apply to start a quick application.'
  });
}

module.exports = async function handler(req, res) {
  if (req.method === 'GET') {
    return res.status(200).json({ ok: true, service: 'interface-report-telegram-bot' });
  }
  if (req.method !== 'POST') return res.status(405).json({ ok: false });

  const expectedSecret = process.env.TELEGRAM_WEBHOOK_SECRET;
  if (expectedSecret && req.headers['x-telegram-bot-api-secret-token'] !== expectedSecret) {
    return res.status(401).json({ ok: false });
  }

  try {
    const update = req.body || {};
    if (update.callback_query) await handleCallback(update.callback_query);
    if (update.message) await handleMessage(update.message);
    return res.status(200).json({ ok: true });
  } catch (e) {
    console.error('telegram-webhook-error', e);
    return res.status(200).json({ ok: true });
  }
};
