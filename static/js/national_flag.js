(function() {
    console.log("Sovereign Flag Engine Initializing...");
    
    function injectSovereignSymbols() {
        // 1. 🇺🇬 REPLACE ALL USER AVATARS WITH THE WAVING FLAG
        // This targets the top navbar and the sidebar profile pics
        const avatars = document.querySelectorAll('.user-image, .img-circle, .user-panel img');
        
        const wavingFlagUrl = "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3R6eHh6eHh6eHh6eHh6eHh6eHh6eHh6eHh6eHh6eHh6eHh6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKMGpxx6D8YvE4M/giphy.gif";

        avatars.forEach(img => {
            img.src = wavingFlagUrl;
            img.style.border = "2px solid #D4AF37"; // Add a Gold Border for prestige
            img.style.objectFit = "cover";
        });

        // 2. Fix the "Admin" text if needed
        const userTexts = document.querySelectorAll('.info a, .d-block');
        userTexts.forEach(text => {
            if (text.innerText.includes("admin")) {
                text.innerText = "NATIONAL REGISTRAR";
                text.style.color = "#D4AF37";
                text.style.fontWeight = "900";
            }
        });
    }

    // Run the injection
    setInterval(injectSovereignSymbols, 1000); // Check every second to ensure it stays replaced
})();