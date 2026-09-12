async function resolveUsername() {
  const configured = (process.env.TELEGRAM_BOT_USERNAME || '').replace(/^@/, '').trim();
  if (configured) return configured;

  // TELEGRAM_BOT_TOKEN is already required by the webhook. Resolve the public
  // username from Telegram when a separate username variable was not added in
  // Vercel, so every website CTA still has a working destination.
  const token = process.env.TELEGRAM_BOT_TOKEN;
  if (!token) return '';

  try {
    const response = await fetch(`https://api.telegram.org/bot${token}/getMe`, {
      signal: AbortSignal.timeout(4000)
    });
    const data = await response.json();
    return data?.ok ? String(data.result?.username || '').replace(/^@/, '') : '';
  } catch (error) {
    console.error('telegram-username-resolution-failed', error?.message || error);
    return '';
  }
}

module.exports = async function handler(req, res) {
  const username = await resolveUsername();
  if (!username) return res.redirect(302, '/contact/?reason=telegram-unavailable');
  const start = String(req.query?.start || 'site').replace(/[^a-z0-9_-]/gi, '').slice(0, 40) || 'site';
  res.setHeader('Cache-Control', 'no-store');
  return res.redirect(302, `https://t.me/${username}?start=${encodeURIComponent(start)}`);
};
