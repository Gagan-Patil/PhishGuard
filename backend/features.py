import re
import math
from urllib.parse import urlparse
import tldextract

def get_entropy(text):
    """Calculates Shannon entropy to detect random/obfuscated strings."""
    if not text:
        return 0
    prob = [float(text.count(c)) / len(text) for c in set(text)]
    return -sum(p * math.log2(p) for p in prob)

def extract_features(url: str) -> dict:
    """
    Extracts 40+ numeric features from a single URL.
    Groups: Lexical, Host-based, Keyword/Semantic, Trust Signals.
    """
    features = {}
    
    # Ensure URL has a scheme for proper parsing
    if not url.startswith('http'):
        url = 'http://' + url
        
    parsed = urlparse(url)
    ext = tldextract.extract(url)
    url_lower = url.lower()

    # --- 1. Lexical Features ---
    features['url_length'] = len(url)
    features['hostname_length'] = len(parsed.netloc)
    features['path_length'] = len(parsed.path)
    features['query_length'] = len(parsed.query)
    
    # Character counts
    features['count_at'] = url.count('@')
    features['count_question'] = url.count('?')
    features['count_hyphen'] = url.count('-')
    features['count_equal'] = url.count('=')
    features['count_slash'] = url.count('/')
    features['count_percent'] = url.count('%')
    
    digit_count = sum(c.isdigit() for c in url)
    letter_count = sum(c.isalpha() for c in url)
    features['digit_count'] = digit_count
    features['letter_count'] = letter_count
    features['digit_ratio'] = digit_count / len(url) if len(url) > 0 else 0
    features['letter_ratio'] = letter_count / len(url) if len(url) > 0 else 0
    features['uppercase_ratio'] = sum(1 for c in url if c.isupper()) / len(url) if len(url) > 0 else 0
    
    features['entropy_url'] = get_entropy(url)
    features['entropy_domain'] = get_entropy(parsed.netloc)
    
    tokens = re.split(r'\W+', url)
    features['longest_token_length'] = max((len(t) for t in tokens if t), default=0)
    features['path_segments'] = len([s for s in parsed.path.split('/') if s])

    # --- 2. Host-Based Features ---
    # IP address instead of domain
    features['has_ip'] = 1 if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', parsed.netloc) else 0
    features['subdomain_count'] = len([s for s in ext.subdomain.split('.') if s])
    
    suspicious_tlds = ['tk', 'ml', 'ga', 'cf', 'xyz', 'top', 'zip']
    features['tld_is_suspicious'] = 1 if ext.suffix in suspicious_tlds else 0
    features['domain_length'] = len(ext.domain)
    features['has_punycode'] = 1 if 'xn--' in url_lower else 0
    
    shorteners = ['bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'is.gd', 'ow.ly']
    features['is_shortener'] = 1 if ext.registered_domain in shorteners else 0
    features['non_standard_port'] = 1 if parsed.port and parsed.port not in [80, 443] else 0

    # --- 3. Keyword / Semantic Features ---
    keywords = ['login', 'verify', 'secure', 'account', 'update', 'bank', 
                'paypal', 'signin', 'confirm', 'password', 'wallet', 'free']
    for kw in keywords:
        features[f'kw_{kw}'] = url_lower.count(kw)
        
    # Detect brand names used deceptively in subdomains or paths
    brands = ['paypal', 'apple', 'google', 'microsoft', 'facebook', 'amazon', 'netflix']
    brand_in_sub_or_path = 0
    for brand in brands:
        if (brand in ext.subdomain.lower() or brand in parsed.path.lower()) and brand != ext.domain.lower():
            brand_in_sub_or_path = 1
            break
    features['brand_outside_domain'] = brand_in_sub_or_path
    
    features['https_in_hostname'] = 1 if 'https' in parsed.netloc.lower() else 0
    features['double_slash_in_path'] = 1 if '//' in parsed.path else 0

    # --- 4. Trust Signals ---
    features['uses_https'] = 1 if parsed.scheme == 'https' else 0

    return features

if __name__ == "__main__":
    import time
    test_url = "http://paypal.com.secure-login.xyz/verify?id=1"
    
    start_time = time.perf_counter()
    res = extract_features(test_url)
    latency_ms = (time.perf_counter() - start_time) * 1000
    
    print(f"Phase 4 complete!")
    print(f"Extracted {len(res)} features in {latency_ms:.2f} ms")
    print(f"Test URL: {test_url}")
    print("Sample features:")
    for k, v in list(res.items())[:10]:
        print(f"  {k}: {v}")