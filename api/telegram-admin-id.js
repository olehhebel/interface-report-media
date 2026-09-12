const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;

module.exports = async function handler(req, res) {
  if (req.method !== 'GET') return res.status(405).json({ ok: false });
  if (!process.env.TELEGRAM_SETUP_SECRET || req.query?.key !== process.env.TELEGRAM_SETUP_SECRET) {
    return res.status(401).json({ ok: false });
  }
  if (!BOT_TOKEN) return res.status(500).json({ ok: false, error: 'TELEGRAM_BOT_TOKEN missing' });

  const r = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/getUpdates?limit=25&timeout=0`);
  const data = await r.json();
  if (!data.ok) return res.status(502).json({ ok: false, error: data.description || 'Telegram API error' });

  const chats = [];
  const seen = new Set();
  for (const update of data.result || []) {
    const msg = update.message || update.edited_message || update.callback_query?.message;
    const chat = msg?.chat;
    const from = update.message?.from || update.edited_message?.from || update.callback_query?.from;
    if (!chat || chat.type !== 'private' || seen.has(chat.id)) continue;
    seen.add(chat.id);
    chats.push({
      chatId: chat.id,
      username: from?.username || '',
      name: [from?.first_name, from?.last_name].filter(Boolean).join(' '),
      text: update.message?.text || '',
      date: update.message?.date || null
    });
  }

  return res.status(200).json({ ok: true, chats });
};
