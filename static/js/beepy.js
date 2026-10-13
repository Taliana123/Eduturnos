(() => {
    if (document.getElementById('livebeep-script')) return;
    const wireTabs = () => {
        document.querySelectorAll('#lbContact .lbTab[onclick]').forEach((tab) => {
            const match = /^_lbContact\.tabLoad\('([a-z]+)'\)$/.exec(tab.getAttribute('onclick'));
            if (!match || !['chat', 'email', 'callback'].includes(match[1])) return;
            const key = match[1];
            tab.removeAttribute('onclick');
            tab.removeAttribute('onmouseover');
            tab.removeAttribute('onmouseout');
            tab.addEventListener('click', () => window._lbContact?.tabLoad(key));
            tab.addEventListener('mouseover', () => window._lbContact?.tabOver(key));
            tab.addEventListener('mouseout', () => window._lbContact?.tabOut(key));
        });
        document.querySelectorAll('#lbContact .lbPowered [onclick]').forEach((link) => link.removeAttribute('onclick'));
    };
    const observer = new MutationObserver(wireTabs);
    observer.observe(document.documentElement, { childList: true, subtree: true });
    const script = document.createElement('script');
    script.id = 'livebeep-script';
    script.src = 'https://www.beepychatbot.com/' + location.hostname + '/eye.js?cid=27952&iidf=21859&lang=es';
    script.async = true;
    document.head.append(script);
})();