/**
 * Interface Report lead-mail bridge.
 * Deploy as a Web app: Execute as Me; access Anyone.
 * Set script property IR_WEBHOOK_SECRET to the same random secret stored in
 * Vercel's GOOGLE_SCRIPT_WEBHOOK_SECRET. Never put the secret in this source.
 */
function doPost(e) {
  function reply(ok, id, error) {
    return ContentService.createTextOutput(JSON.stringify({
      ok: ok,
      applicationId: id || '',
      error: error || ''
    })).setMimeType(ContentService.MimeType.JSON);
  }
  var data;
  try {
    if (!e || !e.postData || e.postData.length > 5000) return reply(false, '', 'invalid_request');
    data = JSON.parse(e.postData.contents);
  } catch (_) {
    return reply(false, '', 'invalid_json');
  }
  var secret = PropertiesService.getScriptProperties().getProperty('IR_WEBHOOK_SECRET');
  if (!secret || secret.length < 32 || String(data.secret || '') !== secret) {
    return reply(false, '', 'unauthorized');
  }
  var id = String(data.applicationId || '');
  var email = String(data.email || '').trim().toLowerCase();
  var company = String(data.company || '').replace(/[\r\n]+/g, ' ').trim();
  var goal = String(data.goal || '').trim();
  var packages = {sponsored: 'Sponsored Story', feature: 'Founder / Product Feature', distribution: 'Feature + Distribution'};
  var plan = packages[String(data.package || '')];
  if (!/^IR-WEB-[A-Z0-9]+-[A-F0-9]{8}$/.test(id) ||
      !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) ||
      company.length < 2 || company.length > 160 || !plan || goal.length < 8 || goal.length > 1200) {
    return reply(false, id, 'invalid_payload');
  }
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(5000)) return reply(false, id, 'busy');
  try {
    var cache = CacheService.getScriptCache();
    if (cache.get(id) === 'sent') return reply(true, id, '');
    if (MailApp.getRemainingDailyQuota() < 1) return reply(false, id, 'daily_quota_exceeded');
    MailApp.sendEmail({
      to: 'doctorgebel@gmail.com',
      replyTo: email,
      name: 'Interface Report',
      subject: 'Interface Report request · ' + plan + ' · ' + company,
      body: [
        'Application: ' + id,
        'Package: ' + plan,
        'Company: ' + company,
        'URL: ' + String(data.url || '—').slice(0, 300),
        'Contact: ' + email,
        'Telegram: ' + String(data.telegram || '—').slice(0, 80),
        'Goal / angle:', goal,
        'Source: ' + String(data.source || 'website').slice(0, 80),
        'Submitted: ' + String(data.createdAt || ''),
        '', 'Review editorial fit before publication.'
      ].join('\n')
    });
    cache.put(id, 'sent', 21600);
    return reply(true, id, '');
  } catch (err) {
    console.error('IR lead email failed: ' + id + ' ' + String(err));
    return reply(false, id, 'mail_failed');
  } finally {
    lock.releaseLock();
  }
}
