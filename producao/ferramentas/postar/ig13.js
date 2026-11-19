(() => { const t=document.querySelector('[role=dialog] div[contenteditable=true], [role=dialog] textarea'); if(!t) return 'sem'; t.focus(); return t.tagName; })()
