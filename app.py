# ============================================
# FAKE REVIEW DETECTOR - Week 2: Flask API
# ============================================
# Run: python3 app.py
# Test: open http://localhost:5000
# ============================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import re
import os

app = Flask(__name__)
CORS(app)  # Allows Chrome extension to call this API

# ============================================
# Load the saved model from Week 1
# ============================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    model = joblib.load(os.path.join(BASE_DIR, 'fake_review_model.pkl'))
    vectorizer = joblib.load(os.path.join(BASE_DIR, 'tfidf_vectorizer.pkl'))
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    print("Make sure fake_review_model.pkl and tfidf_vectorizer.pkl are in the same folder")


# ============================================
# Helper: Preprocess text
# ============================================

def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ============================================
# Helper: Analyze a list of reviews
# ============================================

def analyze_reviews(reviews):
    results = []
    fake_count = 0

    for review in reviews:
        clean = preprocess(review)
        features = vectorizer.transform([clean])
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0]
        confidence = round(max(probability) * 100, 1)

        is_fake = bool(prediction == 1)
        if is_fake:
            fake_count += 1

        results.append({
            'review': review[:100] + '...' if len(review) > 100 else review,
            'is_fake': is_fake,
            'confidence': confidence,
            'label': '🚩 FAKE' if is_fake else '✅ REAL'
        })

    total = len(reviews)
    fake_percentage = round((fake_count / total) * 100) if total > 0 else 0

    # Trust score: 100 = all real, 0 = all fake
    trust_score = 100 - fake_percentage

    if trust_score >= 80:
        trust_label = "✅ Trustworthy"
        trust_color = "green"
    elif trust_score >= 50:
        trust_label = "⚠️ Suspicious"
        trust_color = "orange"
    else:
        trust_label = "🚩 Highly Suspicious"
        trust_color = "red"

    return {
        'total_reviews': total,
        'fake_count': fake_count,
        'real_count': total - fake_count,
        'fake_percentage': fake_percentage,
        'trust_score': trust_score,
        'trust_label': trust_label,
        'trust_color': trust_color,
        'reviews': results
    }


# ============================================
# ROUTES
# ============================================

# Home route - check if API is running
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': '🟢 API is running',
        'name': 'AI Fake Review Detector',
        'version': '1.0',
        'endpoints': {
            'POST /analyze': 'Analyze a single review',
            'POST /analyze-bulk': 'Analyze multiple reviews',
            'GET /health': 'Check API health'
        }
    })


# Health check
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'model_loaded': True})


# Analyze a single review
@app.route('/analyze', methods=['POST'])
def analyze_single():
    data = request.get_json()

    if not data or 'review' not in data:
        return jsonify({'error': 'Please provide a review field'}), 400

    review = data['review'].strip()
    if not review:
        return jsonify({'error': 'Review cannot be empty'}), 400

    result = analyze_reviews([review])

    return jsonify({
        'review': review,
        'is_fake': result['reviews'][0]['is_fake'],
        'confidence': result['reviews'][0]['confidence'],
        'label': result['reviews'][0]['label']
    })


# Analyze multiple reviews (for Chrome extension)
@app.route('/analyze-bulk', methods=['POST'])
def analyze_bulk():
    data = request.get_json()

    if not data or 'reviews' not in data:
        return jsonify({'error': 'Please provide a reviews array'}), 400

    reviews = data['reviews']
    if not isinstance(reviews, list) or len(reviews) == 0:
        return jsonify({'error': 'Reviews must be a non-empty array'}), 400

    if len(reviews) > 50:
        return jsonify({'error': 'Maximum 50 reviews per request'}), 400

    result = analyze_reviews(reviews)
    return jsonify(result)


# ============================================
# Run the app
# ============================================

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Fake Review Detector API Starting...")
    print("="*50)
    print("📡 Running at: http://localhost:5000")
    print("📖 Endpoints:")
    print("   GET  /          → API info")
    print("   GET  /health    → Health check")
    print("   POST /analyze   → Single review")
    print("   POST /analyze-bulk → Multiple reviews")
    print("="*50 + "\n")
app.run(host='0.0.0.0', port=10000, debug=False)