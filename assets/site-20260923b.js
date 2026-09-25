const BRAND_LOGO='/assets/interface-report-mark.jpg';
const BRAND_LOGO_ABS='https://interfacereport.com/assets/interface-report-mark.jpg';
const FAVICON='/assets/favicon.png';

function applyBranding(){
  const headerBrand=document.querySelector('.brand');
  if(headerBrand){
    headerBrand.innerHTML='';
    const img=document.createElement('img');
    img.src=BRAND_LOGO;img.alt='';img.width=925;img.height=1055;img.className='ir-brand-symbol';
    const name=document.createElement('span');name.textContent='Interface Report';headerBrand.append(img,name);
  }
  for(const footerBrand of document.querySelectorAll('.footer-brand')){
    footerBrand.innerHTML='';
    const img=document.createElement('img');
    img.src=BRAND_LOGO;img.alt='';img.width=925;img.height=1055;img.className='ir-brand-symbol';
    const name=document.createElement('span');name.textContent='Interface Report';footerBrand.append(img,name);
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
          value.logo={"@type":"ImageObject","url":BRAND_LOGO_ABS,"contentUrl":BRAND_LOGO_ABS,"width":925,"height":1055};
          value.image={"@type":"ImageObject","url":BRAND_LOGO_ABS,"contentUrl":BRAND_LOGO_ABS,"width":925,"height":1055};
        }
        Object.values(value).forEach(visit);
      };
      visit(data);node.textContent=JSON.stringify(data);
    }catch(_){/* Keep malformed schema untouched. */}
  }
}

applyBranding();
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',applyBranding,{once:true});
window.addEventListener('load',applyBranding,{once:true});
setTimeout(applyBranding,250);

const menu=document.querySelector('.menu');const nav=document.querySelector('.nav');
if(menu&&nav){menu.addEventListener('click',()=>{const open=nav.dataset.open==='1';nav.dataset.open=open?'0':'1';nav.style.display=open?'none':'flex';nav.style.position='absolute';nav.style.top='66px';nav.style.left='0';nav.style.right='0';nav.style.padding='20px';nav.style.flexDirection='column';nav.style.background='#F6F6F2';nav.style.borderBottom='1px solid rgba(8,10,13,.14)';menu.setAttribute('aria-expanded',String(!open));});}

if(!document.querySelector('script[src="/assets/growth-20260925.js?v=frontpage10"]')){
  const growth=document.createElement('script');growth.src='/assets/growth-20260925.js?v=frontpage10';growth.async=false;document.head.appendChild(growth);
}
