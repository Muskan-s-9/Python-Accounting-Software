# JournalEntryBook
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

    
    
class SalesReturnEntry(BaseJournalEntry):
    def process(self):
        ledger_name = 'Sales Return'
        category, _, _ = self.ledger.retrieve_ledger(ledger_name.lower())
        dr = self.sys_a.debit_transaction(self.entry['Total']) if category in ['ASSET', 'EXPENSE'] else self.sys_b.debit_transaction(self.entry['Total'])
        self.append_entry(ledger_name, dr, 0)
        
        
class IGSTTaxEntry(BaseJournalEntry):
    def process(self):
        rate = str(self.entry['Tax'])
        ledger_name = f'tax igst {rate}%'
        category, _, _ = self.ledger.retrieve_ledger(ledger_name.lower())
        cr = self.sys_a.credit_transaction(self.entry['Tax IGST']) if category in ['ASSET', 'EXPENSE'] else self.sys_b.credit_transaction(self.entry['Tax IGST'])
        self.append_entry(ledger_name, 0, -cr)



class CGSTTaxEntry(BaseJournalEntry):
    def process(self):
        rate = str(self.entry['Tax'])
        ledger_name = f'tax cgst {rate}%'
        category, _, _ = self.ledger.retrieve_ledger(ledger_name.lower())
        cr = self.sys_a.credit_transaction(self.entry['Tax CGST']) * -1
        self.append_entry(ledger_name, 0, cr)


class ToLedgerEntry(BaseJournalEntry):
    def process(self):
        ledger_name = self.entry['To']
        category, _, _ = self.ledger.retrieve_ledger(ledger_name.lower())
        cr = (self.sys_a if category in ['ASSET', 'EXPENSE'] else self.sys_b).credit_transaction(self.entry['Amount']) * -1
        self.append_entry(ledger_name, 0, cr)



class BankReceiptEntry(BaseJournalEntry):
    def process(self):
        ledger_name = 'Axis Bank A/c'
        category, _, _ = self.ledger.retrieve_ledger(ledger_name.lower())
        dr = (self.sys_a if category in ['ASSET', 'EXPENSE'] else self.sys_b).debit_transaction(self.entry['Total'])
        self.append_entry(ledger_name, dr, 0)



class SalesReversalEntry(BaseJournalEntry):
    def process(self):
        ledger_name = self.entry['To']
        category, _, _ = self.ledger.retrieve_ledger(ledger_name.lower())
        cr = (self.sys_a if category in ['ASSET', 'EXPENSE'] else self.sys_b).debit_transaction(self.entry['Total']) * -1
        self.append_entry(ledger_name, 0, cr)

        
from account_configuration.LedgerManager import LedgerManager
from journal_entry_processor.Debit_Credit_Rules import AssetExpenseRule, LiabilityCapitalRevenueRule

class CreditNoteJournalEntryProcessor:
    def __init__(self, entry_df):
        self.df = entry_df
        self.sys_a = AssetExpenseRule()
        self.sys_b = LiabilityCapitalRevenueRule()
        self.ledger = LedgerManager()
        self.journal_book = JournalEntryBook()

    def process_entries(self):
        for i in range(len(self.df)):
            entry = self.df.iloc[i]
            base_journal = f'S00{i+1}'
            extended_journal = f'S00{i+1}B'

            try:
                SalesReturnEntry(entry, base_journal, self.journal_book, self.ledger, self.sys_a, self.sys_b).process()
                IGSTTaxEntry(entry, base_journal, self.journal_book, self.ledger, self.sys_a, self.sys_b).process()
                CGSTTaxEntry(entry, base_journal, self.journal_book, self.ledger, self.sys_a, self.sys_b).process()
                ToLedgerEntry(entry, base_journal, self.journal_book, self.ledger, self.sys_a, self.sys_b).process()
                BankReceiptEntry(entry, extended_journal, self.journal_book, self.ledger, self.sys_a, self.sys_b).process()
                SalesReversalEntry(entry, extended_journal, self.journal_book, self.ledger, self.sys_a, self.sys_b).process()
            except Exception as e:
                print(f"[ERROR at row {i+1}]: {e}")

    def get_journal_entries(self):
        return self.journal_book.get_entries()
