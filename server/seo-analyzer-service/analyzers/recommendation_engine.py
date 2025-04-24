from typing import Dict, List, Optional, Any
import json

class SEORecommendationEngine:
    """Generate SEO recommendations based on analysis results."""
    
    def __init__(self):
        self.priority_weights = {
            'critical': 1.0,
            'high': 0.7,
            'medium': 0.4,
            'low': 0.2
        }
    
    def generate_recommendations(self, 
                               readability_score: float,
                               keyword_density: Dict[str, float],
                               competitor_analysis: Optional[Dict] = None,
                               keyword_opportunities: Optional[Dict] = None,
                               content_gaps: Optional[Dict] = None) -> List[Dict]:
        """Generate comprehensive SEO recommendations."""
        recommendations = []
        
        # Readability recommendations
        readability_recs = self.generate_readability_recommendations(readability_score)
        recommendations.extend(readability_recs)
        
        # Keyword density recommendations
        keyword_recs = self.generate_keyword_recommendations(keyword_density)
        recommendations.extend(keyword_recs)
        
        # Competitor-based recommendations
        if competitor_analysis:
            competitor_recs = self.generate_competitor_recommendations(competitor_analysis)
            recommendations.extend(competitor_recs)
        
        # Keyword opportunity recommendations
        if keyword_opportunities:
            opportunity_recs = self.generate_opportunity_recommendations(keyword_opportunities)
            recommendations.extend(opportunity_recs)
        
        # Content gap recommendations
        if content_gaps:
            gap_recs = self.generate_gap_recommendations(content_gaps)
            recommendations.extend(gap_recs)
        
        # Sort by priority
        recommendations.sort(key=lambda x: self.priority_weights.get(x['priority'], 0), reverse=True)
        
        return recommendations
    
    def generate_readability_recommendations(self, score: float) -> List[Dict]:
        """Generate recommendations based on readability score."""
        recommendations = []
        
        if score < 30:
            recommendations.append({
                'type': 'readability',
                'priority': 'critical',
                'issue': 'Very difficult to read',
                'recommendation': 'Simplify sentence structure and use shorter words. Target 8th-grade reading level.',
                'impact': 'High - Poor readability significantly impacts user engagement and SEO'
            })
        elif score < 50:
            recommendations.append({
                'type': 'readability',
                'priority': 'high',
                'issue': 'Difficult to read',
                'recommendation': 'Break up long sentences and paragraphs. Use more common vocabulary.',
                'impact': 'Medium - Improved readability will increase time on page'
            })
        elif score < 60:
            recommendations.append({
                'type': 'readability',
                'priority': 'medium',
                'issue': 'Moderately difficult to read',
                'recommendation': 'Consider simplifying complex sections for broader audience appeal.',
                'impact': 'Low to Medium - Minor improvements can enhance user experience'
            })
        
        return recommendations
    
    def generate_keyword_recommendations(self, keyword_density: Dict[str, float]) -> List[Dict]:
        """Generate recommendations based on keyword density."""
        recommendations = []
        
        for keyword, density in keyword_density.items():
            if density < 0.001:
                recommendations.append({
                    'type': 'keyword_density',
                    'priority': 'high',
                    'issue': f'Keyword "{keyword}" is underused',
                    'recommendation': f'Increase usage of "{keyword}" to 1-2% density',
                    'impact': 'High - Proper keyword density is crucial for ranking'
                })
            elif density > 0.03:
                recommendations.append({
                    'type': 'keyword_density',
                    'priority': 'high',
                    'issue': f'Keyword "{keyword}" may be overused',
                    'recommendation': f'Reduce usage of "{keyword}" to avoid keyword stuffing',
                    'impact': 'High - Keyword stuffing can lead to penalties'
                })
        
        return recommendations
    
    def generate_competitor_recommendations(self, competitor_analysis: Dict) -> List[Dict]:
        """Generate recommendations based on competitor analysis."""
        recommendations = []
        
        insights = competitor_analysis.get('insights', {})
        
        # Process weaknesses
        for weakness in insights.get('weaknesses', []):
            recommendations.append({
                'type': 'competitor_insight',
                'priority': 'high',
                'issue': weakness,
                'recommendation': self.get_recommendation_for_weakness(weakness),
                'impact': 'High - Addressing competitive weaknesses improves ranking potential'
            })
        
        # Process opportunities
        for opportunity in insights.get('opportunities', []):
            recommendations.append({
                'type': 'competitor_insight',
                'priority': 'medium',
                'issue': 'Opportunity identified',
                'recommendation': opportunity,
                'impact': 'Medium - Capitalizing on opportunities can provide competitive advantage'
            })
        
        return recommendations
    
    def generate_opportunity_recommendations(self, keyword_opportunities: Dict) -> List[Dict]:
        """Generate recommendations based on keyword opportunities."""
        recommendations = []
        
        # Long-tail opportunities
        if keyword_opportunities.get('long_tail_opportunities'):
            long_tail = keyword_opportunities['long_tail_opportunities'][:5]
            recommendations.append({
                'type': 'keyword_opportunity',
                'priority': 'medium',
                'issue': 'Long-tail keyword opportunities found',
                'recommendation': f'Consider targeting these long-tail keywords: {", ".join(long_tail)}',
                'impact': 'Medium - Long-tail keywords often have lower competition and higher conversion rates'
            })
        
        # Semantic variations
        if keyword_opportunities.get('semantic_variations'):
            for main_keyword, variations in keyword_opportunities['semantic_variations'].items():
                if variations:
                    recommendations.append({
                        'type': 'keyword_opportunity',
                        'priority': 'medium',
                        'issue': f'Semantic variations for "{main_keyword}" found',
                        'recommendation': f'Include variations like: {", ".join(variations[:3])}',
                        'impact': 'Medium - Semantic variations improve topical relevance'
                    })
        
        # Question keywords
        if keyword_opportunities.get('question_keywords'):
            questions = keyword_opportunities['question_keywords'][:3]
            if questions:
                recommendations.append({
                    'type': 'keyword_opportunity',
                    'priority': 'high',
                    'issue': 'Question-based search opportunities',
                    'recommendation': f'Create content answering: {"; ".join(questions)}',
                    'impact': 'High - Featured snippets and voice search optimization'
                })
        
        return recommendations
    
    def generate_gap_recommendations(self, content_gaps: Dict) -> List[Dict]:
        """Generate recommendations based on content gaps."""
        recommendations = []
        
        # Topic gaps
        if content_gaps.get('topic_gaps'):
            high_priority_topics = [gap['topic'] for gap in content_gaps['topic_gaps'] if gap.get('importance') == 'high']
            if high_priority_topics:
                recommendations.append({
                    'type': 'content_gap',
                    'priority': 'critical',
                    'issue': 'Missing important topics',
                    'recommendation': f'Add content covering: {", ".join(high_priority_topics[:5])}',
                    'impact': 'Critical - These topics are essential for comprehensive coverage'
                })
        
        # Depth gaps
        if content_gaps.get('depth_gaps'):
            for metric, gap_data in content_gaps['depth_gaps'].items():
                if gap_data['gap_percentage'] > 30:
                    recommendations.append({
                        'type': 'content_gap',
                        'priority': 'high',
                        'issue': f'Content depth insufficient for {metric}',
                        'recommendation': f'Increase {metric} by {gap_data["gap_percentage"]:.0f}% to match competitors',
                        'impact': 'High - Content depth affects authority and rankings'
                    })
        
        # Keyword coverage gaps
        if content_gaps.get('keyword_gaps'):
            missing_keywords = content_gaps['keyword_gaps'].get('missing_keywords', [])
            if missing_keywords:
                keywords = [gap['keyword'] for gap in missing_keywords[:5]]
                recommendations.append({
                    'type': 'content_gap',
                    'priority': 'critical',
                    'issue': 'Missing target keywords',
                    'recommendation': f'Include these keywords: {", ".join(keywords)}',
                    'impact': 'Critical - Missing target keywords severely impacts ranking potential'
                })
        
        # Semantic gaps
        if content_gaps.get('semantic_gaps'):
            top_semantic_gaps = [gap['topic'] for gap in content_gaps['semantic_gaps'][:5]]
            if top_semantic_gaps:
                recommendations.append({
                    'type': 'content_gap',
                    'priority': 'medium',
                    'issue': 'Semantic coverage gaps',
                    'recommendation': f'Expand content to cover: {", ".join(top_semantic_gaps)}',
                    'impact': 'Medium - Better semantic coverage improves topical authority'
                })
        
        return recommendations
    
    def get_recommendation_for_weakness(self, weakness: str) -> str:
        """Convert a weakness into an actionable recommendation."""
        weakness_lower = weakness.lower()
        
        if 'shorter' in weakness_lower or 'word count' in weakness_lower:
            return 'Expand content with more detailed information, examples, and explanations'
        elif 'readable' in weakness_lower:
            return 'Simplify language, break up long paragraphs, and use bullet points where appropriate'
        elif 'title' in weakness_lower:
            return 'Optimize title length (50-60 characters) and include primary keyword'
        elif 'meta description' in weakness_lower:
            return 'Create compelling meta description (150-160 characters) with call-to-action'
        elif 'heading' in weakness_lower or 'h1' in weakness_lower or 'h2' in weakness_lower:
            return 'Add more descriptive headings to improve content structure and scannability'
        else:
            return f'Address identified weakness: {weakness}'