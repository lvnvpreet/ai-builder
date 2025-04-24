import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Set, Optional
from collections import defaultdict
import spacy
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ContentGapAnalyzer:
    """Analyze content gaps between your content and competitors."""
    
    def __init__(self, nlp=None):
        self.nlp = nlp or spacy.load("en_core_web_sm")
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session
    
    async def fetch_competitor_content(self, url: str) -> str:
        """Fetch competitor content."""
        session = await self.get_session()
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract main content
                    content_tags = soup.find_all(['article', 'main', 'div'])
                    for tag in content_tags:
                        if tag.get('class') and any('content' in str(c).lower() for c in tag.get('class')):
                            return tag.get_text(separator=' ', strip=True)
                    
                    # Fallback to body text
                    return soup.get_text(separator=' ', strip=True)
                else:
                    return ""
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""
    
    async def find_gaps(self, your_content: str, competitor_urls: List[str], target_keywords: Optional[List[str]] = None) -> Dict:
        """Find content gaps between your content and competitors."""
        # Fetch competitor content
        competitor_contents = []
        for url in competitor_urls:
            content = await self.fetch_competitor_content(url)
            if content:
                competitor_contents.append(content)
        
        if not competitor_contents:
            return {
                'error': 'Could not fetch competitor content',
                'gaps': []
            }
        
        # Analyze content structure
        your_structure = self.analyze_content_structure(your_content)
        competitor_structures = [self.analyze_content_structure(c) for c in competitor_contents]
        
        # Find topic gaps
        topic_gaps = self.find_topic_gaps(your_content, competitor_contents)
        
        # Find depth gaps
        depth_gaps = self.find_depth_gaps(your_structure, competitor_structures)
        
        # Find keyword coverage gaps
        keyword_gaps = self.find_keyword_coverage_gaps(your_content, competitor_contents, target_keywords)
        
        # Find semantic gaps
        semantic_gaps = self.find_semantic_gaps(your_content, competitor_contents)
        
        return {
            'topic_gaps': topic_gaps,
            'depth_gaps': depth_gaps,
            'keyword_gaps': keyword_gaps,
            'semantic_gaps': semantic_gaps,
            'recommendations': self.generate_gap_recommendations(topic_gaps, depth_gaps, keyword_gaps, semantic_gaps)
        }
    
    def analyze_content_structure(self, content: str) -> Dict:
        """Analyze the structure of content."""
        doc = self.nlp(content)
        
        # Count sections, paragraphs, sentences
        paragraphs = content.split('\n\n')
        sentences = list(doc.sents)
        
        # Extract headers (simplified - in real case, would parse HTML)
        headers = []
        for sent in sentences:
            if sent.text.isupper() or (sent.text.istitle() and len(sent.text.split()) < 10):
                headers.append(sent.text)
        
        # Extract lists (simplified)
        lists = []
        for para in paragraphs:
            if para.strip().startswith(('•', '-', '*', '1.', '2.', '3.')):
                lists.append(para)
        
        return {
            'word_count': len(content.split()),
            'paragraph_count': len(paragraphs),
            'sentence_count': len(sentences),
            'header_count': len(headers),
            'list_count': len(lists),
            'avg_sentence_length': np.mean([len(sent.text.split()) for sent in sentences]),
            'headers': headers,
            'lists': lists
        }
    
    def find_topic_gaps(self, your_content: str, competitor_contents: List[str]) -> List[Dict]:
        """Find topics covered by competitors but not by you."""
        # Extract topics using TF-IDF
        all_contents = [your_content] + competitor_contents
        vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(all_contents)
        
        feature_names = vectorizer.get_feature_names_out()
        
        # Get your topics
        your_topics = set()
        your_tfidf = tfidf_matrix[0].toarray()[0]
        for idx, score in enumerate(your_tfidf):
            if score > 0.1:  # Threshold for considering a topic
                your_topics.add(feature_names[idx])
        
        # Get competitor topics
        competitor_topics = set()
        for i in range(1, len(all_contents)):
            comp_tfidf = tfidf_matrix[i].toarray()[0]
            for idx, score in enumerate(comp_tfidf):
                if score > 0.1:
                    competitor_topics.add(feature_names[idx])
        
        # Find gaps
        topic_gaps = []
        for topic in competitor_topics - your_topics:
            # Count how many competitors cover this topic
            coverage_count = 0
            for i in range(1, len(all_contents)):
                if tfidf_matrix[i, list(feature_names).index(topic)] > 0.1:
                    coverage_count += 1
            
            if coverage_count >= len(competitor_contents) / 2:  # At least half of competitors cover it
                topic_gaps.append({
                    'topic': topic,
                    'competitor_coverage': coverage_count,
                    'importance': 'high' if coverage_count == len(competitor_contents) else 'medium'
                })
        
        return topic_gaps
    
    def find_depth_gaps(self, your_structure: Dict, competitor_structures: List[Dict]) -> Dict:
        """Find gaps in content depth."""
        avg_competitor_metrics = {
            'word_count': np.mean([s['word_count'] for s in competitor_structures]),
            'paragraph_count': np.mean([s['paragraph_count'] for s in competitor_structures]),
            'header_count': np.mean([s['header_count'] for s in competitor_structures]),
            'list_count': np.mean([s['list_count'] for s in competitor_structures])
        }
        
        depth_gaps = {}
        
        # Compare metrics
        if your_structure['word_count'] < avg_competitor_metrics['word_count'] * 0.8:
            depth_gaps['word_count'] = {
                'your_value': your_structure['word_count'],
                'competitor_average': avg_competitor_metrics['word_count'],
                'gap_percentage': (avg_competitor_metrics['word_count'] - your_structure['word_count']) / avg_competitor_metrics['word_count'] * 100
            }
        
        if your_structure['header_count'] < avg_competitor_metrics['header_count'] * 0.8:
            depth_gaps['header_count'] = {
                'your_value': your_structure['header_count'],
                'competitor_average': avg_competitor_metrics['header_count'],
                'gap_percentage': (avg_competitor_metrics['header_count'] - your_structure['header_count']) / avg_competitor_metrics['header_count'] * 100
            }
        
        if your_structure['list_count'] < avg_competitor_metrics['list_count'] * 0.8:
            depth_gaps['list_count'] = {
                'your_value': your_structure['list_count'],
                'competitor_average': avg_competitor_metrics['list_count'],
                'gap_percentage': (avg_competitor_metrics['list_count'] - your_structure['list_count']) / avg_competitor_metrics['list_count'] * 100
            }
        
        return depth_gaps
    
    def find_keyword_coverage_gaps(self, your_content: str, competitor_contents: List[str], target_keywords: Optional[List[str]] = None) -> Dict:
        """Find gaps in keyword coverage."""
        gaps = {
            'missing_keywords': [],
            'underused_keywords': [],
            'competitor_keywords': []
        }
        
        if not target_keywords:
            return gaps
        
        your_content_lower = your_content.lower()
        
        # Check target keyword usage
        for keyword in target_keywords:
            keyword_lower = keyword.lower()
            your_count = your_content_lower.count(keyword_lower)
            
            competitor_counts = []
            for comp_content in competitor_contents:
                comp_count = comp_content.lower().count(keyword_lower)
                competitor_counts.append(comp_count)
            
            avg_competitor_count = np.mean(competitor_counts) if competitor_counts else 0
            
            if your_count == 0:
                gaps['missing_keywords'].append({
                    'keyword': keyword,
                    'competitor_average': avg_competitor_count
                })
            elif your_count < avg_competitor_count * 0.5:
                gaps['underused_keywords'].append({
                    'keyword': keyword,
                    'your_count': your_count,
                    'competitor_average': avg_competitor_count
                })
        
        # Find competitor keywords not in target list
        all_competitor_text = ' '.join(competitor_contents)
        competitor_doc = self.nlp(all_competitor_text)
        
        # Extract frequent noun phrases from competitors
        competitor_keywords = defaultdict(int)
        for chunk in competitor_doc.noun_chunks:
            if len(chunk.text.split()) >= 2:
                competitor_keywords[chunk.text.lower()] += 1
        
        # Find frequent competitor keywords not in your content
        for keyword, count in competitor_keywords.items():
            if count >= len(competitor_contents) and keyword not in your_content_lower:
                gaps['competitor_keywords'].append({
                    'keyword': keyword,
                    'frequency': count
                })
        
        return gaps
    
    def find_semantic_gaps(self, your_content: str, competitor_contents: List[str]) -> List[Dict]:
        """Find semantic gaps using topic modeling."""
        # Create document embeddings
        all_contents = [your_content] + competitor_contents
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(all_contents)
        
        # Calculate similarity between your content and each competitor
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
        
        # Identify topics where similarity is low
        semantic_gaps = []
        feature_names = vectorizer.get_feature_names_out()
        
        for i, similarity in enumerate(similarities):
            if similarity < 0.5:  # Low similarity threshold
                # Find topics unique to this competitor
                comp_tfidf = tfidf_matrix[i+1].toarray()[0]
                your_tfidf = tfidf_matrix[0].toarray()[0]
                
                for idx, (comp_score, your_score) in enumerate(zip(comp_tfidf, your_tfidf)):
                    if comp_score > 0.1 and your_score < 0.05:
                        semantic_gaps.append({
                            'topic': feature_names[idx],
                            'competitor_index': i,
                            'gap_score': comp_score - your_score
                        })
        
        # Sort and return top gaps
        semantic_gaps.sort(key=lambda x: x['gap_score'], reverse=True)
        return semantic_gaps[:20]
    
    def generate_gap_recommendations(self, topic_gaps: List[Dict], depth_gaps: Dict, 
                                   keyword_gaps: Dict, semantic_gaps: List[Dict]) -> List[Dict]:
        """Generate recommendations based on identified gaps."""
        recommendations = []
        
        # Topic gap recommendations
        if topic_gaps:
            high_importance_topics = [gap['topic'] for gap in topic_gaps if gap['importance'] == 'high']
            if high_importance_topics:
                recommendations.append({
                    'type': 'topic',
                    'priority': 'high',
                    'recommendation': f"Add sections covering these important topics: {', '.join(high_importance_topics[:5])}",
                    'impact': 'High - These topics are covered by all competitors'
                })
        
        # Depth gap recommendations
        if depth_gaps.get('word_count'):
            gap_percentage = depth_gaps['word_count']['gap_percentage']
            recommendations.append({
                'type': 'depth',
                'priority': 'high' if gap_percentage > 50 else 'medium',
                'recommendation': f"Expand content by {gap_percentage:.0f}% to match competitor depth",
                'impact': 'Medium to High - More comprehensive content ranks better'
            })
        
        # Keyword gap recommendations
        if keyword_gaps.get('missing_keywords'):
            missing = [gap['keyword'] for gap in keyword_gaps['missing_keywords']]
            recommendations.append({
                'type': 'keyword',
                'priority': 'high',
                'recommendation': f"Include these missing target keywords: {', '.join(missing)}",
                'impact': 'High - Critical for SEO targeting'
            })
        
        if keyword_gaps.get('underused_keywords'):
            underused = [gap['keyword'] for gap in keyword_gaps['underused_keywords']]
            recommendations.append({
                'type': 'keyword',
                'priority': 'medium',
                'recommendation': f"Increase usage of these keywords: {', '.join(underused)}",
                'impact': 'Medium - Improve keyword density for better relevance'
            })
        
        # Semantic gap recommendations
        if semantic_gaps:
            top_semantic_topics = [gap['topic'] for gap in semantic_gaps[:5]]
            recommendations.append({
                'type': 'semantic',
                'priority': 'medium',
                'recommendation': f"Cover these related concepts: {', '.join(top_semantic_topics)}",
                'impact': 'Medium - Improve topical relevance and comprehensiveness'
            })
        
        return recommendations
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()