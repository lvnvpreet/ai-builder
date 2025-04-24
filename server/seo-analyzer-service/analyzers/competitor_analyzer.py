import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Set
from urllib.parse import urlparse
import re
import spacy
import textstat

class CompetitorAnalyzer:
    """Analyze competitor websites for SEO metrics."""
    
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session
    
    async def fetch_url(self, url: str) -> str:
        """Fetch webpage content."""
        session = await self.get_session()
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"Failed to fetch {url}: Status {response.status}")
                    return ""
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""
    
    def extract_seo_data(self, html: str, url: str) -> Dict:
        """Extract SEO-relevant data from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract title
        title = soup.find('title')
        title_text = title.text.strip() if title else ""
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_desc_text = meta_desc['content'].strip() if meta_desc and meta_desc.has_attr('content') else ""
        
        # Extract meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        meta_keywords_text = meta_keywords['content'].strip() if meta_keywords and meta_keywords.has_attr('content') else ""
        
        # Extract headings
        h1_tags = [h1.text.strip() for h1 in soup.find_all('h1')]
        h2_tags = [h2.text.strip() for h2 in soup.find_all('h2')]
        h3_tags = [h3.text.strip() for h3 in soup.find_all('h3')]
        
        # Extract main content
        main_content = ""
        content_tags = soup.find_all(['article', 'main', 'div'])
        for tag in content_tags:
            if tag.get('class') and any('content' in str(c).lower() for c in tag.get('class')):
                main_content = tag.get_text(separator=' ', strip=True)
                break
        
        if not main_content:
            main_content = soup.get_text(separator=' ', strip=True)
        
        # Extract links
        internal_links = []
        external_links = []
        domain = urlparse(url).netloc
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('/') or domain in href:
                internal_links.append(href)
            elif href.startswith('http'):
                external_links.append(href)
        
        # Extract images with alt tags
        images = []
        for img in soup.find_all('img'):
            images.append({
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            })
        
        # Calculate word count
        word_count = len(main_content.split())
        
        # Calculate readability
        readability_score = textstat.flesch_reading_ease(main_content) if main_content else 0
        
        return {
            'url': url,
            'title': title_text,
            'title_length': len(title_text),
            'meta_description': meta_desc_text,
            'meta_description_length': len(meta_desc_text),
            'meta_keywords': meta_keywords_text,
            'h1_tags': h1_tags,
            'h2_tags': h2_tags,
            'h3_tags': h3_tags,
            'word_count': word_count,
            'readability_score': readability_score,
            'internal_links_count': len(internal_links),
            'external_links_count': len(external_links),
            'images_count': len(images),
            'images_with_alt': sum(1 for img in images if img['alt']),
            'content_preview': main_content[:500] + "..." if len(main_content) > 500 else main_content
        }
    
    async def analyze_competitors(self, competitor_urls: List[str], your_content: str, target_keywords: Optional[List[str]] = None) -> Dict:
        """Analyze competitor websites and compare with your content."""
        competitor_data = []
        
        # Fetch and analyze competitor websites
        for url in competitor_urls:
            html = await self.fetch_url(url)
            if html:
                data = self.extract_seo_data(html, url)
                if target_keywords:
                    data['keyword_usage'] = self.analyze_keyword_usage(html, target_keywords)
                competitor_data.append(data)
        
        # Analyze your content
        your_data = self.analyze_your_content(your_content, target_keywords)
        
        # Compare and generate insights
        insights = self.generate_comparative_insights(your_data, competitor_data)
        
        return {
            'your_analysis': your_data,
            'competitor_analysis': competitor_data,
            'insights': insights
        }
    
    def analyze_keyword_usage(self, content: str, keywords: List[str]) -> Dict[str, int]:
        """Analyze how keywords are used in content."""
        content_lower = content.lower()
        usage = {}
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            usage[keyword] = {
                'total_count': content_lower.count(keyword_lower),
                'title_count': content_lower.count(f"<title>.*{keyword_lower}.*</title>"),
                'h1_count': content_lower.count(f"<h1>.*{keyword_lower}.*</h1>"),
                'h2_count': content_lower.count(f"<h2>.*{keyword_lower}.*</h2>")
            }
        
        return usage
    
    def analyze_your_content(self, content: str, target_keywords: Optional[List[str]] = None) -> Dict:
        """Analyze your content for SEO metrics."""
        word_count = len(content.split())
        readability_score = textstat.flesch_reading_ease(content)
        
        # Basic keyword analysis
        keyword_usage = {}
        if target_keywords:
            content_lower = content.lower()
            for keyword in target_keywords:
                keyword_lower = keyword.lower()
                keyword_usage[keyword] = content_lower.count(keyword_lower)
        
        return {
            'word_count': word_count,
            'readability_score': readability_score,
            'keyword_usage': keyword_usage
        }
    
    def generate_comparative_insights(self, your_data: Dict, competitor_data: List[Dict]) -> Dict:
        """Generate insights by comparing your content with competitors."""
        insights = {
            'strengths': [],
            'weaknesses': [],
            'opportunities': [],
            'threats': []
        }
        
        if not competitor_data:
            return insights
        
        # Calculate averages from competitor data
        avg_word_count = sum(c['word_count'] for c in competitor_data) / len(competitor_data)
        avg_readability = sum(c['readability_score'] for c in competitor_data) / len(competitor_data)
        avg_title_length = sum(c['title_length'] for c in competitor_data) / len(competitor_data)
        avg_meta_desc_length = sum(c['meta_description_length'] for c in competitor_data) / len(competitor_data)
        
        # Compare word count
        if your_data['word_count'] > avg_word_count:
            insights['strengths'].append(f"Your content is more comprehensive ({your_data['word_count']} words vs average {avg_word_count:.0f})")
        else:
            insights['weaknesses'].append(f"Your content is shorter than competitors ({your_data['word_count']} words vs average {avg_word_count:.0f})")
        
        # Compare readability
        if your_data['readability_score'] > avg_readability:
            insights['strengths'].append(f"Your content is more readable (score: {your_data['readability_score']:.1f} vs average {avg_readability:.1f})")
        else:
            insights['weaknesses'].append(f"Your content could be more readable (score: {your_data['readability_score']:.1f} vs average {avg_readability:.1f})")
        
        # Identify opportunities
        all_h2_topics = set()
        for competitor in competitor_data:
            all_h2_topics.update(competitor['h2_tags'])
        
        if all_h2_topics:
            insights['opportunities'].append(f"Consider covering these topics: {', '.join(list(all_h2_topics)[:5])}")
        
        return insights
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()