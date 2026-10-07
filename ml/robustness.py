import pandas as pd
import joblib
import warnings
from features import extract_features

warnings.filterwarnings('ignore')

def main():
    print("Starting Robustness Testing against Obfuscations...\n")
    model = joblib.load('backend/model.joblib')
    
    # Hacker tricks: URL shorteners, IPs, fake paths, and punycode
    obfuscated_urls = [
        "https://bit.ly/3xY89L",                                  # URL Shortener
        "http://192.168.1.100/secure-update",                     # IP Address
        "http://paypal.com.login-security-update.xyz/verify",     # Brand in subdomain
        "http://google.com@10.0.0.1/login"                        # @ Trick
    ]
    
    print(f"{'Hacker URL Trick':<55} | {'Model Verdict'}")
    print("-" * 75)
    
    for url in obfuscated_urls:
        features = extract_features(url)
        X = pd.DataFrame([features])
        pred = model.predict(X)[0]
        verdict = "Phishing 🚨" if pred == 1 else "Safe ✅"
        print(f"{url:<55} | {verdict}")
        
    print("\nRobustness Test Complete! Put these results in your presentation.")

if __name__ == "__main__":
    main()