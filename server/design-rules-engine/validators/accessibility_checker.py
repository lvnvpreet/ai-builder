from typing import Dict, List, Any
from .validation_base import ValidationBase, ValidationIssue
from utils.accessibility_utils import check_wcag_compliance, calculate_focus_order

class AccessibilityChecker(ValidationBase):
    def validate(self, content: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate content for accessibility issues."""
        issues = []
        
        # Check for alt text on images
        issues.extend(self.check_alt_text(content))
        
        # Check for ARIA labels
        issues.extend(self.check_aria_labels(content))
        
        # Check heading structure
        issues.extend(self.check_heading_structure(content))
        
        # Check keyboard navigation
        issues.extend(self.check_keyboard_navigation(content))
        
        # Check focus order
        issues.extend(self.check_focus_order(content))
        
        # Check WCAG compliance
        issues.extend(self.check_wcag_compliance(content))
        
        return issues
    
    def check_alt_text(self, content: Dict[str, Any]) -> List[ValidationIssue]:
        """Check if all images have alt text."""
        issues = []
        
        for page in content.get("pages", []):
            for section in page.get("sections", []):
                elements = section.get("elements", [])
                for element in elements:
                    if element.get("type") == "image":
                        if not element.get("alt"):
                            issues.append(ValidationIssue(
                                rule_id="a11y_001",
                                severity="error",
                                message=f"Image missing alt text",
                                location=f"page.{page.get('id')}.section.{section.get('id')}.element.{element.get('id')}",
                                suggestions=["Add descriptive alt text for the image"]
                            ))
        
        return issues
    
    def check_aria_labels(self, content: Dict[str, Any]) -> List[ValidationIssue]:
        """Check if interactive elements have proper ARIA labels."""
        issues = []
        
        interactive_elements = ["button", "link", "input", "select", "textarea"]
        
        for page in content.get("pages", []):
            for section in page.get("sections", []):
                elements = section.get("elements", [])
                for element in elements:
                    if element.get("type") in interactive_elements:
                        if not element.get("aria-label") and not element.get("text"):
                            issues.append(ValidationIssue(
                                rule_id="a11y_002",
                                severity="error",
                                message=f"Interactive element missing ARIA label",
                                location=f"page.{page.get('id')}.section.{section.get('id')}.element.{element.get('id')}",
                                suggestions=["Add aria-label attribute or visible text"]
                            ))
        
        return issues
    
    def check_heading_structure(self, content: Dict[str, Any]) -> List[ValidationIssue]:
        """Check if heading structure is properly nested."""
        issues = []
        
        for page in content.get("pages", []):
            headings = []
            
            # Collect all headings
            for section in page.get("sections", []):
                elements = section.get("elements", [])
                for element in elements:
                    if element.get("type", "").startswith("h"):
                        headings.append({
                            "level": int(element["type"][1]),
                            "text": element.get("text", ""),
                            "location": f"page.{page.get('id')}.section.{section.get('id')}.element.{element.get('id')}"
                        })
            
            # Check heading hierarchy
            if headings:
                # Check for multiple h1
                h1_count = sum(1 for h in headings if h["level"] == 1)
                if h1_count > 1:
                    issues.append(ValidationIssue(
                        rule_id="a11y_003",
                        severity="warning",
                        message="Multiple h1 headings found on page",
                        location=f"page.{page.get('id')}",
                        suggestions=["Use only one h1 heading per page"]
                    ))
                elif h1_count == 0:
                    issues.append(ValidationIssue(
                        rule_id="a11y_003",
                        severity="error",
                        message="No h1 heading found on page",
                        location=f"page.{page.get('id')}",
                        suggestions=["Add an h1 heading to the page"]
                    ))
                
                # Check for proper nesting
                for i in range(1, len(headings)):
                    current_level = headings[i]["level"]
                    previous_level = headings[i-1]["level"]
                    
                    if current_level > previous_level + 1:
                        issues.append(ValidationIssue(
                            rule_id="a11y_004",
                            severity="error",
                            message=f"Heading level skipped: h{current_level} after h{previous_level}",
                            location=headings[i]["location"],
                            suggestions=[f"Use h{previous_level + 1} instead"]
                        ))
        
        return issues
    
    def check_keyboard_navigation(self, content: Dict[str, Any]) -> List[ValidationIssue]:
        """Check if all interactive elements are keyboard accessible."""
        issues = []
        
        for page in content.get("pages", []):
            for section in page.get("sections", []):
                elements = section.get("elements", [])
                for element in elements:
                    if element.get("type") in ["button", "link", "input", "select", "textarea"]:
                        # Check if element has tabindex
                        tabindex = element.get("tabindex")
                        if tabindex and int(tabindex) < -1:
                            issues.append(ValidationIssue(
                                rule_id="a11y_005",
                                severity="error",
                                message=f"Invalid tabindex value: {tabindex}",
                                location=f"page.{page.get('id')}.section.{section.get('id')}.element.{element.get('id')}",
                                suggestions=["Use tabindex values of -1, 0, or positive integers only"]
                            ))
                        
                        # Check for keyboard event handlers
                        if element.get("onClick") and not (element.get("onKeyPress") or element.get("onKeyDown")):
                            issues.append(ValidationIssue(
                                rule_id="a11y_006",
                                severity="warning",
                                message="Click handler without keyboard handler",
                                location=f"page.{page.get('id')}.section.{section.get('id')}.element.{element.get('id')}",
                                suggestions=["Add onKeyPress or onKeyDown handler for keyboard accessibility"]
                            ))
        
        return issues
    
    def check_focus_order(self, content: Dict[str, Any]) -> List[ValidationIssue]:
        """Check if focus order is logical."""
        issues = []
        
        for page in content.get("pages", []):
            # Calculate focus order
            focus_order = calculate_focus_order(page)
            
            # Check if focus order matches visual order
            visual_order = []
            for section in page.get("sections", []):
                for element in section.get("elements", []):
                    if element.get("type") in ["button", "link", "input", "select", "textarea"]:
                        visual_order.append(element.get("id"))
            
            # Compare orders
            if focus_order != visual_order:
                issues.append(ValidationIssue(
                    rule_id="a11y_007",
                    severity="warning",
                    message="Focus order doesn't match visual order",
                    location=f"page.{page.get('id')}",
                    suggestions=["Adjust tabindex values to match visual layout"]
                ))
        
        return issues
    
    def check_wcag_compliance(self, content: Dict[str, Any]) -> List[ValidationIssue]:
        """Check for WCAG compliance issues."""
        issues = []
        
        # Use utility function to check WCAG compliance
        wcag_issues = check_wcag_compliance(content)
        
        for issue in wcag_issues:
            issues.append(ValidationIssue(
                rule_id=f"wcag_{issue['criterion']}",
                severity=issue['severity'],
                message=issue['message'],
                location=issue['location'],
                suggestions=issue.get('suggestions', [])
            ))
        
        return issues