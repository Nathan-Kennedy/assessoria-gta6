(() => { const d=document.querySelector('ytcp-uploads-dialog');
 ['VIDEO_PAID_PRODUCT_PLACEMENT_NO','VIDEO_HAS_ALTERED_CONTENT_NO'].forEach(n=>d.querySelector(`tp-yt-paper-radio-button[name=${n}]`).click());
 const t=d.querySelector('#tags-container input'); t.scrollIntoView({block:'center'}); t.focus();
 const cat=d.querySelector('#category'); return cat?cat.innerText.replace(/\s+/g,' '):'?'; })()
