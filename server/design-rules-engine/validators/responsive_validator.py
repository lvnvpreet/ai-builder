from typing import Dict, List, Any, Tuple
from .validation_base import ValidationBase, ValidationIssue

class ResponsiveValidator(ValidationBase):
    def __init__(self):
        super().__init__()
        self.breakpoints = {
            "mobile": 576,
            "tablet": 768,
            "desktop": 992,
            "large": 1200
        }
    
    def validate(self, content: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate responsive design aspects."""
        issues = []
        
        # Check breakpoint coverage
        issues.extend(self.check_breakpoint_coverage(content))
        
        # Check touch targets
        issues.extend(self.check_touch_targets(content))
        
        # Check flexible layouts
        issues.extend(self.check_flexible_layouts(content))
        
        # Check image responsiveness
        issues.extend(self.check_responsive_images(content))
        
        # Check text scaling
        issues.extend(self.check_text_scaling(content))
        
        return issues
    
    def check_breakpoint_coverage(self, content: Dict[str, Any]) -> List[ValidationIssue]:
        """Check if all breakpoints have appropriate styles."""
        issues = []
        
        for page in content.get("pages", []):
            for section in page.get("sections", []):
                responsive_styles = section.get("responsive_styles", {})
                
                # Check if mobile breakpoint is covered
                if "mobile" not in responsive_styles and section.get("layout") != "fluid":
                    issues.append(ValidationIssue(
                        rule_id="resp_001",
                        severity="error",
                        message="Missing mobile breakpoint styles",
                        location=f"page.{page.get('id')}.section.{section.get('id')}",
                        suggestions=["Add responsive styles for mobile breakpoint"]
                    ))
                
                # Check for proper layout changes at breakpoints
                desktop_layout = section.get("layout", {})
                mobile_layout = responsive_styles.get("mobile", {}).get("layout")
                
                if desktop_layout == "multi-column" and not mobile_layout:
                    issues.append(ValidationIssue(
                        rule_id="resp_002",
                        severity="warning",
                        message="Multi-column layout without mobile adjustment",
                        location=f"page.{page.get('id')}.section.{section.get('id')}",
                        suggestions=["Consider stacking columns vertically on mobile"]
                    ))
        
        return issues
    
    def check_touch_targets(self, content: Dict[str, Any]) -> List[ValidationIssue]:
        """Check if touch targets are appropriately sized for mobile."""
        issues = []
        min_touch_size = 44  # Apple HIG recommendation
        
        for page in content.get("pages", []):
            for section in page.get("sections", []):
                elements = section.get("elements", [])
                mobile_styles = section.get("responsive_styles", {}).get("mobile", {})
                
                for element in elements:
                    if element.get("type") in ["button", "link", "input", "select"]:
                        # Get mobile-specific styles if available
                        elem_mobile_style = mobile_styles.get("elements", {}).get(element.get("id"), {})
                        
                        # Check width and height
                        width = elem_mobile_style.get("width") or element.get("style", {}).get("width")
                        height = elem_mobile_style.get("height") or element.get("style", {}).get("height")
                        
                        if width and height:
                            # Convert to pixels if needed
                            width_px = self._convert_to_pixels(width)
                            height_px = self._convert_to_pixels(height)
                            
                            if width_px < min_touch_size or height_px < min_touch_size:
                                issues.append(ValidationIssue(
                                    rule_id="resp_003",
                                    severity="warning",
                                    message=f"Touch target too small: {width_px}x{height_px}px",
                                    location=f"page.{page.get('id')}.section.{section.get('id')}.element.{element.get('id')}",
                                    suggestions=[f"Increase size to at least {min_touch_size}x{min_touch_size}px on mobile"]
                                ))
        
        return issues
    
    def check_flexible_layouts(self, content: Dict[str, Any]) -> List[ValidationIssue]:
        """Check if layouts use flexible units and adapt to screen size."""
        issues = []
        
        for page in content.get("pages", []):
            for section in page.get("sections", []):
                layout = section.get("layout", {})
                
                # Check for fixed width layouts
                if layout.get("width") and self._is_fixed_unit(layout["width"]):
                    issues.append(ValidationIssue(
                        rule_id="resp_004",
                        severity="warning",
                        message="Fixed width layout detected",
                        location=f"page.{page.get('id')}.section.{section.get('id')}",
                        suggestions=["Use percentage or viewport units for responsive layouts"]
                    ))
                
                # Check grid/flex usage
                if layout.get("type") == "grid":
                    grid_template = layout.get("gridTemplateColumns")
                    if grid_template and "px" in str(grid_template):
                        issues.append(ValidationIssue(
                            rule_id="resp_005",
                            severity="warning",
                            message="Fixed pixel values in grid template",
                            location=f"page.{page.get('id')}.section.{section.get('id')}",
                            suggestions=["Use fr units or auto-fit/auto-fill for responsive grid"]
                        ))
        
        return issues
    
    def check_responsive_images(self, content: Dict[str, Any]) -> List[ValidationIssue]:
        """Check if images are responsive and have appropriate srcset."""
        issues = []
        
        for page in content.get("pages", []):
            for section in page.get("sections", []):
                elements = section.get("elements", [])
                for element in elements:
                    if element.get("type") == "image":
                        # Check for responsive attributes
                        if not element.get("srcset") and not element.get("sizes"):
                            issues.append(ValidationIssue(
                                rule_id="resp_006",
                                severity="warning",
                                message="Image without responsive attributes",
                                location=f"page.{page.get('id')}.section.{section.get('id')}.element.{element.get('id')}",
                                suggestions=["Add srcset and sizes attributes for responsive images"]
                            ))
                        
                        # Check for fixed dimensions
                        style = element.get("style", {})
                        if style.get("width") and self._is_fixed_unit(style["width"]):
                            issues.append(ValidationIssue(
                                rule_id="resp_007",
                                severity="warning",
                                message="Image with fixed width",
                                location=f"page.{page.get('id')}.section.{section.get('id')}.element.{element.get('id')}",
                                suggestions=["Use max-width: 100% for responsive images"]
                            ))
        
        return issues
    
    def check_text_scaling(self, content: Dict[str, Any]) -> List[ValidationIssue]:
        """Check if text scales appropriately across devices."""
        issues = []
        
        for page in content.get("pages", []):
            for section in page.get("sections", []):
                elements = section.get("elements", [])
                responsive_styles = section.get("responsive_styles", {})
                
                for element in elements:
                    if self._is_text_element(element):
                        desktop_font_size = element.get("style", {}).get("fontSize")
                        mobile_font_size = responsive_styles.get("mobile", {}).get("elements", {}).get(
                            element.get("id"), {}).get("fontSize")
                        
                        # Check if font size is too small on mobile
                        if mobile_font_size and self._convert_to_pixels(mobile_font_size) < 14:
                            issues.append(ValidationIssue(
                                rule_id="resp_008",
                                severity="warning",
                                message="Font size too small on mobile",
                                location=f"page.{page.get('id')}.section.{section.get('id')}.element.{element.get('id')}",
                                suggestions=["Minimum font size should be 14px on mobile"]
                            ))
                        
                        # Check if font size uses fixed units
                        if desktop_font_size and self._is_fixed_unit(desktop_font_size):
                            issues.append(ValidationIssue(
                                rule_id="resp_009",
                                severity="info",
                                message="Font size using fixed units",
                                location=f"page.{page.get('id')}.section.{section.get('id')}.element.{element.get('id')}",
                                suggestions=["Consider using rem or em units for better scaling"]
                            ))
        
        return issues
    
    def _is_fixed_unit(self, value: str) -> bool:
        """Check if a CSS value uses fixed units."""
        if isinstance(value, str):
            return "px" in value and not any(unit in value for unit in ["%", "vw", "vh", "em", "rem"])
        return False
    
    def _convert_to_pixels(self, value: Any) -> float:
        """Convert CSS value to pixels (simplified)."""
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str):
            if "px" in value:
                return float(value.replace("px", ""))
            elif "rem" in value:
                return float(value.replace("rem", "")) * 16  # Assuming 16px base font
            elif "em" in value:
                return float(value.replace("em", "")) * 16  # Simplified
        return 0
    
    def _is_text_element(self, element: Dict[str, Any]) -> bool:
        """Check if element contains text."""
        text_elements = ["p", "h1", "h2", "h3", "h4", "h5", "h6", "span", "a", "button", "label"]
        return element.get("type") in text_elements or element.get("text")