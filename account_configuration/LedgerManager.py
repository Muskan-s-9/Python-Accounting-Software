import pandas as pd
import os


class LedgerManager:
    def __init__(self):
        self.file_path = 'Account_Configuration/Ledger_config_data/Ledger_Library.xlsx'
        self.main_df = pd.read_excel(self.file_path, engine='openpyxl')  # ← read from Excel
        self.main_df['C5'] = self.main_df['C5'].astype(str).str.lower()
        self.main_df['C3'] = self.main_df['C3'].astype(str).str.lower()

    def retrieve_ledger(self, c5: str, flag = False):
        """Retrieve ledger information if C5 exists."""
        c5 = c5.lower()
        match = self.main_df.loc[self.main_df['C5'] == c5]

        if not match.empty:
            if not flag:
                print(f" Ledger name '{c5}' already present.")
                
            row = match.iloc[0]
            return row['C1'], row['C2'], row['C3']
        
        print(f"Ledger name '{c5}' not found.")
        return self.enter_ledger(c5)

    def enter_ledger(self, c5: str):
        """Enter a new ledger or update existing C3 with new C5 if vacant."""
        c5 = c5.lower()
        c3 = input("Enter C3 (Account Name): ").strip()
        c4 = input("Enter C4 (Sub ledger, or 'none'): ").strip()
        if c4.lower() == 'none':
            c4 = c3

        matches = self.main_df[self.main_df['C3'] == c3]

        if matches.empty:
            print(f"No existing entry for account name '{c3}'.")
#             print(f" enter correct ledger name'{c3}'  or type q for exist")
            self.enter_ledger(c5)
            return self.retrieve_ledger(c5,flag = True)

        if (matches['C5'] == '').any():
            # Update existing row with empty C5
            self.main_df.loc[self.main_df['C3'] == c3, ['C4', 'C5']] = [c4, c5]
            print(f"Updated C3 '{c3}' with new C5 '{c5}'.")
        else:
            # Append new row
            row = matches.iloc[0]
            new_entry = {
                'C1': row['C1'],
                'C2': row['C2'],
                'C3': c3,
                'C4': c4,
                'C5': c5,
                'G_CODE': row.get('G_CODE', '')
            }
            self.main_df = pd.concat([self.main_df, pd.DataFrame([new_entry])], ignore_index=True)
            print(f"Appended new ledger entry with C3 '{c3}' and C5 '{c5}'.")

        # Save the updated DataFrame
        self.main_df.to_excel(self.file_path, index=False)
        print("Ledger data saved.")
        return self.retrieve_ledger(c5)
