from typing import Dict, List, Any, Tuple
from .validation_base import ValidationBase, ValidationIssue
from utils.color_utils import hex_to_rgb, calculate_contrast_ratio, get_luminance

class ContrastChecker(ValidationBase):
    def validate(self, content: Dict[str, Any], branding: Dict[str, Any] = None) -> List[ValidationIssue]:
        """Validate color contrast throughout the content."""
        issues = []
        
        # Check text contrast
        issues.extend(self.check_text_contrast(content, branding))
        
        # Check UI element contrast
        issues.extend(self.check_ui_contrast(content, branding))
        
        # Check brand color contrast
        if branding:
            issues.extend(self.check_brand_color_contrast(branding))
        
        return issues
    
    def check_text_contrast(self, content: Dict[str, Any], branding: Dict[str, Any] = None) -> List[ValidationIssue]:
        """Check contrast ratio for all text elements."""
        issues = []
        min_contrast_normal = 4.5  # WCAG AA standard
        min_contrast_large = 3.0   # WCAG AA standard for large text
        
        for page in content.get("pages", []):
            for section in page.get("sections", []):
                elements = section.get("elements", [])
                for element in elements:
                    if self._is_text_element(element):
                        text_color = element.get("style", {}).get("color")
                        bg_color = element.get("style", {}).get("backgroundColor")
                        
                        if text_color and bg_color:
                            contrast_ratio = calculate_contrast_ratio(text_color, bg_color)
                            is_large_text = self._is_large_text(element)
                            min_required = min_contrast_large if is_large_text else min_contrast_normal
                            
                            if contrast_ratio < min_required:
                                issues.append(ValidationIssue(
                                    rule_id="color_001",
                                    severity="error",
                                    message=f"Insufficient contrast ratio: {contrast_ratio:.2f} (min: {min_required})",
                                    location=f"page.{page.get('id')}.section.{section.get('id')}.element.{element.get('id')}",
                                    suggestions=[
                                        f"Adjust text color to achieve contrast ratio >= {min_required}",
                                        f"Current: {text_color} on {bg_color}"
                                    ]
                                ))
        
        return issues
    
    def check_ui_contrast(self, content: Dict[str, Any], branding: Dict[str, Any] = None) -> List[ValidationIssue]:
        """Check contrast for UI elements (buttons, form fields, etc.)."""
        issues = []
        min_ui_contrast = 3.0  # WCAG AA standard for UI components
        
        ui_elements = ["button", "input", "select", "textarea"]
        
        for page in content.get("pages", []):
            for section in page.get("sections", []):
                elements = section.get("elements", [])
                for element in elements:
                    if element.get("type") in ui_elements:
                        # Check border contrast
                        border_color = element.get("style", {}).get("borderColor")
                        bg_color = element.get("style", {}).get("backgroundColor")
                        
                        if border_color and bg_color:
                            contrast_ratio = calculate_contrast_ratio(border_color, bg_color)
                            if contrast_ratio < min_ui_contrast:
                                issues.append(ValidationIssue(
                                    rule_id="color_003",
                                    severity="warning",
                                    message=f"Low UI element contrast: {contrast_ratio:.2f}",
                                    location=f"page.{page.get('id')}.section.{section.get('id')}.element.{element.get('id')}",
                                    suggestions=[f"Increase border contrast to at least {min_ui_contrast}"]
                                ))
                        
                        # Check focus state contrast
                        focus_border = element.get("style", {}).get("focusBorderColor")
                        if focus_border and bg_color:
                            contrast_ratio = calculate_contrast_ratio(focus_border, bg_color)
                            if contrast_ratio < min_ui_contrast:
                                issues.append(ValidationIssue(
                                    rule_id="color_004",
                                    severity="error",
                                    message=f"Low focus indicator contrast: {contrast_ratio:.2f}",
                                    location=f"page.{page.get('id')}.section.{section.get('id')}.element.{element.get('id')}",
                                    suggestions=[f"Increase focus indicator contrast to at least {min_ui_contrast}"]
                                ))
        
        return issues
    
    def check_brand_color_contrast(self, branding: Dict[str, Any]) -> List[ValidationIssue]:
        """Check contrast between brand colors."""
        issues = []
        
        primary_color = branding.get("primary_color")
        secondary_color = branding.get("secondary_color")
        text_color = branding.get("text_color", "#000000")
        background_color = branding.get("background_color", "#FFFFFF")
        
        # Check primary color against background
        if primary_color and background_color:
            contrast_ratio = calculate_contrast_ratio(primary_color, background_color)
            if contrast_ratio < 4.5:
                issues.append(ValidationIssue(
                    rule_id="color_005",
                    severity="warning",
                    message=f"Primary brand color has low contrast with background: {contrast_ratio:.2f}",
                    location="branding.primary_color",
                    suggestions=["Consider adjusting primary color for better contrast"]
                ))
        
        # Check secondary color against background
        if secondary_color and background_color:
            contrast_ratio = calculate_contrast_ratio(secondary_color, background_color)
            if contrast_ratio < 4.5:
                issues.append(ValidationIssue(
                    rule_id="color_005",
                    severity="warning",
                    message=f"Secondary brand color has low contrast with background: {contrast_ratio:.2f}",
                    location="branding.secondary_color",
                    suggestions=["Consider adjusting secondary color for better contrast"]
                ))
        
        # Check text color against primary color (for buttons, etc.)
        if text_color and primary_color:
            contrast_ratio = calculate_contrast_ratio(text_color, primary_color)
            if contrast_ratio < 4.5:
                issues.append(ValidationIssue(
                    rule_id="color_006",
                    severity="error",
                    message=f"Text color has low contrast with primary color: {contrast_ratio:.2f}",
                    location="branding.text_color",
                    suggestions=["Adjust text color for better readability on primary color"]
                ))
        
        return issues
    
    def _is_text_element(self, element: Dict[str, Any]) -> bool:
        """Check if element contains text."""
        text_elements = ["p", "h1", "h2", "h3", "h4", "h5", "h6", "span", "a", "button", "label"]
        return element.get("type") in text_elements or element.get("text")
    
    def _is_large_text(self, element: Dict[str, Any]) -> bool:
        """Check if text is considered large (18pt or 14pt bold)."""
        font_size = element.get("style", {}).get("fontSize", 16)
        font_weight = element.get("style", {}).get("fontWeight", "normal")
        
        if isinstance(font_size, str):
            font_size = int(font_size.replace("px", ""))
        
        is_bold = font_weight in ["bold", "700", "800", "900"]
        
        return (font_size >= 18) or (font_size >= 14 and is_bold)