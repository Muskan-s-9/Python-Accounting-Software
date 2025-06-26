class JournalEntryBook:
    def __init__(self):
        self.entries = {
            'J1 - Journal Number': [],
            'J2 - Date': [],
            'J3 - Invoice_Ref_Number': [],
            'J4 - Ledger_Name': [],
            'J6 - Dr Amount': [],
            'J7 - Cr Amount': [],
            'J9 - Description/Narration': [],
        }

    def add_entry(self, journal_number, date, invoice_number, ledger_name, dr, cr, narration):
        self.entries['J1 - Journal Number'].append(journal_number)
        self.entries['J2 - Date'].append(date)
        self.entries['J3 - Invoice_Ref_Number'].append(invoice_number)
        self.entries['J4 - Ledger_Name'].append(ledger_name)
        self.entries['J6 - Dr Amount'].append(dr)
        self.entries['J7 - Cr Amount'].append(cr)
        self.entries['J9 - Description/Narration'].append(narration)

    def get_entries(self):
        return self.entries


class BasePurchaseEntry:
    def __init__(self, entry, journal_number, invoice_number, date,
                 ledger_manager, asset_expense, liability_capital, journal_book):
        self.entry = entry
        self.journal_number = journal_number
        self.invoice_number = invoice_number
        self.date = date
        self.ledger = ledger_manager
        self.asset_expense = asset_expense
        self.liability_capital = liability_capital
        self.journal_book = journal_book

    def get_dr_cr(self, amount, ledger_type):
        if ledger_type in ['ASSET', 'EXPENSE']:
            return self.asset_expense.debit_transaction(amount), 0
        return self.liability_capital.debit_transaction(amount), 0

    def get_cr_dr(self, amount, ledger_type):
        if ledger_type in ['ASSET', 'EXPENSE']:
            return 0, self.asset_expense.credit_transaction(amount)
        return 0, self.liability_capital.credit_transaction(amount)

    def append_entry(self, ledger_name, dr, cr):
        self.journal_book.add_entry(
            journal_number=self.journal_number,
            date=self.date,
            invoice_number=self.invoice_number,
            ledger_name=ledger_name,
            dr=dr,
            cr=cr,
            narration='Purchase'
        )

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
 


from account_configuration.LedgerManager import LedgerManager
from journal_entry_processor.Debit_Credit_Rules import AssetExpenseRule, LiabilityCapitalRevenueRule

class PurchaseJournalEntryProcessor:
    def __init__(self,entry_df):
        self.df = entry_df
        self.asset_expense = AssetExpenseRule()
        self.liability_capital = LiabilityCapitalRevenueRule()
        self.ledger = LedgerManager()
        self.journal_book = JournalEntryBook()

    def process_entries(self):
        for i, entry in self.df.iterrows():
            print(f"Entry Number - {i}")
            journal_number = f'P00{i+1}'
            invoice_number = entry['Invoice Number']
            date = entry['Invoice Date']

            components = [ToEntry, IGSTEntry, CGSTEntry, PurchaseCreditEntry, BankEntry]

            for comp in components:
                comp(entry, journal_number, invoice_number, date,
                     self.ledger, self.asset_expense, self.liability_capital,
                     self.journal_book).process()

            print("=" * 75 + "\n")

    def get_journal_entries(self):
        return self.journal_book.get_entries()
