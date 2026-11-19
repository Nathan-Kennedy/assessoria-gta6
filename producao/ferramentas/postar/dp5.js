(() => { const all=[...document.querySelectorAll('*')].map(e=>e.innerText||'').join(' '); return [/clonar|clone|sua voz|voz personalizada|upload de voz/i.test(document.body.innerText)] })()
