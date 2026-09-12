function track(name,params={}){
  try{
    if(typeof window.gtag==='function')window.gtag('event',name,params);
    else if(Array.isArray(window.dataLayer))window.dataLayer.push({event:name,...params});
  }catch(_){/* Analytics must never block UX. */}
}

function addHoneypot(form){
  if(form.querySelector('[name="company_website"]'))return;
  const wrap=document.createElement('div');
  wrap.className='ir-honeypot';wrap.setAttribute('aria-hidden','true');
  wrap.innerHTML='<label>Company website<input name="company_website" tabindex="-1" autocomplete="off"></label>';
  form.appendChild(wrap);
}

for(const f of document.querySelectorAll('[data-newsletter]')){
  addHoneypot(f);
  f.addEventListener('submit',async e=>{
    e.preventDefault();
    const email=f.querySelector('input[type=email]');
    const note=f.parentElement.querySelector('.form-note')||f.querySelector('.form-note');
    const button=f.querySelector('button[type=submit]');
    if(!email||!email.checkValidity()){email?.reportValidity();return;}
    track('newsletter_signup_start',{source:f.dataset.source||location.pathname});
    const previous=button?.textContent;
    if(button){button.disabled=true;button.textContent='Joining…';}
    if(note)note.textContent='';
    try{
      const params=new URLSearchParams(location.search);
      const response=await fetch('/api/newsletter',{
        method:'POST',
        headers:{'content-type':'application/json'},
        body:JSON.stringify({
          email:email.value,
          company_website:f.querySelector('[name="company_website"]')?.value||'',
          source:f.dataset.source||location.pathname,
          utm_source:params.get('utm_source')||'interfacereport.com',
          utm_medium:params.get('utm_medium')||'website',
          utm_campaign:params.get('utm_campaign')||'newsletter_signup',
          utm_content:params.get('utm_content')||f.dataset.source||location.pathname,
          referring_site:document.referrer||location.href
        })
      });
      const data=await response.json().catch(()=>({}));
      if(!response.ok)throw new Error(data.error||'signup_failed');
      if(note)note.textContent='Check your inbox to confirm your subscription.';
      email.value='';
      track('newsletter_signup_complete',{source:f.dataset.source||location.pathname});
    }catch(error){
      if(note)note.textContent=error.message==='newsletter_not_configured'?'Newsletter signup is being connected. Please use the Newsletter page again shortly.':'We could not add you right now. Please try again.';
      track('newsletter_signup_error',{source:f.dataset.source||location.pathname,error:error.message});
    }finally{
      if(button){button.disabled=false;button.textContent=previous||'Subscribe';}
    }
  });
}

function loadCommerceStyles(){
  for(const href of ['/assets/commerce.css','/assets/growth.css']){
    if(document.querySelector(`link[href="${href}"]`))continue;
    const link=document.createElement('link');link.rel='stylesheet';link.href=href;document.head.appendChild(link);
  }
}

function addPreferredSources(){
  const path=location.pathname;
  const eligible=path==='/'||path.startsWith('/analysis/')||path.startsWith('/topics/')||path.startsWith('/latest');
  if(!eligible||document.querySelector('.ir-preferred-source'))return;
  loadCommerceStyles();
  const section=document.createElement('section');
  section.className='ir-preferred-source';
  section.innerHTML='<div class="wrap ir-preferred-source-inner"><div><div class="kicker">Google Preferred Sources</div><h2>Want more Interface Report in Search?</h2><p>Add Interface Report as a preferred source. Google may highlight our reporting for you in Top Stories, AI Mode and AI Overviews where those features are available.</p></div><div class="ir-preferred-source-action"><div google-add-preferred-source-btn data-theme="light" data-lang="en"></div><a href="https://www.google.com/preferences/source?q=interfacereport.com" rel="noopener" target="_blank">Open source preferences ↗</a></div></div></section>';
  const footer=document.querySelector('.footer');
  if(footer)footer.insertAdjacentElement('beforebegin',section);
  if(!document.querySelector('script[src="https://news.google.com/swg/js/v1/publisher.js"]')){
    const script=document.createElement('script');
    script.async=true;script.src='https://news.google.com/swg/js/v1/publisher.js';
    document.head.appendChild(script);
  }
}

function ensureFooterNewsletterLink(){
  const footer=document.querySelector('.footer');
  if(!footer)return;
  const columns=[...footer.querySelectorAll('.footer-grid>div')];
  const publication=columns.find(col=>col.querySelector('h4')?.textContent.trim()==='Publication');
  if(publication&&!publication.querySelector('a[href="/newsletter/"]')){
    const link=document.createElement('a');link.href='/newsletter/';link.textContent='Newsletter';publication.appendChild(link);
  }
  const standards=columns.find(col=>col.querySelector('h4')?.textContent.trim()==='Standards');
  if(standards&&!standards.querySelector('a[href="/advertising-policy/"]')){
    const link=document.createElement('a');link.href='/advertising-policy/';link.textContent='Advertising Policy';standards.appendChild(link);
  }
}

