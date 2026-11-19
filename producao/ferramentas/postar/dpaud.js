(() => [...document.querySelectorAll('audio, source, a[href]')].map(e=>(e.tagName)+' '+(e.src||e.href)).filter(x=>/mp3|wav|audio|blob|storage|supabase|r2|cdn/i.test(x)).slice(0,10))()
