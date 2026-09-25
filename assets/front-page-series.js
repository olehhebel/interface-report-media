(()=>{
  const root=document.getElementById('front-page-series');
  if(!root)return;
  const viewport=root.querySelector('.series-viewport');
  const track=root.querySelector('.series-track');
  const group=track.querySelector('.series-group');
  const clone=group.cloneNode(true);
  clone.setAttribute('aria-hidden','true');
  clone.querySelectorAll('a,button').forEach(link=>link.tabIndex=-1);
  // The cloned invitation remains clickable for sighted pointer users.
  clone.querySelectorAll('[data-package]').forEach(link=>link.addEventListener('click',event=>{
    event.preventDefault();
    group.querySelector('[data-package="launch-monthly"]')?.click();
  }));
  track.appendChild(clone);

  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
  let pausedUntil=0, visible=true, last=0;
  const pause=(duration=7000)=>{pausedUntil=performance.now()+duration;};
  const advance=(direction)=>{
    pause();
    const width=group.getBoundingClientRect().width;
    if(direction<0&&viewport.scrollLeft<340)viewport.scrollLeft+=width;
    viewport.scrollBy({left:direction*Math.min(370,viewport.clientWidth*.82),behavior:reduced.matches?'instant':'smooth'});
  };
  root.querySelector('[data-series-prev]').addEventListener('click',()=>advance(-1));
  root.querySelector('[data-series-next]').addEventListener('click',()=>advance(1));
  viewport.addEventListener('mouseenter',()=>pause(60000));
  viewport.addEventListener('mouseleave',()=>pause(2500));
  viewport.addEventListener('pointerdown',()=>pause(9000));
  viewport.addEventListener('wheel',()=>pause(6000),{passive:true});
  viewport.addEventListener('focusin',()=>pause(60000));
  viewport.addEventListener('focusout',()=>pause(2500));
  new IntersectionObserver(entries=>{visible=entries[0]?.isIntersecting||false;},{threshold:.05}).observe(root);
  const tick=now=>{
    if(last&&!reduced.matches&&visible&&now>pausedUntil){
      viewport.scrollLeft+=Math.min(now-last,64)*.038;
      const width=group.getBoundingClientRect().width;
      if(width&&viewport.scrollLeft>=width)viewport.scrollLeft-=width;
    }
    last=now;
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
})();
