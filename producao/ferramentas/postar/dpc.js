(() => [...document.querySelectorAll('h3,h4,div,span')].filter(e=>e.children.length===0 && /Ana Alice/i.test(e.innerText||'')).map(e=>e.innerText.trim()).slice(0,6))()
