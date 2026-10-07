chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'show_warning') {
        if (document.getElementById('phishguard-warning')) return;

        const overlay = document.createElement('div');
        overlay.id = 'phishguard-warning';
        overlay.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(220, 38, 38, 0.96); color: white; z-index: 2147483647;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            font-family: system-ui, -apple-system, sans-serif; text-align: center;
        `;
        
        const reasonsHtml = message.data.reasons.map(r => `<li>${r}</li>`).join('');
        
        overlay.innerHTML = `
            <h1 style="font-size: 3rem; margin-bottom: 10px;">🚨 Deceptive Site Ahead</h1>
            <p style="font-size: 1.5rem; max-width: 600px;">PhishGuard has flagged this page as dangerous (Score: ${message.data.score}/100).</p>
            <div style="background: rgba(0,0,0,0.3); padding: 25px; border-radius: 12px; margin: 20px 0; text-align: left; font-size: 1.2rem;">
                <h3 style="margin-top: 0;">Explainable AI Analysis:</h3>
                <ul>${reasonsHtml}</ul>
            </div>
            <div style="margin-top: 20px;">
                <button id="phishguard-leave" style="padding: 15px 30px; font-size: 1.2rem; background: white; color: #DC2626; border: none; border-radius: 8px; cursor: pointer; margin-right: 15px; font-weight: bold;">Take me to safety</button>
                <button id="phishguard-proceed" style="padding: 15px 30px; font-size: 1.2rem; background: transparent; color: white; border: 2px solid white; border-radius: 8px; cursor: pointer;">Proceed anyway</button>
            </div>
        `;
        
        document.body.appendChild(overlay);
        document.body.style.overflow = 'hidden'; 
        
        document.getElementById('phishguard-leave').addEventListener('click', () => window.history.back());
        document.getElementById('phishguard-proceed').addEventListener('click', () => {
            overlay.remove();
            document.body.style.overflow = 'auto';
        });
    }
});