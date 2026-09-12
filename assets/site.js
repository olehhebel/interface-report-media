const BRAND_LOGO='/assets/interface-report-logo.png';
const BRAND_LOGO_ABS='https://interfacereport.com/assets/interface-report-logo.png';
const FAVICON='/assets/favicon.png';

function applyBranding(){
  const headerBrand=document.querySelector('.brand');
  if(headerBrand){
    headerBrand.innerHTML='';
    const img=document.createElement('img');
    img.src=BRAND_LOGO;img.alt='Interface Report';img.width=1536;img.height=768;
    img.style.cssText='width:clamp(150px,14vw,210px);height:auto;max-height:56px;object-fit:contain;object-position:left center;display:block';
    headerBrand.appendChild(img);
  }
  for(const footerBrand of document.querySelectorAll('.footer-brand')){
    footerBrand.innerHTML='';
    const img=document.createElement('img');
    img.src=BRAND_LOGO;img.alt='Interface Report';img.width=1536;img.height=768;
    img.style.cssText='width:min(280px,100%);height:auto;object-fit:contain;object-position:left center;display:block';
    footerBrand.appendChild(img);
  }
  for(const oldIcon of [...document.querySelectorAll('link[rel~="icon"],link[rel="shortcut icon"]')]) oldIcon.remove();
  const icon=document.createElement('link');icon.rel='icon';icon.type='image/png';icon.href=FAVICON;document.head.appendChild(icon);
  for(const node of document.querySelectorAll('script[type="application/ld+json"]')){
    try{
      const data=JSON.parse(node.textContent);
      const visit=(value)=>{
        if(!value||typeof value!=='object')return;
        if(Array.isArray(value)){value.forEach(visit);return;}
        const types=Array.isArray(value['@type'])?value['@type']:[value['@type']];
        if(types.includes('Organization')||types.includes('NewsMediaOrganization')){
          value.logo={"@type":"ImageObject","url":BRAND_LOGO_ABS,"contentUrl":BRAND_LOGO_ABS,"width":1536,"height":768};
          value.image={"@type":"ImageObject","url":BRAND_LOGO_ABS,"contentUrl":BRAND_LOGO_ABS,"width":1536,"height":768};
        }
        Object.values(value).forEach(visit);
      };
      visit(data);node.textContent=JSON.stringify(data);
    }catch(_){/* Keep malformed third-party schema untouched. */}
  }
}

applyBranding();
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',applyBranding,{once:true});
window.addEventListener('load',applyBranding,{once:true});
setTimeout(applyBranding,250);

const menu=document.querySelector('.menu');const nav=document.querySelector('.nav');
if(menu&&nav){menu.addEventListener('click',()=>{const open=nav.dataset.open==='1';nav.dataset.open=open?'0':'1';nav.style.display=open?'none':'flex';nav.style.position='absolute';nav.style.top='66px';nav.style.left='0';nav.style.right='0';nav.style.padding='20px';nav.style.flexDirection='column';nav.style.background='#F6F6F2';nav.style.borderBottom='1px solid rgba(8,10,13,.14)';menu.setAttribute('aria-expanded',String(!open));});}
for(const f of document.querySelectorAll('[data-newsletter]')){f.addEventListener('submit',e=>{e.preventDefault();const email=f.querySelector('input[type=email]');const note=f.parentElement.querySelector('.form-note');if(!email.checkValidity()){email.reportValidity();return;}note.textContent='Launch-list capture will be connected before the public launch.';email.value='';});}

function applyCommerce(){
  if(!document.querySelector('link[href="/assets/commerce.css"]')){
    const link=document.createElement('link');
    link.rel='stylesheet';link.href='/assets/commerce.css';document.head.appendChild(link);
  }

  if(!document.querySelector('.ir-telegram-fab')){
    const fab=document.createElement('a');
    fab.className='ir-telegram-fab';
    fab.href='/api/telegram-link?start=site';
    fab.setAttribute('aria-label','Apply or pay through the Interface Report Telegram bot');
    fab.innerHTML='<span class="ir-telegram-fab-dot" aria-hidden="true"></span><span>Apply / pay in Telegram ↗</span>';
    document.body.appendChild(fab);
  }

  if(location.pathname.replace(/\/+$/,'/')==='/advertise/'){
    const slugs=['sponsored','feature','distribution'];
    document.querySelectorAll('.price').forEach((card,index)=>{
      if(card.querySelector('.ir-price-actions'))return;
      const slug=slugs[index]||'site';
      const actions=document.createElement('div');
      actions.className='ir-price-actions';
      actions.innerHTML=`<a href="/api/telegram-link?start=${slug}">Apply / pay ↗</a><a class="ir-secondary" href="/sponsored-content-policy/">Policy</a>`;
      card.appendChild(actions);
    });

    const prose=document.querySelector('.prose');
    if(prose&&!prose.querySelector('.ir-commerce-strip')){
      const strip=document.createElement('div');
      strip.className='ir-commerce-strip';
      strip.innerHTML='<div><strong>Ready to publish?</strong><p>Choose a package, send one short brief and continue to secure PayPal checkout inside Telegram.</p></div><a href="/api/telegram-link?start=site">Open commercial desk ↗</a>';
      const firstH2=prose.querySelector('h2');
      if(firstH2)firstH2.insertAdjacentElement('afterend',strip);else prose.prepend(strip);
    }
  }
}

applyCommerce();
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',applyCommerce,{once:true});
window.addEventListener('load',applyCommerce,{once:true});
