# SQL Statement Generator

A Python utility that converts tab-separated data into SQL INSERT and DELETE statements. This tool is particularly useful for generating SQL scripts from query results or spreadsheet data.

## Features

- Converts tab-separated data to SQL INSERT statements
- Automatically generates corresponding DELETE statements
- Parses SELECT statements to determine table structure
- Supports full table inserts or specific column selection
- Handles Unicode text including special characters
- Proper SQL value formatting (NULL values, string quotes)
- Simple drag-and-drop interface
- Preserves schema and table names from input

## Requirements

- Python 3.x
- Windows OS (for drag-and-drop functionality)

## Usage

### Simple Method (Recommended)
1. Prepare your input file with:
   - SELECT statement on the first line
   - Column headers (tab-separated)
   - Data rows (tab-separated)
2. Drag and drop your input file onto `sql_generator.bat`
3. The tool will generate an output file named `[input_name]_output.sql`

### Input File Format

```
SELECT * FROM schema.table WHERE condition
[blank line]
Column1    Column2    Column3    ...
value1     value2     value3     ...
value1     value2     value3     ...
```

Example:
```
select * from HR.dbo.Employees
[blank line]
ID    FirstName    LastName    Department
1     John         Doe         IT
2     Jane         Smith       HR
```

### Output Format

The generated SQL file will contain:
```sql
-- Insert statements
INSERT INTO HR.dbo.Employees VALUES ('1', 'John', 'Doe', 'IT');
INSERT INTO HR.dbo.Employees VALUES ('2', 'Jane', 'Smith', 'HR');

-- Delete statements (in reverse order for safety)
DELETE FROM HR.dbo.Employees WHERE [ID] = '2';
DELETE FROM HR.dbo.Employees WHERE [ID] = '1';
```

## Advanced Features

### Column Selection
You can specify which columns to include in the SELECT statement:
```sql
SELECT FirstName, LastName FROM HR.dbo.Employees
```
The tool will generate INSERT statements using only the specified columns.

### Schema Support
- Fully supports schema-qualified table names (e.g., `schema.table` or `database.schema.table`)
- Preserves the full table path in generated statements
- Automatically removes WITH (NOLOCK) hints from input SELECT statements

### SQL Hint Handling
- WITH (NOLOCK) hints in the input SELECT statement are automatically removed
- This ensures clean INSERT statements without unnecessary table hints
- Original query structure is preserved for all other parts

### NULL Handling
- NULL values in the input are properly handled in SQL statements
- Empty cells are treated as NULL values

### Value Formatting
- Automatically adds N' prefix for Unicode text when needed
- Properly escapes special characters in strings
- Maintains data type integrity in generated SQL

## Notes

- The input file must be tab-separated
- First line must contain a valid SELECT statement
- Column headers must include 'ID' field for DELETE statement generation
- Output statements are ordered with INSERTs first, then DELETEs (in reverse order)
- Unicode text is automatically detected and properly formatted