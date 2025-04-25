from typing import Dict, List, Any

def check_wcag_compliance(content: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Check for WCAG compliance issues."""
    issues = []
    
    # Check for language attribute
    if not content.get("lang"):
        issues.append({
            "criterion": "3.1.1",
            "severity": "error",
            "message": "Missing language attribute",
            "location": "document",
            "suggestions": ["Add lang attribute to the HTML element"]
        })
    
    # Check for proper page title
    for page in content.get("pages", []):
        if not page.get("title"):
            issues.append({
                "criterion": "2.4.2",
                "severity": "error",
                "message": "Missing page title",
                "location": f"page.{page.get('id')}",
                "suggestions": ["Add a descriptive title to the page"]
            })
    
    # Check for skip links
    has_skip_link = False
    for page in content.get("pages", []):
        for section in page.get("sections", []):
            for element in section.get("elements", []):
                if element.get("type") == "link" and element.get("role") == "skip-link":
                    has_skip_link = True
                    break
    
    if not has_skip_link:
        issues.append({
            "criterion": "2.4.1",
            "severity": "warning",
            "message": "No skip link found",
            "location": "document",
            "suggestions": ["Add a skip link at the beginning of the page"]
        })
    
    return issues

def calculate_focus_order(page: Dict[str, Any]) -> List[str]:
    """Calculate the focus order for interactive elements."""
    focus_order = []
    interactive_elements = []
    
    # Collect all interactive elements
    for section in page.get("sections", []):
        for element in section.get("elements", []):
            if element.get("type") in ["button", "link", "input", "select", "textarea"]:
                interactive_elements.append({
                    "id": element.get("id"),
                    "tabindex": element.get("tabindex", 0),
                    "position": len(interactive_elements)
                })
    
    # Sort by tabindex, then by position
    interactive_elements.sort(key=lambda x: (x["tabindex"], x["position"]))
    
    # Extract IDs in order
    focus_order = [elem["id"] for elem in interactive_elements]
    
    return focus_order

def check_aria_validity(element: Dict[str, Any]) -> List[str]:
    """Check if ARIA attributes are valid for the element."""
    issues = []
    element_type = element.get("type")
    aria_role = element.get("role")
    
    # Check role validity
    valid_roles = {
        "button": ["button", "link", "menuitem", "tab"],
        "link": ["link", "button", "menuitem", "tab"],
        "div": ["region", "navigation", "main", "complementary", "banner", "contentinfo"],
        "section": ["region", "navigation", "main", "complementary"],
        # Add more mappings
    }
    
    if aria_role and element_type in valid_roles:
        if aria_role not in valid_roles[element_type]:
            issues.append(f"Invalid ARIA role '{aria_role}' for element type '{element_type}'")
    
    # Check required attributes for role
    required_attributes = {
        "tab": ["aria-selected", "aria-controls"],
        "slider": ["aria-valuenow", "aria-valuemin", "aria-valuemax"],
        "combobox": ["aria-expanded", "aria-controls"],
        # Add more mappings
    }
    
    if aria_role in required_attributes:
        for attr in required_attributes[aria_role]:
            if not element.get(attr):
                issues.append(f"Missing required attribute '{attr}' for role '{aria_role}'")
    
    return issues