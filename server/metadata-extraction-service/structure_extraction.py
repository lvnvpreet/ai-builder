# server/metadata-extraction-service/structure_extraction.py
import re
import spacy
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import networkx as nx
from collections import defaultdict

class DocumentStructureExtractor:
    """Extract and analyze document structure."""
    
    def __init__(self, nlp=None):
        self.nlp = nlp or spacy.load("en_core_web_sm")
        
    def extract_structure(self, text: str, format: str = "text") -> Dict[str, Any]:
        """Extract document structure based on format."""
        if format == "html":
            return self._extract_html_structure(text)
        elif format == "markdown":
            return self._extract_markdown_structure(text)
        else:
            return self._extract_text_structure(text)
    
    def _extract_html_structure(self, html: str) -> Dict[str, Any]:
        """Extract structure from HTML content."""
        soup = BeautifulSoup(html, 'html.parser')
        
        structure = {
            "headings": [],
            "sections": [],
            "lists": [],
            "tables": [],
            "links": [],
            "hierarchy": {}
        }
        
        # Extract headings and create hierarchy
        heading_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        current_hierarchy = defaultdict(list)
        
        for tag in soup.find_all(heading_tags):
            level = int(tag.name[1])
            heading = {
                "level": level,
                "text": tag.get_text().strip(),
                "id": tag.get('id', ''),
                "position": len(structure["headings"])
            }
            structure["headings"].append(heading)
            current_hierarchy[level].append(heading)
        
        # Extract sections
        sections = soup.find_all(['section', 'article', 'div'])
        for section in sections:
            if section.get('class') or section.get('id'):
                structure["sections"].append({
                    "tag": section.name,
                    "id": section.get('id', ''),
                    "class": section.get('class', []),
                    "text_preview": section.get_text()[:100] + "..."
                })
        
        # Extract lists
        for list_tag in soup.find_all(['ul', 'ol']):
            items = [li.get_text().strip() for li in list_tag.find_all('li')]
            structure["lists"].append({
                "type": list_tag.name,
                "items": items,
                "position": len(structure["lists"])
            })
        
        # Extract tables
        for table in soup.find_all('table'):
            headers = [th.get_text().strip() for th in table.find_all('th')]
            rows = []
            for tr in table.find_all('tr'):
                cells = [td.get_text().strip() for td in tr.find_all('td')]
                if cells:
                    rows.append(cells)
            
            structure["tables"].append({
                "headers": headers,
                "rows": rows,
                "position": len(structure["tables"])
            })
        
        # Extract links
        for link in soup.find_all('a'):
            structure["links"].append({
                "text": link.get_text().strip(),
                "href": link.get('href', ''),
                "title": link.get('title', '')
            })
        
        # Build hierarchy tree
        structure["hierarchy"] = self._build_hierarchy_tree(structure["headings"])
        
        return structure
    
    def _extract_markdown_structure(self, markdown: str) -> Dict[str, Any]:
        """Extract structure from Markdown content."""
        structure = {
            "headings": [],
            "sections": [],
            "lists": [],
            "code_blocks": [],
            "links": [],
            "images": [],
            "hierarchy": {}
        }
        
        lines = markdown.split('\n')
        current_section = []
        
        for i, line in enumerate(lines):
            # Extract headings
            heading_match = re.match(r'^(#{1,6})\s+(.*)', line)
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2)
                structure["headings"].append({
                    "level": level,
                    "text": text,
                    "line_number": i,
                    "position": len(structure["headings"])
                })
                
                # Save current section
                if current_section:
                    structure["sections"].append({
                        "content": '\n'.join(current_section),
                        "start_line": i - len(current_section),
                        "end_line": i - 1
                    })
                    current_section = []
            else:
                current_section.append(line)
            
            # Extract lists
            list_match = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.*)', line)
            if list_match:
                indent = len(list_match.group(1))
                marker = list_match.group(2)
                content = list_match.group(3)
                
                structure["lists"].append({
                    "type": "ordered" if re.match(r'\d+\.', marker) else "unordered",
                    "indent_level": indent // 2,
                    "content": content,
                    "line_number": i
                })
            
            # Extract code blocks
            if line.startswith('```'):
                if not hasattr(self, '_in_code_block'):
                    self._in_code_block = False
                
                if not self._in_code_block:
                    self._in_code_block = True
                    self._code_block_start = i
                    self._code_block_language = line[3:].strip()
                else:
                    self._in_code_block = False
                    structure["code_blocks"].append({
                        "language": self._code_block_language,
                        "start_line": self._code_block_start,
                        "end_line": i,
                        "content": '\n'.join(lines[self._code_block_start + 1:i])
                    })
            
            # Extract links
            link_matches = re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', line)
            for match in link_matches:
                structure["links"].append({
                    "text": match.group(1),
                    "url": match.group(2),
                    "line_number": i
                })
            
            # Extract images
            image_matches = re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', line)
            for match in image_matches:
                structure["images"].append({
                    "alt_text": match.group(1),
                    "url": match.group(2),
                    "line_number": i
                })
        
        # Save last section
        if current_section:
            structure["sections"].append({
                "content": '\n'.join(current_section),
                "start_line": len(lines) - len(current_section),
                "end_line": len(lines) - 1
            })
        
        # Build hierarchy tree
        structure["hierarchy"] = self._build_hierarchy_tree(structure["headings"])
        
        return structure
    
    def _extract_text_structure(self, text: str) -> Dict[str, Any]:
        """Extract structure from plain text using NLP techniques."""
        doc = self.nlp(text)
        
        structure = {
            "sentences": [],
            "paragraphs": [],
            "sections": [],
            "entities": [],
            "key_phrases": [],
            "structural_patterns": {}
        }
        
        # Extract sentences
        for sent in doc.sents:
            structure["sentences"].append({
                "text": sent.text,
                "start": sent.start_char,
                "end": sent.end_char,
                "root": sent.root.text,
                "root_pos": sent.root.pos_
            })
        
        # Extract paragraphs (based on blank lines)
        paragraphs = re.split(r'\n\s*\n', text)
        current_pos = 0
        
        for para in paragraphs:
            if para.strip():
                structure["paragraphs"].append({
                    "text": para.strip(),
                    "start": current_pos,
                    "end": current_pos + len(para),
                    "word_count": len(para.split()),
                    "sentence_count": len(list(self.nlp(para).sents))
                })
            current_pos += len(para) + 2  # Account for \n\n
        
        # Detect sections based on capitalization patterns
        potential_headings = []
        for i, sent in enumerate(doc.sents):
            # Check if sentence is likely a heading
            if (len(sent.text.split()) < 10 and 
                sent.text.strip().endswith((':', '.')) and
                (sent.text.isupper() or sent.text.istitle())):
                potential_headings.append({
                    "text": sent.text.strip(),
                    "sentence_index": i,
                    "position": sent.start_char
                })
        
        # Create sections based on potential headings
        for i, heading in enumerate(potential_headings):
            start_pos = heading["position"]
            end_pos = potential_headings[i + 1]["position"] if i + 1 < len(potential_headings) else len(text)
            
            structure["sections"].append({
                "heading": heading["text"],
                "content": text[start_pos:end_pos].strip(),
                "start": start_pos,
                "end": end_pos
            })
        
        # Extract entities
        for ent in doc.ents:
            structure["entities"].append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
        
        # Extract key phrases using noun chunks
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) > 1:  # Only multi-word phrases
                structure["key_phrases"].append({
                    "text": chunk.text,
                    "root": chunk.root.text,
                    "start": chunk.start_char,
                    "end": chunk.end_char
                })
        
        # Identify structural patterns
        structure["structural_patterns"] = self._identify_structural_patterns(doc)
        
        return structure
    
    def _build_hierarchy_tree(self, headings: List[Dict]) -> Dict:
        """Build a hierarchical tree structure from headings."""
        if not headings:
            return {}
        
        root = {"level": 0, "text": "Document Root", "children": []}
        stack = [root]
        
        for heading in headings:
            level = heading["level"]
            
            # Pop stack until we find parent level
            while stack and stack[-1]["level"] >= level:
                stack.pop()
            
            # Create node for current heading
            node = {
                "level": level,
                "text": heading["text"],
                "position": heading.get("position", 0),
                "children": []
            }
            
            # Add to parent's children
            if stack:
                stack[-1]["children"].append(node)
            
            # Push to stack
            stack.append(node)
        
        return root
    
    def _identify_structural_patterns(self, doc) -> Dict[str, Any]:
        """Identify structural patterns in the document."""
        patterns = {
            "enumeration_patterns": [],
            "definition_patterns": [],
            "list_patterns": [],
            "comparison_patterns": []
        }
        
        # Detect enumeration patterns (First, Second, Third, etc.)
        enumeration_words = ["first", "second", "third", "fourth", "fifth", "finally", "lastly"]
        for sent in doc.sents:
            for token in sent:
                if token.text.lower() in enumeration_words:
                    patterns["enumeration_patterns"].append({
                        "text": sent.text,
                        "marker": token.text,
                        "position": sent.start_char
                    })
        
        # Detect definition patterns (X is Y, X means Y, etc.)
        definition_patterns = [
            r"(\w+)\s+(?:is|are|means|refers to|defined as)\s+(.+)",
            r"(?:define|definition of)\s+(\w+)\s+(?:is|as)\s+(.+)"
        ]
        
        for sent in doc.sents:
            for pattern in definition_patterns:
                match = re.search(pattern, sent.text, re.IGNORECASE)
                if match:
                    patterns["definition_patterns"].append({
                        "term": match.group(1),
                        "definition": match.group(2),
                        "sentence": sent.text,
                        "position": sent.start_char
                    })
        
        # Detect list patterns
        list_markers = ["•", "-", "*", "–", "—"]
        current_list = []
        
        for sent in doc.sents:
            if any(sent.text.strip().startswith(marker) for marker in list_markers):
                current_list.append(sent.text.strip())
            elif current_list:
                patterns["list_patterns"].append({
                    "items": current_list,
                    "position": sent.start_char
                })
                current_list = []
        
        # Detect comparison patterns
        comparison_words = ["compared to", "in contrast to", "unlike", "similar to", "different from"]
        for sent in doc.sents:
            for phrase in comparison_words:
                if phrase in sent.text.lower():
                    patterns["comparison_patterns"].append({
                        "text": sent.text,
                        "comparison_type": phrase,
                        "position": sent.start_char
                    })
        
        return patterns
    
    def analyze_document_complexity(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze document complexity based on structure."""
        complexity = {
            "structural_complexity": 0.0,
            "hierarchical_depth": 0,
            "section_count": 0,
            "average_section_length": 0.0,
            "list_density": 0.0,
            "cross_references": 0,
            "complexity_score": 0.0
        }
        
        # Calculate hierarchical depth
        def get_max_depth(node, current_depth=0):
            if not node.get("children"):
                return current_depth
            return max(get_max_depth(child, current_depth + 1) for child in node["children"])
        
        if "hierarchy" in structure and structure["hierarchy"]:
            complexity["hierarchical_depth"] = get_max_depth(structure["hierarchy"])
        
        # Count sections and calculate average length
        if "sections" in structure:
            complexity["section_count"] = len(structure["sections"])
            if structure["sections"]:
                total_length = sum(len(section.get("content", "").split()) for section in structure["sections"])
                complexity["average_section_length"] = total_length / len(structure["sections"])
        
        # Calculate list density
        if "lists" in structure and "paragraphs" in structure:
            total_words = sum(para.get("word_count", 0) for para in structure["paragraphs"])
            list_items = sum(len(lst.get("items", [])) for lst in structure["lists"])
            if total_words > 0:
                complexity["list_density"] = list_items / total_words
        
        # Count cross-references (links pointing to internal anchors)
        if "links" in structure:
            complexity["cross_references"] = sum(
                1 for link in structure["links"] 
                if link.get("href", "").startswith("#")
            )
        
        # Calculate overall complexity score
        complexity["structural_complexity"] = (
            complexity["hierarchical_depth"] * 0.3 +
            min(complexity["section_count"] / 10, 1.0) * 0.3 +
            min(complexity["average_section_length"] / 100, 1.0) * 0.2 +
            complexity["list_density"] * 0.1 +
            min(complexity["cross_references"] / 5, 1.0) * 0.1
        )
        
        complexity["complexity_score"] = round(complexity["structural_complexity"] * 100, 2)
        
        return complexity