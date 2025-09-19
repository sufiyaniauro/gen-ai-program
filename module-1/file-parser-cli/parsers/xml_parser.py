import xml.etree.ElementTree as ET
from parsers.base_parser import BaseParser

class XMLParser(BaseParser):
    """Parser for XML files."""
    
    def parse(self, file_path):
        """Parse XML file and return structured data as a dictionary."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            return self._xml_to_dict(root)
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing XML file: {str(e)}")
    
    def validate(self, data):
        """Validate XML data structure."""
        if data is None:
            return False, ["Data is null"]
        
        errors = []
        if isinstance(data, dict):
            self._validate_dict(data, errors)
            
        return len(errors) == 0, errors
    
    def _validate_dict(self, data, errors, prefix=""):
        """Validate a dictionary recursively."""
        for key, value in data.items():
            if key == "":
                errors.append(f"{prefix}Empty tag found")
            if isinstance(value, dict):
                self._validate_dict(value, errors, prefix=f"{prefix}{key}.")
    
    def _xml_to_dict(self, element):
        """Convert XML element to dictionary."""
        result = {}
        
        if element.attrib:
            result["@attributes"] = dict(element.attrib)
        
        for child in element:
            child_data = self._xml_to_dict(child)
            
            if child.tag in result:
                if type(result[child.tag]) is list:
                    result[child.tag].append(child_data)
                else:
                    result[child.tag] = [result[child.tag], child_data]
            else:
                result[child.tag] = child_data
        
        text = element.text.strip() if element.text else ""
        if text and not result:
            return text
        elif text:
            result["#text"] = text
            
        return result
