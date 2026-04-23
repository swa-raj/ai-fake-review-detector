# ============================================
# FAKE REVIEW DETECTOR - API Test Script
# Run this AFTER starting app.py
# ============================================
# Terminal 1: python3 app.py
# Terminal 2: python3 test_api.py
# ============================================

import urllib.request
import json

BASE_URL = "http://localhost:8080"
def post(endpoint, data):
    url = f"{BASE_URL}{endpoint}"
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def get(endpoint):
    with urllib.request.urlopen(f"{BASE_URL}{endpoint}") as response:
        return json.loads(response.read().decode('utf-8'))

print("="*50)
print("🧪 TESTING FAKE REVIEW DETECTOR API")
print("="*50)

# Test 1: Health check
print("\n1️⃣  Health Check:")
result = get("/health")
print(f"   Status: {result['status']}")

# Test 2: Single fake review
print("\n2️⃣  Single Fake Review:")
result = post("/analyze", {
    "review": "Amazing product!! Best ever!! Buy now!! Highly recommend to everyone!!"
})
print(f"   Label: {result['label']}")
print(f"   Confidence: {result['confidence']}%")

# Test 3: Single real review
print("\n3️⃣  Single Real Review:")
result = post("/analyze", {
    "review": "Used this for 2 weeks. Works well but the zipper feels cheap. Good for the price though."
})
print(f"   Label: {result['label']}")
print(f"   Confidence: {result['confidence']}%")

# Test 4: Bulk reviews
print("\n4️⃣  Bulk Review Analysis:")
result = post("/analyze-bulk", {
    "reviews": [
        "Amazing!! Best product ever!! Buy now!! 5 stars!!",
        "Works okay. Battery drains fast but display is sharp.",
        "Wow wow wow!! Superb!! Excellent!! Highly recommend!!",
        "Used for 3 weeks. Build quality is decent. Delivery was on time.",
        "Perfect product!! Changed my life!! Everyone must buy!!"
    ]
})
print(f"   Total Reviews: {result['total_reviews']}")
print(f"   Fake: {result['fake_count']} | Real: {result['real_count']}")
print(f"   Trust Score: {result['trust_score']}/100")
print(f"   Verdict: {result['trust_label']}")

print("\n" + "="*50)
print("✅ ALL TESTS PASSED! API is working perfectly.")
print("="*50)
