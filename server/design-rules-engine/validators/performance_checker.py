from typing import Dict, List, Any
from .validation_base import ValidationBase, ValidationIssue

class PerformanceChecker(ValidationBase):
    def validate(self, content: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate performance-related aspects of the design."""
        issues = []
        
        # Check image optimization
        issues.extend(self.check_image_optimization(content))
        
        # Check font loading
        issues.extend(self.check_font_loading(content))
        
        # Check animation performance
        issues.extend(self.check_animation_performance(content))
        
        # Check DOM complexity
        issues.extend(self.check_dom_complexity(content))
        
        # Check CSS complexity
        issues.extend(self.check_css_complexity(content))
        
        return issues
    
    def check_image_optimization(self, content: Dict[str, Any]) -> List[ValidationIssue]:
        """Check if images are optimized for web."""
        issues = []
        max_image_size_kb = 200
        
        for page in content.get("pages", []):
            for section in page.get("sections", []):
                elements = section.get("elements", [])
                for element in elements:
                    if element.get("type") == "image":
                        # Check image size
                        image_size = element.get("size_kb")
                        if image_size and image_size > max_image_size_kb:
                            issues.append(ValidationIssue(
                                rule_id="perf_001",
                                severity="warning",
                                message=f"Large image size: {image_size}KB",
                                location=f"page.{page.get('id')}.section.{section.get('id')}.element.{element.get('id')}",
                                suggestions=[
                                    f"Optimize image to be under {max_image_size_kb}KB",
                                    "Consider using WebP format",
                                    "Implement lazy loading"
                                ]
                            ))
                        
                        # Check for proper format
                        image_format = element.get("format", "").lower()
                        if image_format not in ["webp", "jpg", "jpeg", "png", "svg"]:
                            issues.append(ValidationIssue(
                                rule_id="perf_002",
                                severity="warning",
                                message=f"Non-optimal image format: {image_format}",
                                location=f"page.{page.get('id')}.section.{section.get('id')}.element.{element.get('id')}",
                                suggestions=["Use WebP for better compression"]
                            ))
                        
                        # Check for lazy loading
                        if not element.get("loading") == "lazy":
                            issues.append(ValidationIssue(
                                rule_id="perf_003",
                                severity="info",
                                message="Image without lazy loading",
                                location=f"page.{page.get('id')}.section.{section.get('id')}.element.{element.get('id')}",
                                suggestions=["Add loading='lazy' attribute for below-the-fold images"]
                            ))
        
        return issues
    
    def check_font_loading(self, content: Dict[str, Any]) -> List[ValidationIssue]:
        """Check font loading strategies."""
        issues = []
        
        fonts = content.get("fonts", [])
        if len(fonts) > 3:
            issues.append(ValidationIssue(
                rule_id="perf_004",
                severity="warning",
                message=f"Too many font families: {len(fonts)}",
                location="global.fonts",
                suggestions=["Limit to 2-3 font families maximum"]
            ))
        
        for font in fonts:
            # Check for font-display property
            if not font.get("font-display"):
                issues.append(ValidationIssue(
                    rule_id="perf_005",
                    severity="warning",
                    message=f"Font '{font.get('family')}' missing font-display property",
                    location=f"global.fonts.{font.get('family')}",
                    suggestions=["Add font-display: swap for better performance"]
                ))
            
            # Check for font weights
            weights = font.get("weights", [])
            if len(weights) > 4:
                issues.append(ValidationIssue(
                    rule_id="perf_006",
                    severity="info",
                    message=f"Font '{font.get('family')}' has many weights: {len(weights)}",
                    location=f"global.fonts.{font.get('family')}",
                    suggestions=["Consider reducing font weights to improve load time"]
                ))
        
        return issues
    
    def check_animation_performance(self, content: Dict[str, Any]) -> List[ValidationIssue]:
        """Check for performance-heavy animations."""
        issues = []
        
        for page in content.get("pages", []):
            for section in page.get("sections", []):
                elements = section.get("elements", [])
                for element in elements:
                    animations = element.get("animations", [])
                    for animation in animations:
                        # Check for transform vs layout properties
                        animated_properties = animation.get("properties", [])
                        layout_properties = ["width", "height", "top", "left", "margin", "padding"]
                        
                        for prop in animated_properties:
                            if prop in layout_properties:
                                issues.append(ValidationIssue(
                                    rule_id="perf_007",
                                    severity="warning",
                                    message=f"Animating layout property: {prop}",
                                    location=f"page.{page.get('id')}.section.{section.get('id')}.element.{element.get('id')}",
                                    suggestions=["Use transform and opacity for better performance"]
                                ))
                        
                        # Check animation duration
                        duration = animation.get("duration", 0)
                        if duration > 1000:  # 1 second
                            issues.append(ValidationIssue(
                                rule_id="perf_008",
                                severity="info",
                                message=f"Long animation duration: {duration}ms",
                                location=f"page.{page.get('id')}.section.{section.get('id')}.element.{element.get('id')}",
                                suggestions=["Consider shorter animations for better UX"]
                            ))
        
        return issues
    
    def check_dom_complexity(self, content: Dict[str, Any]) -> List[ValidationIssue]:
        """Check for excessive DOM complexity."""
        issues = []
        max_dom_depth = 15
        max_elements_per_section = 50
        
        for page in content.get("pages", []):
            # Check DOM depth
            dom_depth = self._calculate_dom_depth(page)
            if dom_depth > max_dom_depth:
                issues.append(ValidationIssue(
                    rule_id="perf_009",
                    severity="warning",
                    message=f"Excessive DOM depth: {dom_depth} levels",
                    location=f"page.{page.get('id')}",
                    suggestions=["Flatten DOM structure where possible"]
                ))
            
            # Check elements per section
            for section in page.get("sections", []):
                element_count = len(section.get("elements", []))
                if element_count > max_elements_per_section:
                    issues.append(ValidationIssue(
                        rule_id="perf_010",
                        severity="warning",
                        message=f"Too many elements in section: {element_count}",
                        location=f"page.{page.get('id')}.section.{section.get('id')}",
                        suggestions=["Consider breaking into smaller sections"]
                    ))
        
        return issues
    
    def check_css_complexity(self, content: Dict[str, Any]) -> List[ValidationIssue]:
        """Check for CSS complexity issues."""
        issues = []
        
        global_styles = content.get("global_styles", {})
        
        # Check for excessive selectors
        selectors = global_styles.get("selectors", [])
        if len(selectors) > 1000:
            issues.append(ValidationIssue(
                rule_id="perf_011",
                severity="warning",
                message=f"Excessive CSS selectors: {len(selectors)}",
                location="global.styles",
                suggestions=["Reduce CSS complexity and remove unused styles"]
            ))
        
        # Check for deep selector nesting
        for selector in selectors:
            nesting_level = selector.count(" ")
            if nesting_level > 3:
                issues.append(ValidationIssue(
                    rule_id="perf_012",
                    severity="info",
                    message=f"Deep selector nesting: {selector}",
                    location="global.styles",
                    suggestions=["Limit selector nesting to 2-3 levels"]
                ))
        
        # Check for inefficient selectors
        inefficient_patterns = ["*", "[id^=", "[class^=", ":not("]
        for selector in selectors:
            for pattern in inefficient_patterns:
                if pattern in selector:
                    issues.append(ValidationIssue(
                        rule_id="perf_013",
                        severity="info",
                        message=f"Potentially inefficient selector: {selector}",
                        location="global.styles",
                        suggestions=["Use more specific selectors for better performance"]
                    ))
                    break
        
        return issues
    
    def _calculate_dom_depth(self, element: Dict[str, Any], current_depth: int = 0) -> int:
        """Recursively calculate DOM depth."""
        max_depth = current_depth
        
        if isinstance(element, dict):
            children = element.get("children", [])
            for child in children:
                child_depth = self._calculate_dom_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
        
        return max_depth