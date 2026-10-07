def get_human_readable_reasons(features: dict) -> list:
    """Maps flagged features to plain-English explanations."""
    reasons = []
    
    if features.get('has_ip', 0) == 1:
        reasons.append("Uses an IP address instead of a domain name")
    if features.get('tld_is_suspicious', 0) == 1:
        reasons.append("Uses a suspicious top-level domain (TLD)")
    if features.get('brand_outside_domain', 0) == 1:
        reasons.append("Brand name used deceptively outside the registered domain")
    if features.get('is_shortener', 0) == 1:
        reasons.append("Hides behind a URL shortener service")
    if features.get('digit_ratio', 0) > 0.15:
        reasons.append("Contains an unusually high number of digits")
    if features.get('url_length', 0) > 80:
        reasons.append("URL is exceptionally long to hide malicious parts")
        
    if not reasons:
        reasons.append("Multiple minor statistical anomalies detected by AI")
        
    return reasons[:3] # Max 3 reasons for a clean UI