import os

def parse_tmdl(file_path):
    """Parse a .tmdl file to extract table and column schema."""
    schema = {}
    current_table = None

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()  # Remove leading/trailing whitespace

                # Detect table name
                if line.startswith("table "):
                    current_table = line.split(" ", 1)[1]  # Extract table name (handles spaces)
                    schema[current_table] = []

                # Detect column name
                elif current_table and line.startswith("column "):
                    column_name = line.split(" ", 1)[1]  # Extract column name (handles spaces)
                    schema[current_table].append(column_name)

        return schema

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return {}

def load_all_tmdls(folder_path):
    """Load and combine schemas from all .tmdl files in a folder."""
    combined_schema = {}

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".tmdl"):
            file_path = os.path.join(folder_path, file_name)
            schema = parse_tmdl(file_path)
            combined_schema.update(schema)

    return combined_schema

if __name__ == "__main__":
    # Specify the folder where your .tmdl files are stored
    folder_path = os.path.dirname(os.path.abspath(__file__))  # Current directory

    # Extract schema from all .tmdl files in the folder
    schema = load_all_tmdls(folder_path)

