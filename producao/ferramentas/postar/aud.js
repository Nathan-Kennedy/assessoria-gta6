(async () => { const d=document.querySelector('ytcp-uploads-dialog');
 const nk=d.querySelector('tp-yt-paper-radio-button[name=VIDEO_MADE_FOR_KIDS_NOT_MFK]'); nk?.click();
 const mais=d.querySelector('#toggle-button'); mais?.scrollIntoView({block:'center'}); mais?.click(); await new Promise(r=>setTimeout(r,1500));
 const out={nk:!!nk, mais:!!mais};
 out.altered=[...d.querySelectorAll('tp-yt-paper-radio-button')].map(r=>[r.getAttribute('name'),r.innerText.trim().slice(0,40),r.checked||r.hasAttribute('checked')]);
 out.tags=!!d.querySelector('#tags-container input, ytcp-form-input-container#tags-container input, input[aria-label*=Tags], input[aria-label*=tag]');
 return out; })()
