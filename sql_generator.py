import sys
import os
import re
from typing import List, Dict, Tuple

def is_greek_string(text: str) -> bool:
    """Check if string contains Greek characters."""
    # Greek Unicode ranges
    greek_pattern = re.compile('[\u0370-\u03FF\u1F00-\u1FFF]')
    return bool(greek_pattern.search(text))

def parse_header(header_line: str) -> List[str]:
    """Parse the header line to get column names."""
    return [col.strip() for col in header_line.split('\t') if col.strip()]

def parse_data_line(line: str, columns: List[str]) -> Dict[str, str]:
    """Parse a data line into a dictionary of column name to value."""
    values = [val.strip() for val in line.split('\t')]
    # Pad the values list with NULL if it's shorter than columns
    values.extend(['NULL'] * (len(columns) - len(values)))
    return dict(zip(columns, values))

def parse_select_statement(select_line: str) -> Tuple[str, List[str], bool]:
    """Parse the SELECT statement to get table name and selected columns."""
    select_line = select_line.strip()
    # Remove WITH (NOLOCK) if present
    select_line = re.sub(r'\s+with\s*\(nolock\)', '', select_line, flags=re.IGNORECASE)
    
    is_select_all = False
    selected_columns = []
    
    # Extract columns
    if select_line.lower().startswith('select *'):
        is_select_all = True
    else:
        # Extract columns between SELECT and FROM
        columns_part = select_line[6:select_line.lower().find('from')].strip()
        selected_columns = [col.strip() for col in columns_part.split(',')]
    
    # Extract table name
    from_parts = select_line.lower().split('from')
    if len(from_parts) < 2:
        raise ValueError("Cannot find table name in SELECT statement")
    
    # Handle schema.table format and remove WITH (NOLOCK)
    full_table_name = from_parts[1].split('where')[0].strip()
    
    return full_table_name, selected_columns, is_select_all

def format_value(val: str) -> str:
    """Format a value for SQL, handling NULL and Greek strings."""
    if val == 'NULL':
        return 'NULL'
    elif is_greek_string(val):
        return f"N'{val}'"
    else:
        return f"'{val}'"

def generate_insert_statement(table_name: str, row_data: Dict[str, str], all_headers: List[str], 
                            selected_columns: List[str], is_select_all: bool) -> str:
    """Generate an INSERT statement for a single row of data."""
    if is_select_all:
        # Use all columns
        columns = all_headers
        values = [row_data.get(header, 'NULL') for header in all_headers]
        value_str = ', '.join(format_value(val) for val in values)
        return f"INSERT INTO {table_name} VALUES ({value_str});"
    else:
        # Use only selected columns
        columns_str = ', '.join(f"[{col}]" for col in selected_columns)
        values = [row_data.get(col, 'NULL') for col in selected_columns]
        value_str = ', '.join(format_value(val) for val in values)
        return f"INSERT INTO {table_name} ({columns_str}) VALUES ({value_str});"

def process_file(file_path: str) -> str:
    """Process the file and return the complete SQL content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read all lines, preserving empty lines
            all_lines = [line.rstrip('\n') for line in file.readlines()]
            
        # Parse SELECT statement
        select_line = all_lines[0].strip()
        if not select_line.lower().startswith('select'):
            raise ValueError("No SELECT statement found in the file")
            
        # Get table name and selected columns
        full_table_name, selected_columns, is_select_all = parse_select_statement(select_line)
        
        # Find headers line (the line containing "ID")
        header_line = None
        data_start = 0
        for i, line in enumerate(all_lines):
            if line.strip().startswith('ID\t'):
                header_line = line
                data_start = i + 1
                break
        
        if not header_line:
            header_line = all_lines[2]  # Fallback to third line
            data_start = 3
        
        # Parse headers
        all_headers = parse_header(header_line)
        
        # Lists to store statements
        output_lines = []
        output_lines.append("-- Insert statements")
        
        # Process data lines
        delete_statements = []
        data_lines = [line for line in all_lines[data_start:] if line.strip()]
        
        for line in data_lines:
            row_data = parse_data_line(line, all_headers)
            if row_data:
                # Add INSERT statement
                output_lines.append(generate_insert_statement(full_table_name, row_data, 
                                                           all_headers, selected_columns, is_select_all))
                
                # Add DELETE statement if ID exists
                if row_data.get('ID') and row_data['ID'] != 'NULL':
                    delete_statements.append(f"DELETE FROM {full_table_name} WHERE [ID] = '{row_data['ID']}';")

        # Add DELETE statements section if we have any
        if delete_statements:
            output_lines.append("")  # Add blank line between sections
            output_lines.append("-- Delete statements (in reverse order for safety)")
            output_lines.extend(reversed(delete_statements))

        # Add final newline
        output_lines.append("")
        
        # Join all lines with newlines
        return "\n".join(output_lines)
        
    except Exception as e:
        raise RuntimeError(f"Error processing file: {str(e)}")

def main():
    if len(sys.argv) != 2:
        print("Please drag and drop a text file onto this script.")
        return
        
    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        return
    
    try:
        output_file = os.path.splitext(input_file)[0] + '_output.sql'
        sql_content = process_file(input_file)
        
        with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
            f.write(sql_content)
            
        print(f"SQL statements have been generated and saved to: {output_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()