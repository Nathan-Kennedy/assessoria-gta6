(() => { const c=[...document.querySelectorAll('div')].find(d=>/darkplanner_audio_09d2aeed/.test(d.innerText||'') && d.innerText.length<300); return c? c.innerText.replace(/\s+/g,' '):'?' })()
