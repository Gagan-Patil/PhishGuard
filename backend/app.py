from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import time
from functools import lru_cache
from typing import List

from backend.features import extract_features
from backend.explain import get_human_readable_reasons

app = FastAPI(title="PhishGuard API")

# Enable CORS for the Chrome Extension and Website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the trained model
model = joblib.load('backend/model.joblib')

# Whitelist to cut false positives on well-known sites
WHITELIST = ["google.com", "github.com", "wikipedia.org", "microsoft.com"]

class URLRequest(BaseModel):
    url: str

class BatchURLRequest(BaseModel):
    urls: List[str]

@lru_cache(maxsize=1000)
def predict_single(url: str):
    start_time = time.perf_counter()
    
    # 1. Check Whitelist
    if any(w in url.lower() for w in WHITELIST):
        return {
            "url": url, "score": 0, "verdict": "safe", "confidence": 1.0,
            "reasons": ["Domain is on the trusted whitelist."],
            "latency_ms": int((time.perf_counter() - start_time) * 1000)
        }

    # 2. Extract Features
    features = extract_features(url)
    df = pd.DataFrame([features])
    
    # 3. Predict & Calculate Score
    proba = model.predict_proba(df)[0][1] if hasattr(model, "predict_proba") else model.predict(df)[0]
    score = int(proba * 100)
    
    # 4. Apply Verdict Bands
    if score < 40:
        verdict = "safe"
    elif score < 70:
        verdict = "suspicious"
    else:
        verdict = "phishing"
        
    # 5. Explainability
    reasons = get_human_readable_reasons(features) if verdict != "safe" else ["Site appears normal and safe."]
    latency = int((time.perf_counter() - start_time) * 1000)
    
    return {
        "url": url,
        "score": score,
        "verdict": verdict,
        "confidence": round(float(proba), 2),
        "reasons": reasons,
        "latency_ms": latency
    }

@app.post("/predict")
def predict_endpoint(req: URLRequest):
    return predict_single(req.url)

@app.post("/batch")
def predict_batch(req: BatchURLRequest):
    return [predict_single(u) for u in req.urls]

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0"}