import os
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from rules.rule_definitions import DesignRuleSet
from validators.design_validator import DesignValidator
from validators.accessibility_checker import AccessibilityChecker
from validators.contrast_checker import ContrastChecker
from validators.responsive_validator import ResponsiveValidator
from validators.performance_checker import PerformanceChecker

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Design Rules Engine",
    description="Validates generated website content/styles against design rules (consistency, contrast, etc.).",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize validators
rule_set = DesignRuleSet()
design_validator = DesignValidator(rule_set)
accessibility_checker = AccessibilityChecker()
contrast_checker = ContrastChecker()
responsive_validator = ResponsiveValidator()
performance_checker = PerformanceChecker()

# --- Data Models ---
class DesignInput(BaseModel):
    template_id: str
    generated_content: Dict[str, Any]  # Structure representing pages, sections, styles
    branding: Dict[str, Any] | None = None
    validate_accessibility: bool = True
    validate_contrast: bool = True
    validate_responsive: bool = True
    validate_performance: bool = True

class ValidationIssue(BaseModel):
    rule_id: str
    severity: str  # 'error', 'warning', 'info'
    message: str
    location: str
    suggestions: List[str] = []

class ValidationResult(BaseModel):
    passed: bool
    issues: List[ValidationIssue] = []
    scores: Dict[str, float] = {}
    summary: Dict[str, int] = {}

# --- API Endpoints ---

@app.get("/")
async def read_root():
    """Basic health check endpoint."""
    return {"message": "Design Rules Engine is running!"}

@app.post("/validate-design", response_model=ValidationResult)
async def validate_design(data: DesignInput):
    """
    Validate design against all rules including consistency, contrast, accessibility, etc.
    """
    try:
        issues = []
        scores = {}
        
        # 1. General design validation
        design_issues = design_validator.validate(data.generated_content, data.branding)
        issues.extend(design_issues)
        scores['design'] = design_validator.calculate_score(design_issues)
        
        # 2. Accessibility validation
        if data.validate_accessibility:
            accessibility_issues = accessibility_checker.validate(data.generated_content)
            issues.extend(accessibility_issues)
            scores['accessibility'] = accessibility_checker.calculate_score(accessibility_issues)
        
        # 3. Contrast validation
        if data.validate_contrast and data.branding:
            contrast_issues = contrast_checker.validate(data.generated_content, data.branding)
            issues.extend(contrast_issues)
            scores['contrast'] = contrast_checker.calculate_score(contrast_issues)
        
        # 4. Responsive design validation
        if data.validate_responsive:
            responsive_issues = responsive_validator.validate(data.generated_content)
            issues.extend(responsive_issues)
            scores['responsive'] = responsive_validator.calculate_score(responsive_issues)
        
        # 5. Performance validation
        if data.validate_performance:
            performance_issues = performance_checker.validate(data.generated_content)
            issues.extend(performance_issues)
            scores['performance'] = performance_checker.calculate_score(performance_issues)
        
        # Calculate summary
        summary = {
            'total_issues': len(issues),
            'errors': len([i for i in issues if i.severity == 'error']),
            'warnings': len([i for i in issues if i.severity == 'warning']),
            'info': len([i for i in issues if i.severity == 'info'])
        }
        
        # Determine if validation passed
        passed = summary['errors'] == 0
        
        return ValidationResult(
            passed=passed,
            issues=issues,
            scores=scores,
            summary=summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@app.get("/rules")
async def get_rules():
    """Get all available design rules."""
    return rule_set.get_all_rules()

@app.get("/rules/{category}")
async def get_rules_by_category(category: str):
    """Get design rules by category."""
    rules = rule_set.get_rules_by_category(category)
    if not rules:
        raise HTTPException(status_code=404, detail=f"No rules found for category: {category}")
    return rules

# --- Run the server (for local development) ---
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "3010"))
    print(f"Starting Design Rules Engine on http://localhost:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)