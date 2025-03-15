import os
import sys

# Set path to the ADOMD.NET DLL
dll_path = r"C:\Program Files\Microsoft.NET\ADOMD.NET\160"
if os.path.exists(dll_path):
    sys.path.append(dll_path)
    print(f"✅ ADOMD.NET DLL path added: {dll_path}")
else:
    print(f"❌ ADOMD.NET DLL not found at: {dll_path}. Please ensure it is installed.")
    exit(1)

from pyadomd import Pyadomd
import pandas as pd

# XMLA connection string for Power BI service
CONNECTION_STRING = (
    "Provider=MSOLAP;"
    "Data Source=powerbi://api.powerbi.com/v1.0/myorg/Dev;"
    "Initial Catalog=MyTestFile;"
)

def execute_dax_query(dax_query):
    try:
        print("🔄 Connecting to XMLA endpoint...")
        with Pyadomd(CONNECTION_STRING) as conn:
            print("✅ Connection established.")
            with conn.cursor() as cur:
                print(f"Executing DAX query: {dax_query}")
                cur.execute(dax_query)
                rows = cur.fetchall()
                if not rows:
                    print("⚠️ No rows returned.")
                    return None
                columns = [col[0] for col in cur.description]
                return pd.DataFrame(rows, columns=columns)
    except Exception as e:
        print(f"❌ Error executing query: {repr(e)}")
        return None

# Test DAX execution with a sample query
if __name__ == "__main__":
    test_query = "EVALUATE ROW('TestColumn', 1)"
    results = execute_dax_query(test_query)
    if results is not None:
        print("Query Results:")
        print(results)
    else:
        print("❌ Query failed.")
