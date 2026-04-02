// LOADER FIX — runs before DOMContentLoaded
(function() {
    function hideLoader() {
        var loader = document.getElementById('luxury-loader');
        if (!loader || loader._done) return;
        loader._done = true;
        loader.style.transition = 'opacity 0.5s ease';
        loader.style.opacity = '0';
        setTimeout(function() { loader.style.display = 'none'; }, 600);
    }
    // If page already loaded (deferred script race condition fix)
    if (document.readyState === 'complete') {
        hideLoader();
    } else {
        window.addEventListener('load', hideLoader);
    }
    // Failsafe: always hide after 3s
    setTimeout(hideLoader, 3000);
})();
