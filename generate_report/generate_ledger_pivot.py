import pandas as pd
import os

def generate_ledger_pivot():
    excel_path = 'journal_entry_processed_data/Combine_data/'
    excel_file = 'Merge'
    fl_name = excel_file.split('_')[0]

    df_data = pd.read_excel(excel_path + excel_file + '.xlsx', engine='openpyxl')

    trial_balance = pd.pivot_table(df_data, index=['J4 - Ledger_Name', 'J2 - Date'], 
                                   values=['J6 - Dr Amount', 'J7 - Cr Amount'], 
                                   aggfunc='sum').fillna(0)

    trial_balance['Balance'] = trial_balance['J6 - Dr Amount'] - trial_balance['J7 - Cr Amount']

    file_path = "reporting_files/Ledgers/"
    trial_balance.to_excel(file_path + fl_name + 'ledger_pivot.xlsx')
