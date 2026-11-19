(() => { const i=[...document.querySelectorAll('input[type=file]')].findIndex(e=>/video\/mp4/.test(e.accept)); return i; })()
