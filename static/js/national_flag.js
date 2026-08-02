(function() {
    console.log("Sovereign Flag Engine Initializing...");
    
    function injectVideo() {
        if (document.getElementById('bg-video')) return;

        var video = document.createElement('video');
        video.id = 'bg-video';
        video.autoplay = true;
        video.muted = true;
        video.loop = true;
        video.setAttribute('playsinline', '');
        
        // 🇺🇬 HIGH-DEFINITION WAVING UGANDA FLAG
        var source = document.createElement('source');
        source.src = 'https://assets.mixkit.co/videos/preview/mixkit-flag-of-uganda-waving-in-the-wind-32538-large.mp4';
        source.type = 'video/mp4';
        
        video.appendChild(source);
        document.body.prepend(video);
    }

    // Run on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectVideo);
    } else {
        injectVideo();
    }
})();