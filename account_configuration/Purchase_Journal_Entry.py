class BasePurchaseEntry:
    def __init__(self, entry, journal_number, invoice_number, date, ledger_manager, asset_expense, liability_capital, output_dict):
        self.entry = entry
        self.journal_number = journal_number
        self.invoice_number = invoice_number
        self.date = date
        self.ledger = ledger_manager
        self.asset_expense = asset_expense
        self.liability_capital = liability_capital
        self.k = output_dict

    def get_dr_cr(self, amount, ledger_type):
        if ledger_type in ['ASSET', 'EXPENSE']:
            return self.asset_expense.debit_transaction(amount), 0
        return self.liability_capital.debit_transaction(amount), 0

    def get_cr_dr(self, amount, ledger_type):
        if ledger_type in ['ASSET', 'EXPENSE']:
            return 0, self.asset_expense.credit_transaction(amount)
        return 0, self.liability_capital.credit_transaction(amount)

    def append_entry(self, ledger_name, dr, cr):
        self.k['J9 - Description/Narration'].append('purchase')
        self.k['J3 - Invoice_Ref_Number'].append(self.invoice_number)
        self.k['J4 - Ledger_Name'].append(ledger_name)
        self.k['J2 - Date'].append(self.date)
        self.k['J1 - Journal Number'].append(self.journal_number)
        self.k['J6 - Dr Amount'].append(dr)
        self.k['J7 - Cr Amount'].append(cr)

    def process(self):
        raise NotImplementedError

        
        
class ToEntry(BasePurchaseEntry):
    def process(self):
        ledger_name = self.entry['Description']
        ledger_type, *_ = self.ledger.retrieve_ledger(ledger_name.lower())
        dr, cr = self.get_dr_cr(self.entry['Amount'], ledger_type)
        self.append_entry(ledger_name, dr, cr)


class IGSTEntry(BasePurchaseEntry):
    def process(self):
        ledger_name = f'tax igst {self.entry["Tax"]}%'
        ledger_type, *_ = self.ledger.retrieve_ledger(ledger_name.lower())
        dr, cr = self.get_dr_cr(self.entry['IGST'], ledger_type)
        self.append_entry(ledger_name, dr, cr)


class CGSTEntry(BasePurchaseEntry):
    def process(self):
        ledger_name = f'tax cgst {self.entry["Tax"]}%'
        ledger_type, *_ = self.ledger.retrieve_ledger(ledger_name.lower())
        dr, cr = self.get_dr_cr(self.entry['SGST'], ledger_type)
        self.append_entry(ledger_name, dr, cr)


class PurchaseCreditEntry(BasePurchaseEntry):
    def process(self):
        ledger_name = self.entry['Sold By']
        ledger_type, *_ = self.ledger.retrieve_ledger(ledger_name.lower())
        dr, cr = self.get_cr_dr(self.entry['Total'], ledger_type)
        self.append_entry(ledger_name, dr, cr)


class BankEntry(BasePurchaseEntry):
    def process(self):
        ledger_name = "To Bank"
        ledger_type, *_ = self.ledger.retrieve_ledger(ledger_name.lower())
        dr, cr = self.get_cr_dr(self.entry['Total'], ledger_type)
        self.append_entry(ledger_name, dr, cr)

        
        
 from journal_entries.purchase_entries import (
    ToEntry, IGSTEntry, CGSTEntry,
    PurchaseCreditEntry, BankEntry
)

class main_df:
    def __init__(self, df, main_df):
        self.df = df
        self.main_df = main_df
        self.asset_expense = Asset_Expense_Rule()
        self.liability_capital = Liability_Capital_Revenue_Rule()
        self.ledger = LedgerManager()

    def process_entries(self):
        for i in range(len(self.df)):
            print(f"Entry Number - {i}")
            entry = self.df.iloc[i]
            journal_number = f'P00{i+1}'
            invoice_number = entry['Invoice Number']
            date = entry['Invoice Date']

            components = [
                ToEntry,
                IGSTEntry,
                CGSTEntry,
                PurchaseCreditEntry,
                BankEntry,
            ]

            for comp in components:
                comp(entry, journal_number, invoice_number, date,
                     self.ledger, self.asset_expense, self.liability_capital, k).process()

            print("=" * 75 + "\n")

            
            
           