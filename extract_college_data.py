import pandas as pd
import json
import os

def extract_data():
    file_path = '/home/shafeeq_h/College_Management_System/college_data.xlsx'
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    try:
        # Load all sheets
        xls = pd.ExcelFile(file_path)
        all_data = {}
        
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            # Convert NaN to None for JSON compatibility
            df = df.where(pd.notnull(df), None)
            all_data[sheet_name] = df.to_dict(orient='records')
            
        output_path = 'college_data.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=4, ensure_ascii=False)
            
        print(f"Data successfully extracted to {output_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_data()
