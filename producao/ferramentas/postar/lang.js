(async () => { const d=document.querySelector('ytcp-uploads-dialog'); const sl=ms=>new Promise(r=>setTimeout(r,ms));
 const pick=async(trig, rx)=>{ trig.scrollIntoView({block:'center'}); trig.click(); await sl(900);
   const it=[...document.querySelectorAll('tp-yt-paper-item, ytcp-text-menu tp-yt-paper-item, [role=option]')].filter(e=>e.offsetParent && rx.test(e.innerText.trim())); if(it[0]) it[0].click(); await sl(600); return it.map(e=>e.innerText.trim()).slice(0,3); };
 const r={};
 r.lang=await pick(d.querySelector('#language-input ytcp-dropdown-trigger, #language-input'), /^Português \(Brasil\)$/);
 r.cat=await pick(d.querySelector('#category ytcp-dropdown-trigger, #category'), /^Jogos$/);
 r.now=[d.querySelector('#language-input')?.innerText.replace(/\s+/g,' '), d.querySelector('#category')?.innerText.replace(/\s+/g,' ')];
 return r; })()
