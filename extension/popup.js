// ============================================
// FAKE REVIEW DETECTOR - Popup Script
// ============================================

async function analyze() {
  const btn = document.getElementById('analyzeBtn');
  const status = document.getElementById('status');
  const result = document.getElementById('result');

  btn.disabled = true;
  btn.textContent = '⏳ Analyzing...';
  status.textContent = 'Scanning reviews on this page...';
  result.style.display = 'none';

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    chrome.tabs.sendMessage(tab.id, { action: 'analyze' }, (response) => {
      btn.disabled = false;
      btn.textContent = '🔍 Analyze Reviews';

      if (chrome.runtime.lastError || !response) {
        status.textContent = '❌ Could not connect. Make sure you are on a product page.';
        return;
      }

      if (!response.success) {
        status.textContent = response.message || '⚠️ Something went wrong.';
        return;
      }

      const data = response.result;
      const colors = { green: '#27ae60', orange: '#f39c12', red: '#e74c3c' };
      const color = colors[data.trust_color] || colors.orange;

      document.getElementById('trustScore').textContent = `${data.trust_score}/100`;
      document.getElementById('trustScore').style.color = color;
      document.getElementById('trustLabel').textContent = data.trust_label;
      document.getElementById('trustLabel').style.color = color;
      document.getElementById('totalCount').textContent = data.total_reviews;
      document.getElementById('realCount').textContent = data.real_count;
      document.getElementById('fakeCount').textContent = data.fake_count;

      status.textContent = `✅ Analysis complete!`;
      result.style.display = 'block';
    });

  } catch (err) {
    btn.disabled = false;
    btn.textContent = '🔍 Analyze Reviews';
    status.textContent = '❌ Error. Try refreshing the page.';
  }
}
