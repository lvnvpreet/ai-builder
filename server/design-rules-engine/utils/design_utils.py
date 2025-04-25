from typing import Dict, List, Any

def extract_styles(content: Dict[str, Any]) -> Dict[str, Any]:
    """Extract all styles from content."""
    styles = {}
    
    # Extract global styles
    styles["global"] = content.get("global_styles", {})
    
    # Extract page-specific styles
    for page in content.get("pages", []):
        page_id = page.get("id")
        styles[f"page_{page_id}"] = page.get("styles", {})
        
        # Extract section styles
        for section in page.get("sections", []):
            section_id = section.get("id")
            styles[f"page_{page_id}_section_{section_id}"] = section.get("styles", {})
    
    return styles

def extract_elements(content: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract all elements from content."""
    elements = []
    
    for page in content.get("pages", []):
        for section in page.get("sections", []):
            for element in section.get("elements", []):
                # Add page and section context
                element_with_context = element.copy()
                element_with_context["page_id"] = page.get("id")
                element_with_context["section_id"] = section.get("id")
                elements.append(element_with_context)
    
    return elements

def find_element_by_id(content: Dict[str, Any], element_id: str) -> Dict[str, Any]:
    """Find an element by its ID."""
    for page in content.get("pages", []):
        for section in page.get("sections", []):
            for element in section.get("elements", []):
                if element.get("id") == element_id:
                    return element
    return {}

def get_element_path(element: Dict[str, Any]) -> str:
    """Get the full path to an element."""
    page_id = element.get("page_id", "unknown")
    section_id = element.get("section_id", "unknown")
    element_id = element.get("id", "unknown")
    return f"page.{page_id}.section.{section_id}.element.{element_id}"