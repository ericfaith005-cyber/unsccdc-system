(function() {
    console.log("Sovereign Identity Engine Initializing...");
    
    function injectSovereignSymbols() {
        // 1. 🇺🇬 REPLACE THE MAN WITH THE WAVING NATIONAL FLAG
        // This targets the specific sidebar image and the top navbar avatar
        const avatars = document.querySelectorAll('.user-panel img, .user-image, .img-circle');
        
        // High-Quality Animated Uganda Flag
        const wavingFlagUrl = "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3R6eHh6eHh6eHh6eHh6eHh6eHh6eHh6eHh6eHh6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKMGpxx6D8YvE4M/giphy.gif";

        avatars.forEach(img => {
            img.src = wavingFlagUrl;
            img.style.border = "2px solid #D4AF37"; // Imperial Gold Border
            img.style.objectFit = "cover";
            img.style.boxShadow = "0 0 15px rgba(212, 175, 55, 0.5)"; // Gold Aura
        });

        // 2. 🏛️ RENAME "admin" TO "NATIONAL REGISTRAR"
        // This looks for the text next to the image
        const userTexts = document.querySelectorAll('.info a, .d-block, .user-panel .info');
        userTexts.forEach(text => {
            if (text.innerText.toLowerCase().includes("admin")) {
                text.innerHTML = '<span style="color: #D4AF37; font-weight: 900; letter-spacing: 1px;">NATIONAL REGISTRAR</span>';
            }
        });
    }

    // Run the injection immediately and then every 2 seconds to ensure it stays
    injectSovereignSymbols();
    setInterval(injectSovereignSymbols, 2000);
})();