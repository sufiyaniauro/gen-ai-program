import json
import csv
import io

class OutputHandler:
    """Handles different output methods for parsed data."""
    
    def print_to_console(self, data, format_type):
        """Print data to the console in a readable format."""
        if isinstance(data, str):
            print(data)
        elif format_type == "json":
            if isinstance(data, (dict, list)):
                print(json.dumps(data, indent=2))
            else:
                print(data)
        elif format_type == "csv" and isinstance(data, list) and data and isinstance(data[0], dict):
            self._print_csv_as_table(data)
        else:
            print(data)
    
    def write_to_file(self, data, file_path, format_type):
        """Write data to a file in the specified format."""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                if isinstance(data, str):
                    file.write(data)
                elif format_type == "json" and isinstance(data, (dict, list)):
                    json.dump(data, file, indent=2)
                else:
                    file.write(str(data))
            print(f"Data successfully written to {file_path}")
        except Exception as e:
            raise ValueError(f"Error writing to file: {str(e)}")
    
    def _print_csv_as_table(self, data):
        """Print CSV data as a formatted table."""
        if not data:
            print("No data")
            return
            
        headers = set()
        for row in data:
            headers.update(row.keys())
        headers = sorted(headers)
        
        widths = {header: len(header) for header in headers}
        for row in data:
            for header in headers:
                value = row.get(header, "")
                widths[header] = max(widths[header], len(str(value)))
        
        header_row = " | ".join(h.ljust(widths[h]) for h in headers)
        print(header_row)
        print("-" * len(header_row))
        
        for row in data:
            values = [str(row.get(h, "")).ljust(widths[h]) for h in headers]
            print(" | ".join(values))
