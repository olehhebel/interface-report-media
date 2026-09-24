// Subscription intake is paused until the self-managed Google workflow is deployed and verified.
// Never acknowledge or store an address while delivery and consent are unconfigured.
module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'method_not_allowed' });
  return res.status(503).json({ ok: false, error: 'subscription_unavailable' });
};
