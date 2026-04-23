async function analyze() {
  const btn = document.getElementById('analyzeBtn');
  const status = document.getElementById('status');
  const result = document.getElementById('result');

  btn.disabled = true;
  btn.textContent = '⏳ Analyzing...';
  status.textContent = 'Scanning reviews...';
  result.style.display = 'none';

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: async () => {
        const reviews = [];
        document.querySelectorAll('[data-hook="review-body"] span').forEach(el => {
          const text = el.innerText?.trim();
          if (text && text.length > 20) reviews.push(text);
        });

        if (reviews.length === 0) return { error: 'No reviews found on this page' };

        try {
          const response = await fetch('http://localhost:8080/analyze-bulk', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reviews: reviews.slice(0, 20) })
          });
          return await response.json();
        } catch (e) {
          return { error: 'API not reachable: ' + e.message };
        }
      }
    });

    btn.disabled = false;
    btn.textContent = '🔍 Analyze Reviews';

    const data = results[0].result;

    if (!data || data.error) {
      status.textContent = '⚠️ ' + (data?.error || 'Something went wrong');
      return;
    }

    const colors = { green: '#27ae60', orange: '#f39c12', red: '#e74c3c' };
    const color = colors[data.trust_color] || colors.orange;

    document.getElementById('trustScore').textContent = data.trust_score + '/100';
    document.getElementById('trustScore').style.color = color;
    document.getElementById('trustLabel').textContent = data.trust_label;
    document.getElementById('trustLabel').style.color = color;
    document.getElementById('totalCount').textContent = data.total_reviews;
    document.getElementById('realCount').textContent = data.real_count;
    document.getElementById('fakeCount').textContent = data.fake_count;

    status.textContent = '✅ Analysis complete!';
    result.style.display = 'block';

  } catch (err) {
    btn.disabled = false;
    btn.textContent = '🔍 Analyze Reviews';
    status.textContent = '❌ Error: ' + err.message;
  }
}
