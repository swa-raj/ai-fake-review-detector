// ============================================
// FAKE REVIEW DETECTOR - Content Script
// Runs on Amazon, Flipkart, Meesho pages
// Scrapes reviews and sends to Flask API
// ============================================

const API_URL = "http://localhost:8080";

// ============================================
// STEP 1: Scrape reviews from the page
// ============================================

function scrapeReviews() {
  let reviews = [];

  // Amazon selectors
  const amazonSelectors = [
    '[data-hook="review-body"] span',
    '.review-text-content span',
    '.cr-original-review-content'
  ];

  // Flipkart selectors
  const flipkartSelectors = [
    '.t-common._2-N8zT',
    '._6K-7Co',
    '.row._3a0MFd'
  ];

  // Meesho selectors
  const meeshoSelectors = [
    '.sc-eDvSVe',
    'p.m-0'
  ];

  const allSelectors = [
    ...amazonSelectors,
    ...flipkartSelectors,
    ...meeshoSelectors
  ];

  for (const selector of allSelectors) {
    const elements = document.querySelectorAll(selector);
    elements.forEach(el => {
      const text = el.innerText?.trim();
      if (text && text.length > 20 && text.length < 1000) {
        reviews.push(text);
      }
    });
    if (reviews.length > 0) break;
  }

  // Remove duplicates
  reviews = [...new Set(reviews)];

  // Max 20 reviews
  return reviews.slice(0, 20);
}


// ============================================
// STEP 2: Send reviews to Flask API
// ============================================

async function analyzeReviews(reviews) {
  try {
    const response = await fetch(`${API_URL}/analyze-bulk`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reviews })
    });

    if (!response.ok) throw new Error('API error');
    return await response.json();
  } catch (error) {
    console.error('Fake Review Detector API error:', error);
    return null;
  }
}


// ============================================
// STEP 3: Inject result banner into the page
// ============================================

function injectBanner(result) {
  // Remove existing banner if any
  const existing = document.getElementById('frd-banner');
  if (existing) existing.remove();

  const colors = {
    green: { bg: '#e6f9f0', border: '#27ae60', text: '#1a7a45' },
    orange: { bg: '#fff8e6', border: '#f39c12', text: '#9a6109' },
    red: { bg: '#fde8e8', border: '#e74c3c', text: '#a93226' }
  };

  const color = colors[result.trust_color] || colors.orange;

  const banner = document.createElement('div');
  banner.id = 'frd-banner';
  banner.innerHTML = `
    <div style="
      position: fixed;
      top: 70px;
      right: 20px;
      z-index: 99999;
      background: ${color.bg};
      border: 2px solid ${color.border};
      border-radius: 12px;
      padding: 16px 20px;
      max-width: 280px;
      font-family: Arial, sans-serif;
      box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    ">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <strong style="color:${color.text}; font-size:15px;">🔍 Review Analyzer</strong>
        <button onclick="document.getElementById('frd-banner').remove()" 
          style="background:none; border:none; cursor:pointer; font-size:18px; color:#999;">✕</button>
      </div>

      <div style="margin-top:12px; text-align:center;">
        <div style="font-size:36px; font-weight:bold; color:${color.text};">
          ${result.trust_score}/100
        </div>
        <div style="font-size:14px; color:${color.text}; margin-top:4px;">
          Trust Score
        </div>
        <div style="font-size:16px; margin-top:8px;">
          ${result.trust_label}
        </div>
      </div>

      <div style="
        margin-top:12px;
        background:white;
        border-radius:8px;
        padding:10px;
        font-size:13px;
        color:#444;
      ">
        <div>📊 Reviews analyzed: <strong>${result.total_reviews}</strong></div>
        <div>✅ Real: <strong>${result.real_count}</strong></div>
        <div>🚩 Fake: <strong>${result.fake_count}</strong></div>
      </div>

      <div style="margin-top:10px; font-size:11px; color:#999; text-align:center;">
        AI Fake Review Detector
      </div>
    </div>
  `;

  document.body.appendChild(banner);
}


// ============================================
// STEP 4: Show loading banner
// ============================================

function injectLoadingBanner() {
  const existing = document.getElementById('frd-banner');
  if (existing) existing.remove();

  const banner = document.createElement('div');
  banner.id = 'frd-banner';
  banner.innerHTML = `
    <div style="
      position: fixed;
      top: 70px;
      right: 20px;
      z-index: 99999;
      background: #f0f4ff;
      border: 2px solid #4a90e2;
      border-radius: 12px;
      padding: 16px 20px;
      max-width: 280px;
      font-family: Arial, sans-serif;
      box-shadow: 0 4px 20px rgba(0,0,0,0.15);
      text-align: center;
    ">
      <strong style="color:#2c5aa0;">🔍 Analyzing Reviews...</strong>
      <div style="margin-top:8px; color:#555; font-size:13px;">Please wait</div>
    </div>
  `;
  document.body.appendChild(banner);
}


// ============================================
// STEP 5: Main function — listen for popup
// ============================================

chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
  if (message.action === 'analyze') {
    injectLoadingBanner();

    const reviews = scrapeReviews();

    if (reviews.length === 0) {
      injectBanner({
        trust_score: '?',
        trust_label: '⚠️ No reviews found',
        trust_color: 'orange',
        total_reviews: 0,
        real_count: 0,
        fake_count: 0
      });
      sendResponse({ success: false, message: 'No reviews found' });
      return;
    }

    const result = await analyzeReviews(reviews);

    if (result) {
      injectBanner(result);
      sendResponse({ success: true, result });
    } else {
      injectBanner({
        trust_score: '!',
        trust_label: '❌ API not running',
        trust_color: 'red',
        total_reviews: 0,
        real_count: 0,
        fake_count: 0
      });
      sendResponse({ success: false, message: 'API error' });
    }
  }
  return true;
});
