chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
    const tab = tabs[0];
    
    chrome.storage.local.get(['result_' + tab.id], (data) => {
        const result = data['result_' + tab.id];
        
        const gauge = document.getElementById('gauge');
        const verdictText = document.getElementById('verdict-text');
        const reasonsList = document.getElementById('reasons-list');
        const latencyText = document.getElementById('latency');
        
        if (result) {
            gauge.textContent = result.score;
            gauge.className = `gauge ${result.verdict}`;
            verdictText.textContent = result.verdict;
            verdictText.style.color = gauge.style.color;
            
            reasonsList.innerHTML = result.reasons.map(r => `<li>${r}</li>`).join('');
            latencyText.textContent = `⚡ AI Inference Latency: ${result.latency_ms} ms`;
        } else {
            verdictText.textContent = "Safe / Untested";
            gauge.className = 'gauge safe';
            gauge.textContent = '0';
            reasonsList.innerHTML = '<li>Internal browser page or whitelist.</li>';
        }
    });
});