(() => { const t=document.querySelector('[role=dialog] div[contenteditable=true], [role=dialog] textarea'); return (t.value||t.innerText) })()
