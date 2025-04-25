import os
import spacy
import textstat
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, Request, Response, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Dict, List, Optional, Set, Any
import asyncio
import json
import aiohttp
from analyzers.competitor_analyzer import CompetitorAnalyzer
from analyzers.keyword_analyzer import KeywordAnalyzer
from analyzers.content_gap_analyzer import ContentGapAnalyzer
from analyzers.recommendation_engine import SEORecommendationEngine

# Load environment variables from .env file
load_dotenv()

# Load the spaCy English model
try:
    nlp = spacy.load("en_core_web_sm")
    print("spaCy model 'en_core_web_sm' loaded successfully.")
except OSError:
    print("Could not find spaCy model 'en_core_web_sm'.")
    print("Download it by running: python -m spacy download en_core_web_sm")
    nlp = None

app = FastAPI(
    title="SEO Analyzer Service",
    description="Comprehensive SEO analysis including competitor analysis, keyword opportunities, and content gap identification.",
    version="2.0.0"
)

# Initialize analyzers
competitor_analyzer = CompetitorAnalyzer()
keyword_analyzer = KeywordAnalyzer(nlp)
content_gap_analyzer = ContentGapAnalyzer(nlp)
recommendation_engine = SEORecommendationEngine()

# --- Data Models ---
class SeoInput(BaseModel):
    text: str
    target_keywords: list[str] | None = None
    competitor_urls: list[str] | None = None
    sessionId: str | None = None

class SeoOutput(BaseModel):
    readability_score: float | None = None
    keyword_density: dict[str, float] = {}
    meta_description: str | None = None
    meta_keywords: list[str] = []
    competitor_analysis: dict | None = None
    keyword_opportunities: dict | None = None
    content_gaps: dict | None = None
    seo_recommendations: list[dict] = []

class CompetitorAnalysisInput(BaseModel):
    competitor_urls: list[str]
    your_content: str
    target_keywords: list[str] | None = None

class KeywordResearchInput(BaseModel):
    seed_keywords: list[str]
    industry: str | None = None

# --- API Endpoints ---

@app.get("/")
async def read_root():
    """ Basic health check endpoint. """
    return {"message": "SEO Analyzer Service is running!"}

@app.post("/seo", response_model=SeoOutput)
async def analyze_seo(data: SeoInput, background_tasks: BackgroundTasks):
    """
    Comprehensive SEO analysis including readability, keyword density, 
    competitor analysis, keyword opportunities, and content gaps.
    """
    if nlp is None:
        raise HTTPException(status_code=503, detail="spaCy language model not loaded.")

    print(f"Received text for SEO analysis: {data.text[:50]}...")

    try:
        doc = nlp(data.text)
        
        # Basic analysis (existing functionality)
        readability_score = textstat.flesch_reading_ease(data.text)
        
        # Keyword density
        keyword_density_output = {}
        if data.target_keywords:
            text_lower = data.text.lower()
            total_words = len([token for token in doc if not token.is_punct])
            if total_words > 0:
                for keyword in data.target_keywords:
                    keyword_lower = keyword.lower()
                    count = text_lower.count(keyword_lower)
                    keyword_density_output[keyword] = round(count / total_words, 4) if total_words > 0 else 0
        
        # Generate meta description
        meta_description_output = None
        try:
            first_sentence = next(doc.sents).text.strip()
            max_desc_len = 160
            if len(first_sentence) > max_desc_len:
                last_space = first_sentence[:max_desc_len].rfind(' ')
                if last_space != -1:
                    meta_description_output = first_sentence[:last_space] + "..."
                else:
                    meta_description_output = first_sentence[:max_desc_len-3] + "..."
            else:
                meta_description_output = first_sentence
        except StopIteration:
            meta_description_output = data.text[:160]
        
        # Generate meta keywords
        meta_keywords_output = list(set(
            token.lemma_.lower()
            for token in doc
            if not token.is_stop and not token.is_punct and token.pos_ in ["NOUN", "PROPN"]
        ))
        
        # New analysis features
        competitor_analysis = None
        keyword_opportunities = None
        content_gaps = None
        seo_recommendations = []
        
        # Competitor analysis (if competitor URLs provided)
        if data.competitor_urls:
            competitor_analysis = await competitor_analyzer.analyze_competitors(
                data.competitor_urls, 
                data.text, 
                data.target_keywords
            )
        
        # Keyword opportunity identification
        keyword_opportunities = keyword_analyzer.find_opportunities(
            data.text, 
            data.target_keywords or []
        )
        
        # Content gap analysis
        if data.competitor_urls:
            content_gaps = await content_gap_analyzer.find_gaps(
                data.text, 
                data.competitor_urls, 
                data.target_keywords
            )
        
        # Generate SEO recommendations
        seo_recommendations = recommendation_engine.generate_recommendations(
            readability_score=readability_score,
            keyword_density=keyword_density_output,
            competitor_analysis=competitor_analysis,
            keyword_opportunities=keyword_opportunities,
            content_gaps=content_gaps
        )
        
        return SeoOutput(
            readability_score=readability_score,
            keyword_density=keyword_density_output,
            meta_description=meta_description_output,
            meta_keywords=meta_keywords_output,
            competitor_analysis=competitor_analysis,
            keyword_opportunities=keyword_opportunities,
            content_gaps=content_gaps,
            seo_recommendations=seo_recommendations
        )
        
    except Exception as e:
        print(f"Error during SEO analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Error during SEO analysis: {e}")

@app.post("/competitor-analysis")
async def analyze_competitors(data: CompetitorAnalysisInput):
    """Analyze competitor websites and compare with your content."""
    try:
        analysis = await competitor_analyzer.analyze_competitors(
            data.competitor_urls,
            data.your_content,
            data.target_keywords
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during competitor analysis: {e}")

@app.post("/keyword-research")
async def research_keywords(data: KeywordResearchInput):
    """Discover keyword opportunities based on seed keywords."""
    try:
        opportunities = keyword_analyzer.research_keywords(
            data.seed_keywords,
            data.industry
        )
        return opportunities
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during keyword research: {e}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "3006"))
    print(f"Starting SEO Analyzer Service on http://localhost:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)