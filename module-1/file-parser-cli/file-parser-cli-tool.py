#!/usr/bin/env python3
import argparse
import os
import sys
import tempfile
from parsers.parser_factory import ParserFactory
from transformers.transformer_factory import TransformerFactory
from utils.output_handler import OutputHandler

VERSION = "1.0.0"

def print_banner():
    banner = f"""
    ╔═══════════════════════════════════════════════════╗
    ║           File Parser CLI Tool v{VERSION}              ║
    ╚═══════════════════════════════════════════════════╝
    """
    print(banner)

def print_usage_examples():
    examples = """
Examples:
    # Parse a CSV file and print to console
    python file-parser-cli-tool.py data.csv
    
    # Parse a JSON file and transform to CSV format
    python file-parser-cli-tool.py data.json -t csv
    
    # Parse a file, validate it, and save to output file
    python file-parser-cli-tool.py data.xml -v -o output.xml
    
    # Filter data and transform it
    python file-parser-cli-tool.py data.csv -q "column=value" -t json
    
    # Read from stdin (pipe)
    cat data.csv | python file-parser-cli-tool.py - -f csv
    
    # Start in interactive mode
    python file-parser-cli-tool.py --interactive
    """
    print(examples)

def get_user_input(prompt, options=None, allow_empty=False):
    while True:
        value = input(prompt).strip()
        if value or allow_empty:
            if options and value and value not in options:
                print(f"Please enter one of: {', '.join(options)}")
                continue
            return value

def interactive_mode():
    print_banner()
    print("\nWelcome to the interactive File Parser Tool!")
    print("Follow the prompts to process your files.\n")
    
    while True:
        print("\n" + "="*50)
        print("MAIN MENU")
        print("="*50)
        print("1. Parse a file")
        print("2. Transform a file to another format")
        print("3. Validate a file")
        print("4. Query/Filter data from a file")
        print("5. Show usage examples")
        print("0. Exit")
        
        choice = get_user_input("\nEnter your choice (0-5): ", options=["0", "1", "2", "3", "4", "5"])
        
        if choice == "0":
            print("\nExiting the File Parser Tool. Goodbye!")
            return
        elif choice == "5":
            print_usage_examples()
            continue
            
        file_path = get_user_input("\nEnter the path to your file: ")
        
        if not os.path.isfile(file_path):
            print(f"Error: File {file_path} not found")
            continue
            
        file_format = os.path.splitext(file_path)[1][1:].lower()
        if file_format not in ["csv", "json", "xml", "txt", "log"]:
            print("Could not determine file format from extension.")
            file_format = get_user_input(
                "Enter file format (csv, json, xml, txt, log): ",
                options=["csv", "json", "xml", "txt", "log"]
            )
        else:
            print(f"Detected file format: {file_format}")
            
        try:
            parser_factory = ParserFactory()
            file_parser = parser_factory.get_parser(file_format)
            
            data = file_parser.parse(file_path)
            print(f"Successfully parsed {file_path}")
            
            if choice == "1":
                output_choice = get_user_input(
                    "\nDisplay output to (1) console or (2) file? Enter 1 or 2: ", 
                    options=["1", "2"]
                )
                
                if output_choice == "2":
                    output_path = get_user_input("Enter output file path: ")
                    output_handler = OutputHandler()
                    output_handler.write_to_file(data, output_path, file_format)
                    print(f"Successfully wrote output to {output_path}")
                else:
                    output_handler = OutputHandler()
                    output_handler.print_to_console(data, file_format)
                    
            elif choice == "2":
                print("\nAvailable transformation formats:")
                transform_formats = ["csv", "json", "xml", "txt"]
                for i, fmt in enumerate(transform_formats, 1):
                    print(f"{i}. {fmt}")
                
                transform_choice = get_user_input(
                    f"Select target format (1-{len(transform_formats)}): ", 
                    options=[str(i) for i in range(1, len(transform_formats)+1)]
                )
                
                target_format = transform_formats[int(transform_choice)-1]
                
                transformer_factory = TransformerFactory()
                transformer = transformer_factory.get_transformer(file_format, target_format)
                transformed_data = transformer.transform(data)
                
                output_choice = get_user_input(
                    "\nDisplay output to (1) console or (2) file? Enter 1 or 2: ", 
                    options=["1", "2"]
                )
                
                if output_choice == "2":
                    output_path = get_user_input("Enter output file path: ")
                    output_handler = OutputHandler()
                    output_handler.write_to_file(transformed_data, output_path, target_format)
                    print(f"Successfully wrote transformed data to {output_path}")
                else:
                    output_handler = OutputHandler()
                    output_handler.print_to_console(transformed_data, target_format)
                
            elif choice == "3":
                is_valid, errors = file_parser.validate(data)
                if is_valid:
                    print("\n✅ Validation successful! File content is valid.")
                else:
                    print("\n❌ Validation failed!")
                    for error in errors:
                        print(f"- {error}")
                        
            elif choice == "4":
                query = get_user_input("\nEnter query expression (e.g., column=value): ")
                
                filtered_data = file_parser.filter(data, query)
                print(f"\nFiltered data - {len(filtered_data)} results found")
                
                output_choice = get_user_input(
                    "\nDisplay output to (1) console or (2) file? Enter 1 or 2: ", 
                    options=["1", "2"]
                )
                
                if output_choice == "2":
                    output_path = get_user_input("Enter output file path: ")
                    output_handler = OutputHandler()
                    output_handler.write_to_file(filtered_data, output_path, file_format)
                    print(f"Successfully wrote filtered data to {output_path}")
                else:
                    output_handler = OutputHandler()
                    output_handler.print_to_console(filtered_data, file_format)
            
            continue_choice = get_user_input("\nDo you want to perform another operation? (y/n): ", options=["y", "n"])
            if continue_choice.lower() != "y":
                print("\nExiting the File Parser Tool. Goodbye!")
                return
                
        except Exception as e:
            print(f"Error: {str(e)}")
            input("\nPress Enter to return to the main menu...")

