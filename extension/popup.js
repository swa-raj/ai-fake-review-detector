const API_URL = "https://ai-fake-review-detector-7kh1.onrender.com";

async function analyze() {
  const btn = document.getElementById('analyzeBtn');
  const status = document.getElementById('status');
  const result = document.getElementById('result');

  btn.disabled = true;
  btn.textContent = '⏳ Analyzing...';
  status.textContent = 'Scanning reviews...';
  result.style.display = 'none';

  // Get the active tab
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  // Inject a script that scrapes AND calls API AND returns result
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: (apiUrl) => {
      return new Promise((resolve) => {
        const reviews = [];
        document.querySelectorAll('[data-hook="review-body"] span').forEach(el => {
          const text = el.innerText?.trim();
          if (text && text.length > 20) reviews.push(text);
        });
        if (reviews.length === 0) { resolve({ error: 'No reviews found' }); return; }
        fetch(apiUrl + '/analyze-bulk', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ reviews: reviews.slice(0, 20) })
        }).then(r => r.json()).then(resolve).catch(e => resolve({ error: e.message }));
      });
    },
    args: [API_URL]
  }).then(results => {
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
  }).catch(err => {
    btn.disabled = false;
    btn.textContent = '🔍 Analyze Reviews';
    status.textContent = '❌ ' + err.message;
  });
}
document.getElementById('analyzeBtn').addEventListener('click', analyze);