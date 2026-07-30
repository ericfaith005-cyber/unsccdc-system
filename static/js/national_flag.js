document.addEventListener("DOMContentLoaded", function() {
    var video = document.createElement('video');
    video.id = 'bg-video';
    video.autoplay = true;
    video.muted = true;
    video.loop = true;
    video.playsinline = true;
    
    // 🇺🇬 High-Quality Waving Uganda Flag
    var source = document.createElement('source');
    source.src = 'https://assets.mixkit.co/videos/preview/mixkit-flag-of-uganda-waving-in-the-wind-32538-large.mp4';
    source.type = 'video/mp4';
    
    video.appendChild(source);
    document.body.appendChild(video);
});