def main():
    parser = argparse.ArgumentParser(
        description="Parse, transform, validate and query structured files",
        epilog="Use '-' as the filename to read from stdin."
    )
    parser.add_argument("file", nargs='?', help="Path to the file to parse (use '-' for stdin)")
    parser.add_argument("-f", "--format", help="Explicitly specify file format (csv, json, xml, txt, log)")
    parser.add_argument("-t", "--transform", help="Transform to format (csv, json, xml, txt)")
    parser.add_argument("-o", "--output", help="Output file path. If not specified, print to console")
    parser.add_argument("-v", "--validate", action="store_true", help="Validate file content")
    parser.add_argument("-q", "--query", help="Filter data with a query expression")
    parser.add_argument("--version", action="version", version=f"File Parser CLI Tool v{VERSION}")
    parser.add_argument("--examples", action="store_true", help="Show usage examples")
    parser.add_argument("-i", "--interactive", action="store_true", help="Start in interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
        return
        
    if args.examples:
        print_banner()
        print_usage_examples()
        return
    
    if not args.file:
        print("Error: No file specified. Use --interactive for interactive mode or provide a file path.")
        print("Run with --examples to see usage examples.")
        sys.exit(1)
    
    temp_file = None
    try:
        if args.file == '-':
            if not args.format:
                print("Error: When reading from stdin, you must specify the format with --format", file=sys.stderr)
                sys.exit(1)
                
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(sys.stdin.buffer.read())
            temp_file.close()
            input_file = temp_file.name
            file_format = args.format
        else:
            if not os.path.isfile(args.file):
                print(f"Error: File {args.file} not found", file=sys.stderr)
                sys.exit(1)
            
            input_file = args.file
            file_format = args.format
            if not file_format:
                file_format = os.path.splitext(args.file)[1][1:].lower()
                if file_format not in ["csv", "json", "xml", "txt", "log"]:
                    print(f"Error: Cannot determine file format from extension. Please specify with --format", file=sys.stderr)
                    sys.exit(1)
        
        try:
            parser_factory = ParserFactory()
            file_parser = parser_factory.get_parser(file_format)
            
            data = file_parser.parse(input_file)
            
            if args.validate:
                is_valid, errors = file_parser.validate(data)
                if not is_valid:
                    print("Validation failed:", file=sys.stderr)
                    for error in errors:
                        print(f"- {error}", file=sys.stderr)
                    sys.exit(1)
            
            if args.query:
                data = file_parser.filter(data, args.query)
            
            if args.transform:
                if args.transform not in ["csv", "json", "xml", "txt"]:
                    print(f"Error: Unsupported transformation format: {args.transform}", file=sys.stderr)
                    sys.exit(1)
                    
                transformer_factory = TransformerFactory()
                transformer = transformer_factory.get_transformer(file_format, args.transform)
                data = transformer.transform(data)
                output_format = args.transform
            else:
                output_format = file_format
            
            output_handler = OutputHandler()
            if args.output:
                output_handler.write_to_file(data, args.output, output_format)
                print(f"Successfully wrote output to {args.output}")
            else:
                output_handler.print_to_console(data, output_format)
                
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
    finally:
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

if __name__ == "__main__":
    if sys.stdout.isatty() and len(sys.argv) == 1:
        print_banner()
        print("\nNo arguments provided. Run with --help for usage information.")
        print("Use --interactive to start in interactive mode.")
    main()
