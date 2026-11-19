(() => [...document.querySelectorAll('ytcp-video-row')].map(r=>r.innerText.replace(/\s+/g,' ').slice(0,220)))()
