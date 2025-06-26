import pandas as pd
from typing import Dict, Any


class Accounting_Ledgers_Configuration:
    def __init__(self, config1: Dict[str, Any], config2: Dict[str, Any]) -> None:
        if not isinstance(config1, dict):
            raise TypeError("config1 must be a dictionary")
        if not isinstance(config2, dict):
            raise TypeError("config2 must be a dictionary")

        self.config: Dict[str, Any] = config1
        self.config2: Dict[str, Any] = config2

    def get_ledger_configs_dataframe(self,path) -> str:
        data = []

        # Process config1
        for account, details in self.config.get('accounts', {}).items():
            try:
                type_dict = details.get('type', {})
                c2_key = next(iter(type_dict))
                account_type = type_dict[c2_key]['type']
            except (KeyError, IndexError, TypeError, StopIteration):
                print(f"Skipping invalid config1 account: {account}")
                continue

            data.append({
                'C1': account_type,
                'C2': c2_key,
                'C3': account
            })

        df1 = pd.DataFrame(data)
        df1['C4'] = df1['C5'] = ''
        df1['G_CODE'] = df1['C1'].map({
            'ASSET': 'G1',
            'LIABILITY': 'G2',
            'EXPENSE': 'G4',
            'REVENUE': 'G5'
        })

        # Process config2
        data2 = []
        for account, details in self.config2.get('accounts', {}).items():
            try:
                c1_val = next(iter(details.values()))
            except (KeyError, StopIteration, TypeError):
                print(f"Skipping invalid config2 account: {account}")
                continue

            data2.append({
                'C1': c1_val,
                'C2': account
            })

        df2 = pd.DataFrame(data2)
        df2['C3'] = df1['C2'].iloc[0] if not df1.empty else ''
        df2['C4'] = df2['C5'] = ''
        df2['G_CODE'] = df2['C1'].map({'Capital': 'G3'})

        # Combine the dataframes
        main_df = pd.concat([df1, df2], ignore_index=True)

        # Save to Excel
                 
        print(f"Saving Excel to: {path}Ledger_Library.xlsx")
        main_df.to_excel(path+"Ledger_Library.xlsx", index=False)
