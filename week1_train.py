# ============================================
# FAKE REVIEW DETECTOR - Week 1 Starter Code
# AI Fake Review Classifier using NLP
# ============================================

# STEP 1: Install dependencies
# Run this in terminal first:
# pip install scikit-learn pandas numpy matplotlib seaborn joblib

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import re


# ============================================
# STEP 2: Generate Synthetic Training Data
# (Replace with real dataset later)
# ============================================

def generate_fake_reviews(n=500):
    """Simulates fake reviews - generic, overly positive, no specifics"""
    fake_templates = [
        "This product is absolutely amazing! Best purchase ever! Highly recommend!",
        "Wow just wow. Changed my life. 5 stars. Buy it now you won't regret.",
        "Perfect product. Fast delivery. Great quality. Very happy. Thank you seller.",
        "Excellent!! superb!! outstanding!! must buy!! great product!!",
        "I love this so much. Amazing quality. Will buy again. Very satisfied customer.",
        "Best product on this site. Everyone should buy this. No complaints at all.",
        "Fantastic item. Arrived quickly. Works perfectly. Seller is very responsive.",
        "Great value for money. Highly satisfied. Will recommend to all my friends.",
        "Top quality product. Very impressed. Exactly as described. 5 star rating.",
        "Wonderful experience. Product exceeded expectations. Very very happy!!",
    ]
    reviews = []
    for _ in range(n):
        base = np.random.choice(fake_templates)
        # Add slight variations
        variations = ["", " Great!", " Love it!", " Amazing!!", " So good."]
        review = base + np.random.choice(variations)
        reviews.append(review)
    return reviews


def generate_real_reviews(n=500):
    """Simulates genuine reviews - specific, balanced, personal details"""
    real_templates = [
        "Bought this for my kitchen. The build quality is decent but the handle feels a bit loose after 2 weeks of use.",
        "Works as described. Setup took about 20 minutes. Battery life is around 6 hours which is okay for the price.",
        "Good product overall. The color is slightly different from the photo - more of a dark grey than black. Still happy.",
        "I've been using this for 3 months now. Still works fine. The only issue is the charging cable is too short.",
        "Decent quality for the price. My daughter loves it. Packaging was secure, no damage during delivery.",
        "It does what it says. Nothing extraordinary but reliable. Would consider buying again if this breaks.",
        "Mixed feelings. The product works but customer support took 4 days to respond to my query.",
        "Solid purchase. I compared this with another brand and this one has better grip. Comfortable to use daily.",
        "Used it twice so far. Seems sturdy. Let's see how it holds up over time. Will update the review later.",
        "Average product. Expected better finishing at this price point. The main function works perfectly though.",
    ]
    reviews = []
    for _ in range(n):
        base = np.random.choice(real_templates)
        reviews.append(base)
    return reviews


# ============================================
# STEP 3: Prepare Dataset
# ============================================

print("📦 Generating training data...")

fake = generate_fake_reviews(500)
real = generate_real_reviews(500)

df = pd.DataFrame({
    'review': fake + real,
    'label': [1] * 500 + [0] * 500  # 1 = fake, 0 = real
})

# Shuffle the dataset
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"✅ Dataset ready: {len(df)} reviews ({df['label'].sum()} fake, {(df['label']==0).sum()} real)")


# ============================================
# STEP 4: Text Preprocessing
# ============================================

def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)     # Remove punctuation/numbers
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    return text

df['clean_review'] = df['review'].apply(preprocess)


# ============================================
# STEP 5: Feature Extraction (TF-IDF)
# ============================================

print("\n🔍 Extracting features with TF-IDF...")

vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),   # Unigrams + bigrams
    stop_words='english'
)

X = vectorizer.fit_transform(df['clean_review'])
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"✅ Training samples: {X_train.shape[0]} | Test samples: {X_test.shape[0]}")


# ============================================
# STEP 6: Train the Model
# ============================================

print("\n🤖 Training Logistic Regression classifier...")

model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train, y_train)

print("✅ Model trained!")


# ============================================
# STEP 7: Evaluate the Model
# ============================================

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n📊 RESULTS:")
print(f"Accuracy: {accuracy * 100:.2f}%")
print("\nDetailed Report:")
print(classification_report(y_test, y_pred, target_names=['Real', 'Fake']))

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6, 4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Real', 'Fake'],
            yticklabels=['Real', 'Fake'])
plt.title('Confusion Matrix - Fake Review Detector')
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.tight_layout()
plt.savefig('confusion_matrix.png', dpi=150)
print("\n✅ Confusion matrix saved as confusion_matrix.png")


# ============================================
# STEP 8: Save the Model
# ============================================

joblib.dump(model, 'fake_review_model.pkl')
joblib.dump(vectorizer, 'tfidf_vectorizer.pkl')
print("✅ Model saved as fake_review_model.pkl")
print("✅ Vectorizer saved as tfidf_vectorizer.pkl")


# ============================================
# STEP 9: Test With Your Own Review
# ============================================

def predict_review(review_text):
    """Predict if a review is fake or real"""
    clean = preprocess(review_text)
    features = vectorizer.transform([clean])
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0]
    
    label = "🚩 FAKE" if prediction == 1 else "✅ REAL"
    confidence = max(probability) * 100
    
    print(f"\nReview: \"{review_text[:80]}...\"" if len(review_text) > 80 else f"\nReview: \"{review_text}\"")
    print(f"Result: {label} (Confidence: {confidence:.1f}%)")
    return prediction, confidence


# Test examples
print("\n" + "="*50)
print("🧪 TESTING WITH SAMPLE REVIEWS:")
print("="*50)

predict_review("Amazing product!! Best ever!! Buy now!! Highly recommend to everyone!!")
predict_review("Used this for 2 weeks. Works well but the zipper feels cheap. Good for the price though.")
predict_review("Wow wow wow. Superb quality. Fast delivery. Very happy. 5 stars. Excellent!!")
predict_review("Battery lasts about 4 hours. Display is sharp. A bit heavy but manageable for daily use.")
