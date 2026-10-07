chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && tab.url.startsWith('http')) {
        try {
            const response = await fetch('http://localhost:8000/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: tab.url })
            });
            
            const data = await response.json();
            
            if (data.verdict === 'safe') {
                chrome.action.setBadgeBackgroundColor({ tabId, color: '#10B981' });
                chrome.action.setBadgeText({ tabId, text: 'SAFE' });
            } else if (data.verdict === 'phishing') {
                chrome.action.setBadgeBackgroundColor({ tabId, color: '#EF4444' });
                chrome.action.setBadgeText({ tabId, text: 'RISK' });
                
                // Send a message to content.js to trigger the red overlay
                chrome.tabs.sendMessage(tabId, { action: 'show_warning', data: data });
            } else {
                chrome.action.setBadgeBackgroundColor({ tabId, color: '#F59E0B' });
                chrome.action.setBadgeText({ tabId, text: 'WARN' });
            }
            
            // Save the result for the popup UI
            chrome.storage.local.set({ ['result_' + tabId]: data });
            
        } catch (error) {
            console.error("PhishGuard API Error:", error);
        }
    }
});