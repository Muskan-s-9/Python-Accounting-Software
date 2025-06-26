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


# Base and Derived Entry Classes
class BaseJournalEntry:
    def __init__(self, entry, journal_number, journal_book, ledger_manager, sys_a, sys_b):
        self.entry = entry
        self.journal_number = journal_number
        self.journal_book = journal_book
        self.ledger = ledger_manager
        self.sys_a = sys_a
        self.sys_b = sys_b
        self.date = entry['Invoice Date']
        self.invoice_number = entry['Invoice Number']

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


class SoldByDebitEntry(BaseJournalEntry):
    def process(self):
        ledger_name = self.entry['Sold By']
        c1, *_ = self.ledger.retrieve_ledger(ledger_name.lower())
        amount = self.entry['Amount']
        dr = self.sys_a.debit_transaction(amount) if c1 in ['ASSET', 'EXPENSE'] else self.sys_b.debit_transaction(amount)
        self.append_entry(ledger_name, dr, 0)
        
        
class IGSTDebitEntry(BaseJournalEntry):
    def process(self):
        ledger_name = f'tax igst {self.entry["Tax"]}%'
        c1, *_ = self.ledger.retrieve_ledger(ledger_name.lower())
        amount = self.entry['IGST']
        dr = self.sys_a.debit_transaction(amount) if c1 in ['ASSET', 'EXPENSE'] else self.sys_b.debit_transaction(amount)
        self.append_entry(ledger_name, dr, 0)

        
        
class CGSTDebitEntry(BaseJournalEntry):
    def process(self):
        ledger_name = f'tax cgst {self.entry["Tax"]}%'
        c1, *_ = self.ledger.retrieve_ledger(ledger_name.lower())
        amount = self.entry['SGST']
        dr = self.sys_a.debit_transaction(amount) if c1 in ['ASSET', 'EXPENSE'] else self.sys_b.debit_transaction(amount)
        self.append_entry(ledger_name, dr, 0)

        
        
class PurchaseReturnCreditEntry(BaseJournalEntry):
    def process(self):
        ledger_name = 'Purchase Return'
        c1, *_ = self.ledger.retrieve_ledger(ledger_name.lower())
        amount = self.entry['Total']
        cr = self.sys_a.credit_transaction(amount) if c1 in ['ASSET', 'EXPENSE'] else self.sys_b.credit_transaction(amount)
        self.append_entry(ledger_name, 0, cr)

        
        
class BankDebitEntry(BaseJournalEntry):
    def process(self):
        ledger_name = 'Bank A/c'
        c1, *_ = self.ledger.retrieve_ledger(ledger_name.lower())
        amount = self.entry['Total']
        dr = self.sys_a.debit_transaction(amount) if c1 in ['ASSET', 'EXPENSE'] else self.sys_b.debit_transaction(amount)
        self.append_entry(ledger_name, dr, 0)

        
class SoldByCrEntryAsItem(BaseJournalEntry):
    def process(self):
        ledger_name = self.entry['Sold By']
        c1, *_ = self.ledger.retrieve_ledger(ledger_name.lower())
        amount = self.entry['Total']
        cr = self.sys_a.debit_transaction(amount) if c1 in ['ASSET', 'EXPENSE'] else self.sys_b.debit_transaction(amount)
        self.append_entry(ledger_name, 0, cr)


from account_configuration.LedgerManager import LedgerManager
from journal_entry_processor.Debit_Credit_Rules import LiabilityCapitalRevenueRule ,AssetExpenseRule


class DebitNoteJournalEntryProcessor:
    def __init__(self, entery_df):
        self.df = entery_df
        self.sys_a = AssetExpenseRule()
        self.sys_b = LiabilityCapitalRevenueRule()
        self.ledger = LedgerManager()
        self.journal_book = JournalEntryBook()

    def process_entries(self):
        for i in range(len(self.df)):
            entry = self.df.iloc[i]
            journal_number = f'D00{i+1}'
            print(f"Entry Number - {i}")

            components = [
                SoldByDebitEntry,
                IGSTDebitEntry,
                CGSTDebitEntry,
                PurchaseReturnCreditEntry,
                BankDebitEntry,
                SoldByCrEntryAsItem
            ]

            for comp in components:
                comp(entry, journal_number, self.journal_book, self.ledger, self.sys_a, self.sys_b).process()

            print("==========================================================================\n")

    def get_journal_entries(self):
        return self.journal_book.get_entries()
