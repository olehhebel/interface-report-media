module.exports = async function handler(req, res) {
  const username = (process.env.TELEGRAM_BOT_USERNAME || '').replace(/^@/, '');
  if (!username) return res.redirect(302, '/advertise/');
  const start = String(req.query?.start || 'site').replace(/[^a-z0-9_-]/gi, '').slice(0, 40) || 'site';
  return res.redirect(302, `https://t.me/${username}?start=${encodeURIComponent(start)}`);
};
