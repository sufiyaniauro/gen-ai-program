import xml.dom.minidom as md
import xml.etree.ElementTree as ET
from transformers.base_transformer import BaseTransformer

class XMLTransformer(BaseTransformer):
    """Transformer to convert data to XML format."""
    
    def transform(self, data):
        """Transform data to XML format.
        
        Args:
            data: Input data (dict, list, or string)
            
        Returns:
            str: XML formatted string
        """
        if isinstance(data, dict):
            return self._dict_to_xml(data)
        elif isinstance(data, list):
            if all(isinstance(item, dict) for item in data):
                return self._list_of_dicts_to_xml(data)
            else:
                return self._list_to_xml(data)
        elif isinstance(data, str):
            try:
                md.parseString(data)  
                return data
            except Exception:
                lines = data.strip().split('\n')
                return self._list_to_xml(lines)
        else:
            raise ValueError(f"Cannot convert {type(data)} to XML")
    
    def _dict_to_xml(self, data, root_name="root"):
        """Convert a dictionary to XML."""
        root = ET.Element(root_name)
        self._add_dict_to_element(root, data)
        
        xml_str = ET.tostring(root, encoding='unicode')
        dom = md.parseString(xml_str)
        return dom.toprettyxml(indent="  ")
    
    def _add_dict_to_element(self, parent, data):
        """Add dictionary data to an XML element."""
        for key, value in data.items():
            if key.startswith('@'):
                parent.set(key[1:], str(value))
            elif isinstance(value, dict):
                child = ET.SubElement(parent, key)
                self._add_dict_to_element(child, value)
            elif isinstance(value, list):
                for item in value:
                    child = ET.SubElement(parent, key)
                    if isinstance(item, dict):
                        self._add_dict_to_element(child, item)
                    else:
                        child.text = str(item)
            else:
                child = ET.SubElement(parent, key)
                child.text = str(value)
    
    def _list_of_dicts_to_xml(self, data):
        """Convert a list of dictionaries to XML."""
        root = ET.Element("root")
        for i, item in enumerate(data):
            child = ET.SubElement(root, f"item")
            self._add_dict_to_element(child, item)
        
        xml_str = ET.tostring(root, encoding='unicode')
        dom = md.parseString(xml_str)
        return dom.toprettyxml(indent="  ")
    
    def _list_to_xml(self, data):
        """Convert a simple list to XML."""
        root = ET.Element("root")
        for item in data:
            child = ET.SubElement(root, "item")
            child.text = str(item)
        
        xml_str = ET.tostring(root, encoding='unicode')
        dom = md.parseString(xml_str)
        return dom.toprettyxml(indent="  ")
