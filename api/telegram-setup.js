const SITE_URL = process.env.SITE_URL || 'https://interfacereport.com';
const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;

async function tg(method, payload) {
  const r = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/${method}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return r.json();
}

module.exports = async function handler(req, res) {
  if (req.method !== 'GET' && req.method !== 'POST') return res.status(405).json({ ok: false });
  if (!BOT_TOKEN) return res.status(500).json({ ok: false, error: 'TELEGRAM_BOT_TOKEN missing' });
  if (!process.env.TELEGRAM_SETUP_SECRET || req.query?.key !== process.env.TELEGRAM_SETUP_SECRET) {
    return res.status(401).json({ ok: false });
  }

  const webhookUrl = `${SITE_URL.replace(/\/$/, '')}/api/telegram`;
  const secretToken = process.env.TELEGRAM_WEBHOOK_SECRET || undefined;
  const webhook = await tg('setWebhook', {
    url: webhookUrl,
    secret_token: secretToken,
    allowed_updates: ['message', 'callback_query'],
    drop_pending_updates: false
  });
  const commands = await tg('setMyCommands', {
    commands: [
      { command: 'start', description: 'Open packages and application flow' },
      { command: 'plans', description: 'View publication packages' },
      { command: 'apply', description: 'Submit a quick application' },
      { command: 'pay', description: 'Payment options' },
      { command: 'help', description: 'Contact and policies' }
    ]
  });

  return res.status(200).json({ ok: Boolean(webhook.ok && commands.ok), webhook, commands, webhookUrl });
};
