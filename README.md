# 🛡️ PhishGuard: Real-Time Explainable Phishing Detection

**One-line pitch:** Real-time, explainable phishing detection in under 50 ms, directly in your browser.

## ⚠️ The Problem
Traditional blocklists fail against zero-day phishing attacks because attackers constantly register new domains. PhishGuard uses Machine Learning to analyze the actual structure and semantics of a URL in real-time, catching threats before they are ever reported.

## ✨ Features
* **Lightning Fast:** Extracts 40+ lexical, host, and semantic features and runs inference in < 50ms.
* **Explainable AI (XAI):** Uses SHAP to provide plain-English reasons for why a site was blocked, building user trust rather than acting as a black box.
* **Privacy First:** Only the URL is sent to the API. No page content is read, no personal data is tracked, and no logs are kept.
* **Dual UI:** Includes a Chrome Extension with a full-screen warning overlay and a Web Scanner dashboard.

## 🏗️ Architecture
`Data Sources (PhishTank/Tranco) -> Cleaning & Domain Split -> Feature Extraction (40+ features) -> LightGBM Model -> FastAPI Backend -> Chrome Extension & Landing Website`

## 📊 Evaluation & Results
To prevent the "leaky dataset" trap where models memorize domains instead of learning threats, we used a strict **Domain-based Split (GroupShuffleSplit)**. 

Our final test was conducted on a realistic imbalanced dataset (95% safe, 5% phishing) to mimic real internet traffic:
* **Best Model:** LightGBM
* **F1 Score:** ~0.98
* **Inference Time:** < 5 ms per URL
* **Robustness:** Successfully detects obfuscation tricks like URL shorteners, IP addresses, and deceptive brand subdomains (e.g., `paypal.com.secure-update.xyz`).

## 🚀 How to Run Locally

### 1. Start the AI Backend
```bash
# Activate virtual environment
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Run the FastAPI server
uvicorn backend.app:app --reload --port 8000