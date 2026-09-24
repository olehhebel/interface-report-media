// Website-only intake. The Apps Script and shared secret stay server-side.
module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  const endpoint = process.env.GOOGLE_NEWSLETTER_WEBAPP_URL;
  const secret = process.env.GOOGLE_NEWSLETTER_SECRET;
  const available = /^https:\/\/script\.google\.com\/macros\/s\/[A-Za-z0-9_-]+\/exec$/.test(endpoint || '') && Boolean(secret && secret.length >= 32);
  if (req.method === 'GET') return res.status(200).json({ ok: true, available });
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'method_not_allowed' });
  if (!available) return res.status(503).json({ ok: false, error: 'subscription_unavailable' });
  const origin = req.headers.origin;
  if (origin && !/^https:\/\/(?:www\.)?interfacereport\.com$/.test(origin)) return res.status(403).json({ ok: false, error: 'origin_not_allowed' });
  if (Number(req.headers['content-length'] || 0) > 2048) return res.status(413).json({ ok: false, error: 'payload_too_large' });
  let body;
  try { body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {}); }
  catch (_) { return res.status(400).json({ ok: false, error: 'invalid_payload' }); }
  if (body.company_website) return res.status(200).json({ ok: true, status: 'confirmation_required' });
  const email = String(body.email || '').trim().toLowerCase();
  if (email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return res.status(400).json({ ok: false, error: 'invalid_email' });
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ secret, email, source: String(body.source || 'website').slice(0, 120) }),
      signal: AbortSignal.timeout(12000)
    });
    const payload = await response.json();
    if (!response.ok || !payload.ok || payload.status !== 'confirmation_required') throw new Error('intake_failed');
    return res.status(200).json({ ok: true, status: 'confirmation_required' });
  } catch (error) {
    console.error('newsletter_intake_failed', error && error.message);
    return res.status(502).json({ ok: false, error: 'subscription_unavailable' });
  }
};
