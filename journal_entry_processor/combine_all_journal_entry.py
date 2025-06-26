import pandas as pd
import os

def merge_excel_files(input_folder='journal_entry_processed_data/', output_file='Merge.xlsx'):
   

    # Ensure correct path format
    input_folder = input_folder.rstrip('/') + '/'
    print("nnnnnnn",input_folder)
    dfs = []
    
    folders = os.listdir(input_folder)
    
    # Read and append all Excel files
    for fl in folders:
        files = os.listdir(input_folder+fl)
        for file_name in files:
            if file_name.endswith('.xlsx'):
                full_path = os.path.join(input_folder,fl, file_name)
                print("path",full_path)
                df = pd.read_excel(full_path, engine="openpyxl")
                dfs.append(df)
            

    if not dfs:
        print("⚠️ No Excel files found or readable in the folder.")
        return

#     Concatenate dataframes
    concatenated_df = pd.concat(dfs, ignore_index=True)

    # Drop 'Unnamed: 0' if present
    if 'Unnamed: 0' in concatenated_df.columns:
        concatenated_df.drop(columns='Unnamed: 0', inplace=True)

    # Save to Excel
    output_file_path = os.path.join(input_folder,'Combine_data',output_file )
    concatenated_df.to_excel(output_file_path, index=False)
    print(f"✅ Merged Excel saved as '{output_file_path}'.")

