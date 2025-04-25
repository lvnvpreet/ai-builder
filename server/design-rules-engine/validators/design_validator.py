from typing import Dict, List, Any
from rules.rule_definitions import DesignRuleSet, RuleCategory
from utils.design_utils import extract_styles, extract_elements
from .validation_base import ValidationBase, ValidationIssue

class DesignValidator(ValidationBase):
    def __init__(self, rule_set: DesignRuleSet):
        super().__init__()
        self.rule_set = rule_set
    
    def validate(self, content: Dict[str, Any], branding: Dict[str, Any] = None) -> List[ValidationIssue]:
        """Validate design against all general design rules."""
        issues = []
        
        # Extract design elements
        styles = extract_styles(content)
        elements = extract_elements(content)
        
        # Run validation for each rule
        for rule in self.rule_set.rules:
            if rule.category in [RuleCategory.LAYOUT, RuleCategory.TYPOGRAPHY, 
                               RuleCategory.SPACING, RuleCategory.CONSISTENCY]:
                method_name = rule.validation_function
                if hasattr(self, method_name):
                    method = getattr(self, method_name)
                    rule_issues = method(elements, styles, rule, branding)
                    issues.extend(rule_issues)
        
        return issues
    
    def check_grid_alignment(self, elements: List[Dict], styles: Dict[str, Any], 
                           rule: Any, branding: Dict[str, Any] = None) -> List[ValidationIssue]:
        """Check if elements align to the grid system."""
        issues = []
        grid_columns = rule.parameters.get("grid_columns", 12)
        gutter = rule.parameters.get("gutter", 30)
        
        for element in elements:
            if element.get("type") == "container":
                width = element.get("style", {}).get("width")
                if width and isinstance(width, (int, float)):
                    # Check if width is a multiple of column width
                    column_width = 100 / grid_columns
                    if width % column_width > 0.1:  # Allow small rounding errors
                        issues.append(ValidationIssue(
                            rule_id=rule.rule_id,
                            severity=rule.severity,
                            message=f"Element '{element.get('id', 'unknown')}' does not align to grid",
                            location=f"element.{element.get('id', 'unknown')}",
                            suggestions=[
                                f"Adjust width to nearest grid column: {round(width / column_width) * column_width}%"
                            ]
                        ))
        
        return issues
    
    def check_visual_hierarchy(self, elements: List[Dict], styles: Dict[str, Any], 
                             rule: Any, branding: Dict[str, Any] = None) -> List[ValidationIssue]:
        """Check if content follows proper visual hierarchy."""
        issues = []
        
        # Extract headings
        headings = [e for e in elements if e.get("type") in ["h1", "h2", "h3", "h4", "h5", "h6"]]
        
        if headings:
            # Check heading order
            current_level = 0
            for heading in headings:
                level = int(heading["type"][1])
                if level > current_level + 1:
                    issues.append(ValidationIssue(
                        rule_id=rule.rule_id,
                        severity=rule.severity,
                        message=f"Heading level skipped: {heading['type']} after h{current_level}",
                        location=f"element.{heading.get('id', 'unknown')}",
                        suggestions=[f"Use h{current_level + 1} instead"]
                    ))
                current_level = level
        
        return issues
    
    def check_font_size_range(self, elements: List[Dict], styles: Dict[str, Any], 
                            rule: Any, branding: Dict[str, Any] = None) -> List[ValidationIssue]:
        """Check if font sizes are within acceptable range."""
        issues = []
        min_size = rule.parameters.get("min_size", 12)
        max_size = rule.parameters.get("max_size", 96)
        
        for element in elements:
            font_size = element.get("style", {}).get("fontSize")
            if font_size and isinstance(font_size, (int, float)):
                if font_size < min_size:
                    issues.append(ValidationIssue(
                        rule_id=rule.rule_id,
                        severity=rule.severity,
                        message=f"Font size too small: {font_size}px",
                        location=f"element.{element.get('id', 'unknown')}",
                        suggestions=[f"Increase font size to at least {min_size}px"]
                    ))
                elif font_size > max_size:
                    issues.append(ValidationIssue(
                        rule_id=rule.rule_id,
                        severity=rule.severity,
                        message=f"Font size too large: {font_size}px",
                        location=f"element.{element.get('id', 'unknown')}",
                        suggestions=[f"Decrease font size to at most {max_size}px"]
                    ))
        
        return issues
    
    def check_line_height(self, elements: List[Dict], styles: Dict[str, Any], 
                         rule: Any, branding: Dict[str, Any] = None) -> List[ValidationIssue]:
        """Check if line height is appropriate for readability."""
        issues = []
        min_ratio = rule.parameters.get("min_ratio", 1.2)
        max_ratio = rule.parameters.get("max_ratio", 1.8)
        
        for element in elements:
            font_size = element.get("style", {}).get("fontSize")
            line_height = element.get("style", {}).get("lineHeight")
            
            if font_size and line_height and isinstance(font_size, (int, float)):
                if isinstance(line_height, str) and line_height.endswith("%"):
                    ratio = float(line_height.strip("%")) / 100
                elif isinstance(line_height, (int, float)):
                    ratio = line_height / font_size
                else:
                    continue
                
                if ratio < min_ratio:
                    issues.append(ValidationIssue(
                        rule_id=rule.rule_id,
                        severity=rule.severity,
                        message=f"Line height ratio too small: {ratio:.2f}",
                        location=f"element.{element.get('id', 'unknown')}",
                        suggestions=[f"Increase line height to at least {min_ratio * font_size}px"]
                    ))
                elif ratio > max_ratio:
                    issues.append(ValidationIssue(
                        rule_id=rule.rule_id,
                        severity=rule.severity,
                        message=f"Line height ratio too large: {ratio:.2f}",
                        location=f"element.{element.get('id', 'unknown')}",
                        suggestions=[f"Decrease line height to at most {max_ratio * font_size}px"]
                    ))
        
        return issues
    
    def check_spacing_consistency(self, elements: List[Dict], styles: Dict[str, Any], 
                                rule: Any, branding: Dict[str, Any] = None) -> List[ValidationIssue]:
        """Check if spacing follows a consistent scale."""
        issues = []
        spacing_scale = rule.parameters.get("spacing_scale", [4, 8, 16, 24, 32, 48, 64])
        
        for element in elements:
            style = element.get("style", {})
            for prop in ["margin", "padding"]:
                value = style.get(prop)
                if value and isinstance(value, (int, float)):
                    if not any(abs(value - scale_value) < 1 for scale_value in spacing_scale):
                        closest = min(spacing_scale, key=lambda x: abs(x - value))
                        issues.append(ValidationIssue(
                            rule_id=rule.rule_id,
                            severity=rule.severity,
                            message=f"{prop} value {value}px not in spacing scale",
                            location=f"element.{element.get('id', 'unknown')}.{prop}",
                            suggestions=[f"Use {closest}px instead"]
                        ))
        
        return issues
    
    def check_component_consistency(self, elements: List[Dict], styles: Dict[str, Any], 
                                  rule: Any, branding: Dict[str, Any] = None) -> List[ValidationIssue]:
        """Check if similar components have consistent styling."""
        issues = []
        
        # Group elements by type
        element_groups = {}
        for element in elements:
            elem_type = element.get("type")
            if elem_type:
                if elem_type not in element_groups:
                    element_groups[elem_type] = []
                element_groups[elem_type].append(element)
        
        # Check consistency within each group
        for elem_type, group in element_groups.items():
            if len(group) > 1:
                # Compare styles of elements in the group
                reference_style = group[0].get("style", {})
                for i, element in enumerate(group[1:], 1):
                    current_style = element.get("style", {})
                    
                    # Check for style differences
                    for prop in ["fontSize", "color", "backgroundColor", "padding", "margin"]:
                        if prop in reference_style and prop in current_style:
                            if reference_style[prop] != current_style[prop]:
                                issues.append(ValidationIssue(
                                    rule_id=rule.rule_id,
                                    severity=rule.severity,
                                    message=f"Inconsistent {prop} for {elem_type} elements",
                                    location=f"element.{element.get('id', 'unknown')}.{prop}",
                                    suggestions=[f"Use {reference_style[prop]} to match other {elem_type} elements"]
                                ))
        
        return issues