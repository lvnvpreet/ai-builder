from typing import Dict, List, Any, Optional
from enum import Enum
import json

class RuleCategory(str, Enum):
    LAYOUT = "layout"
    TYPOGRAPHY = "typography"
    COLOR = "color"
    SPACING = "spacing"
    ACCESSIBILITY = "accessibility"
    RESPONSIVE = "responsive"
    PERFORMANCE = "performance"
    CONSISTENCY = "consistency"

class RuleSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class DesignRule:
    def __init__(self, rule_id: str, category: RuleCategory, severity: RuleSeverity,
                 name: str, description: str, validation_function: str,
                 parameters: Dict[str, Any] = None):
        self.rule_id = rule_id
        self.category = category
        self.severity = severity
        self.name = name
        self.description = description
        self.validation_function = validation_function
        self.parameters = parameters or {}

class DesignRuleSet:
    def __init__(self):
        self.rules = self._load_default_rules()
    
    def _load_default_rules(self) -> List[DesignRule]:
        """Load default design rules."""
        return [
            # Layout Rules
            DesignRule(
                rule_id="layout_001",
                category=RuleCategory.LAYOUT,
                severity=RuleSeverity.ERROR,
                name="Grid Alignment",
                description="Elements should align to the grid system",
                validation_function="check_grid_alignment",
                parameters={"grid_columns": 12, "gutter": 30}
            ),
            DesignRule(
                rule_id="layout_002",
                category=RuleCategory.LAYOUT,
                severity=RuleSeverity.WARNING,
                name="Content Hierarchy",
                description="Content should follow proper visual hierarchy",
                validation_function="check_visual_hierarchy"
            ),
            
            # Typography Rules
            DesignRule(
                rule_id="typo_001",
                category=RuleCategory.TYPOGRAPHY,
                severity=RuleSeverity.ERROR,
                name="Font Size Range",
                description="Font sizes should be within acceptable range",
                validation_function="check_font_size_range",
                parameters={"min_size": 12, "max_size": 96}
            ),
            DesignRule(
                rule_id="typo_002",
                category=RuleCategory.TYPOGRAPHY,
                severity=RuleSeverity.WARNING,
                name="Line Height",
                description="Line height should be appropriate for readability",
                validation_function="check_line_height",
                parameters={"min_ratio": 1.2, "max_ratio": 1.8}
            ),
            
            # Color Rules
            DesignRule(
                rule_id="color_001",
                category=RuleCategory.COLOR,
                severity=RuleSeverity.ERROR,
                name="Contrast Ratio",
                description="Text contrast should meet WCAG guidelines",
                validation_function="check_contrast_ratio",
                parameters={"min_contrast_normal": 4.5, "min_contrast_large": 3.0}
            ),
            DesignRule(
                rule_id="color_002",
                category=RuleCategory.COLOR,
                severity=RuleSeverity.WARNING,
                name="Color Palette Consistency",
                description="Colors should be from the defined brand palette",
                validation_function="check_color_palette_consistency"
            ),
            
            # Spacing Rules
            DesignRule(
                rule_id="spacing_001",
                category=RuleCategory.SPACING,
                severity=RuleSeverity.WARNING,
                name="Consistent Spacing",
                description="Spacing should follow a consistent scale",
                validation_function="check_spacing_consistency",
                parameters={"spacing_scale": [4, 8, 16, 24, 32, 48, 64]}
            ),
            
            # Accessibility Rules
            DesignRule(
                rule_id="a11y_001",
                category=RuleCategory.ACCESSIBILITY,
                severity=RuleSeverity.ERROR,
                name="Alt Text",
                description="Images must have alt text",
                validation_function="check_alt_text"
            ),
            DesignRule(
                rule_id="a11y_002",
                category=RuleCategory.ACCESSIBILITY,
                severity=RuleSeverity.ERROR,
                name="ARIA Labels",
                description="Interactive elements must have ARIA labels",
                validation_function="check_aria_labels"
            ),
            
            # Responsive Rules
            DesignRule(
                rule_id="resp_001",
                category=RuleCategory.RESPONSIVE,
                severity=RuleSeverity.ERROR,
                name="Mobile Breakpoint",
                description="Layout must adapt to mobile breakpoint",
                validation_function="check_mobile_breakpoint",
                parameters={"breakpoint": 768}
            ),
            DesignRule(
                rule_id="resp_002",
                category=RuleCategory.RESPONSIVE,
                severity=RuleSeverity.WARNING,
                name="Touch Target Size",
                description="Touch targets should be at least 44x44px on mobile",
                validation_function="check_touch_target_size",
                parameters={"min_size": 44}
            ),
            
            # Performance Rules
            DesignRule(
                rule_id="perf_001",
                category=RuleCategory.PERFORMANCE,
                severity=RuleSeverity.WARNING,
                name="Image Optimization",
                description="Images should be optimized for web",
                validation_function="check_image_optimization",
                parameters={"max_size_kb": 200}
            ),
            
            # Consistency Rules
            DesignRule(
                rule_id="cons_001",
                category=RuleCategory.CONSISTENCY,
                severity=RuleSeverity.WARNING,
                name="Component Consistency",
                description="Similar components should have consistent styling",
                validation_function="check_component_consistency"
            )
        ]
    
    def get_all_rules(self) -> List[Dict[str, Any]]:
        """Get all rules as dictionaries."""
        return [self._rule_to_dict(rule) for rule in self.rules]
    
    def get_rules_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get rules by category."""
        category_rules = [rule for rule in self.rules if rule.category == category]
        return [self._rule_to_dict(rule) for rule in category_rules]
    
    def get_rule_by_id(self, rule_id: str) -> Optional[DesignRule]:
        """Get a specific rule by ID."""
        for rule in self.rules:
            if rule.rule_id == rule_id:
                return rule
        return None
    
    def _rule_to_dict(self, rule: DesignRule) -> Dict[str, Any]:
        """Convert rule to dictionary."""
        return {
            "rule_id": rule.rule_id,
            "category": rule.category,
            "severity": rule.severity,
            "name": rule.name,
            "description": rule.description,
            "validation_function": rule.validation_function,
            "parameters": rule.parameters
        }