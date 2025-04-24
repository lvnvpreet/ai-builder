from typing import Dict, List, Any

def generate_match_reason(template_data: Dict[str, Any], 
                         industry: str,
                         score: float,
                         target_audience: List[str] = None) -> str:
    """
    Generate a human-readable explanation for why a template was recommended.
    
    Args:
        template_data: Template metadata
        industry: Business industry
        score: Similarity score
        target_audience: Target audience (optional)
        
    Returns:
        Human-readable explanation string
    """
    reasons = []
    
    # Industry match
    template_industries = template_data.get('industries', [])
    if industry and any(i.lower() == industry.lower() for i in template_industries):
        reasons.append(f"Perfect match for {industry} businesses")
    elif template_industries:
        reasons.append(f"Designed for similar industries like {', '.join(template_industries[:2])}")
    
    # Style & aesthetic match
    if 'style' in template_data:
        reasons.append(f"Features a {template_data['style']} design style")
    
    # Target audience match
    if target_audience and 'target_audience' in template_data:
        matching_audiences = [a for a in target_audience if a.lower() in 
                             [ta.lower() for ta in template_data['target_audience']]]
        if matching_audiences:
            reasons.append(f"Optimized for {matching_audiences[0]} audience")
    
    # Features highlight
    key_features = template_data.get('features', [])[:2]
    if key_features:
        reasons.append(f"Includes {' and '.join(key_features)}")
    
    # Confidence level
    if score > 0.9:
        confidence = "Exceptional"
    elif score > 0.8:
        confidence = "Strong"
    elif score > 0.7:
        confidence = "Good"
    else:
        confidence = "Moderate"
    
    # Combine reasons with confidence level
    if reasons:
        explanation = f"{confidence} match: {'. '.join(reasons)}."
    else:
        explanation = f"{confidence} match for your business requirements."
    
    return explanation