function advertiserForm(){
  const form=document.createElement('form');
  form.className='ir-advertiser-form';
  form.dataset.advertiserIntake='';
  form.innerHTML=`
    <div class="ir-form-head"><div><span>Commercial intake</span><h3>Send the brief. We review fit before payment.</h3></div><p>No card details here. If accepted, the PayPal payment link follows after editorial review.</p></div>
    <div class="ir-form-grid">
      <label><span>Package</span><select name="package" required><option value="sponsored">Sponsored Story · $99</option><option value="feature">Founder / Product Feature · $149</option><option value="distribution">Feature + Distribution · $199</option></select></label>
      <label><span>Company / product</span><input name="company" autocomplete="organization" required maxlength="160" placeholder="Acme AI"></label>
      <label class="ir-form-wide"><span>Product URL</span><input name="url" type="url" autocomplete="url" maxlength="300" placeholder="https://example.com"></label>
      <label class="ir-form-wide"><span>Campaign goal / proposed angle</span><textarea name="goal" required maxlength="1200" rows="5" placeholder="What are you launching, who is it for, and what should readers understand?"></textarea></label>
      <label><span>Contact email</span><input name="email" type="email" autocomplete="email" required maxlength="254" placeholder="you@company.com"></label>
      <label><span>Telegram (optional)</span><input name="telegram" maxlength="80" placeholder="@username"></label>
    </div>
    <label class="ir-consent"><input type="checkbox" name="consent" required><span>I understand that submission and payment do not guarantee publication or a positive editorial conclusion.</span></label>
    <div class="ir-form-actions"><button type="submit">Submit for editorial review ↗</button><a href="/api/telegram-link?start=site">Prefer Telegram? Open the commercial desk ↗</a></div>
    <div class="ir-form-note" role="status" aria-live="polite"></div>`;
  addHoneypot(form);
  return form;
}

function bindAdvertiserForm(form){
  if(form.dataset.bound==='1')return;form.dataset.bound='1';
  form.addEventListener('submit',async e=>{
    e.preventDefault();
    if(!form.checkValidity()){form.reportValidity();return;}
    const button=form.querySelector('button[type=submit]');
    const note=form.querySelector('.ir-form-note');
    const previous=button.textContent;
    button.disabled=true;button.textContent='Submitting…';note.textContent='';
    const fd=new FormData(form);
    const payload=Object.fromEntries(fd.entries());
    payload.consent=fd.get('consent')==='on';
    payload.source='advertise-page';
    track('advertiser_lead_start',{package:payload.package});
    try{
      const response=await fetch('/api/advertiser-lead',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload)});
      const data=await response.json().catch(()=>({}));
      if(!response.ok)throw new Error(data.error||'submission_failed');
      note.innerHTML=`Application <strong>${data.applicationId}</strong> received. We review fit first; if accepted, the PayPal payment link follows. For the fastest follow-up, continue in <a href="/api/telegram-link?start=${encodeURIComponent(payload.package)}">Telegram ↗</a>.`;
      track('advertiser_lead_complete',{package:payload.package});
      form.reset();
    }catch(error){
      note.textContent='We could not submit the application. Please use the Telegram commercial desk instead.';
      track('advertiser_lead_error',{package:payload.package,error:error.message});
    }finally{button.disabled=false;button.textContent=previous;}
  });
}

function applyCommerce(){
  loadCommerceStyles();
  ensureFooterNewsletterLink();
  addPreferredSources();

  if(!document.querySelector('.ir-telegram-fab')){
    const fab=document.createElement('a');
    fab.className='ir-telegram-fab';
    fab.href='/api/telegram-link?start=site';
    fab.setAttribute('aria-label','Open the Interface Report commercial desk in Telegram');
    fab.innerHTML='<span class="ir-telegram-fab-dot" aria-hidden="true"></span><span>Commercial desk ↗</span>';
    document.body.appendChild(fab);
  }

  if(location.pathname.replace(/\/+$/,'/')==='/advertise/'){
    const slugs=['sponsored','feature','distribution'];
    document.querySelectorAll('.price').forEach((card,index)=>{
      if(card.querySelector('.ir-price-actions'))return;
      const slug=slugs[index]||'site';
      const actions=document.createElement('div');
      actions.className='ir-price-actions';
      actions.innerHTML=`<a href="#commercial-intake" data-package="${slug}">Apply ↗</a><a class="ir-secondary" href="/sponsored-content-policy/">Policy</a>`;
      card.appendChild(actions);
    });

    const prose=document.querySelector('.prose');
    if(prose&&!prose.querySelector('.ir-commerce-strip')){
      const strip=document.createElement('div');
      strip.className='ir-commerce-strip';
      strip.innerHTML='<div><strong>Review first. Pay second.</strong><p>Send one short brief. We check editorial fit and evidence. Accepted applications receive the PayPal payment link.</p></div><a href="#commercial-intake">Start application ↗</a>';
      const firstH2=prose.querySelector('h2');
      if(firstH2)firstH2.insertAdjacentElement('afterend',strip);else prose.prepend(strip);
    }
    if(prose&&!document.querySelector('[data-advertiser-intake]')){
      const anchor=document.createElement('div');anchor.id='commercial-intake';anchor.className='ir-form-anchor';
      const form=advertiserForm();
      anchor.appendChild(form);prose.appendChild(anchor);bindAdvertiserForm(form);
      document.querySelectorAll('[data-package]').forEach(link=>link.addEventListener('click',()=>{
        const select=form.querySelector('[name="package"]');if(select)select.value=link.dataset.package;
      }));
    }
  }
}

applyCommerce();
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',applyCommerce,{once:true});
window.addEventListener('load',applyCommerce,{once:true});
