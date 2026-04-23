# 🔍 AI Fake Review Detector

A browser extension + ML backend that detects fake reviews on Amazon, Flipkart, and Meesho in real-time.

## 🗓️ Build Plan
| Week | Task |
|------|------|
| ✅ 1 | Train fake review classifier (you are here) |
| 2 | Build Flask API |
| 3 | Build Chrome extension |
| 4 | Connect extension to API |
| 5 | Add trust score UI |
| 6 | Deploy + publish |

## 🚀 Week 1 - Run the Model

```bash
pip install -r requirements.txt
python week1_train.py
```

## 📁 Folder Structure
```
fake-review-detector/
├── ml/
│   ├── week1_train.py        ← You are here
│   ├── fake_review_model.pkl ← Generated after training
│   └── tfidf_vectorizer.pkl  ← Generated after training
├── api/
│   └── app.py                ← Week 2
├── extension/
│   ├── manifest.json         ← Week 3
│   └── content.js            ← Week 3
└── requirements.txt
```

## 🛠️ Tech Stack
- Python + scikit-learn (ML model)
- Flask (API)
- JavaScript (Chrome Extension)
- TF-IDF + Logistic Regression → upgrade to BERT later
