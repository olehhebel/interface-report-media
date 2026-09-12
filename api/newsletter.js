const API_BASE = 'https://api.beehiiv.com/v2';

function validEmail(value = '') {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value).trim());
}

function clean(value = '', max = 180) {
  return String(value).trim().slice(0, max);
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'method_not_allowed' });

  const body = req.body || {};
  if (body.company_website) return res.status(200).json({ ok: true });

  const email = clean(body.email, 254).toLowerCase();
  if (!validEmail(email)) return res.status(400).json({ ok: false, error: 'invalid_email' });

  const apiKey = process.env.BEEHIIV_API_KEY;
  const publicationId = process.env.BEEHIIV_PUBLICATION_ID;
  if (!apiKey || !publicationId) {
    return res.status(503).json({ ok: false, error: 'newsletter_not_configured' });
  }

  const payload = {
    email,
    reactivate_existing: false,
    send_welcome_email: true,
    double_opt_override: 'on',
    utm_source: clean(body.utm_source || 'interfacereport.com', 120),
    utm_medium: clean(body.utm_medium || 'website', 120),
    utm_campaign: clean(body.utm_campaign || 'newsletter_signup', 120),
    utm_content: clean(body.utm_content || body.source || '', 120),
    referring_site: clean(body.referring_site || req.headers.referer || 'https://interfacereport.com/', 500)
  };

  try {
    const response = await fetch(`${API_BASE}/publications/${encodeURIComponent(publicationId)}/subscriptions`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      console.error('beehiiv-subscribe-failed', response.status, data);
      return res.status(response.status === 429 ? 429 : 502).json({ ok: false, error: 'provider_error' });
    }

    return res.status(200).json({ ok: true, status: data?.data?.status || 'pending_confirmation' });
  } catch (error) {
    console.error('beehiiv-subscribe-error', error?.message || error);
    return res.status(502).json({ ok: false, error: 'provider_unavailable' });
  }
};
