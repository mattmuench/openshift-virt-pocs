import re
import sys
import os

def resolve_includes(content, base_dir):
    # Regex to find the include directive: !!!include(filename)!!!
    pattern = re.compile(r'!!!include\((.*?)\)!!!')

    def replace_match(match):
        filename = match.group(1).strip()
        filepath = os.path.join(base_dir, filename)
        
        try:
            with open(filepath, 'r') as f:
                # Recursively resolve includes in the included file (if any)
                included_content = resolve_includes(f.read(), os.path.dirname(filepath))
                return included_content
        except FileNotFoundError:
            print(f"Error: Included file not found: {filepath}", file=sys.stderr)
            return f"**ERROR: File '{filename}' not found.**"
        except Exception as e:
            print(f"Error reading file {filepath}: {e}", file=sys.stderr)
            return f"**ERROR reading file '{filename}'.**"

    return pattern.sub(replace_match, content)

def main():
    if len(sys.argv) != 3:
        print("Usage: python preprocess.py <source_file> <output_file>", file=sys.stderr)
        sys.exit(1)

    source_file = sys.argv[1]
    output_file = "README.md"
    
    try:
        with open(source_file, 'r') as f:
            source_content = f.read()
        
        # Resolve includes starting from the directory of the source file
        processed_content = resolve_includes(source_content, os.path.dirname(source_file) or '.')
        
        with open(output_file, 'w') as f:
            f.write(processed_content)
        
        print(f"Successfully generated {output_file} from {source_file}")
        
    except FileNotFoundError:
        print(f"Error: Source file not found: {source_file}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()