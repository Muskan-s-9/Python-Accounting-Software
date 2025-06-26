import pandas as pd


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

    def get_journal_entries(self):
        return self.entries

from account_configuration.LedgerManager import LedgerManager
from journal_entry_processor.Debit_Credit_Rules import AssetExpenseRule, LiabilityCapitalRevenueRule

class SalesJournalEntryProcessor:
    def __init__(self, df):
        self.df = df
        self.ledger = LedgerManager()
        self.sys_a = AssetExpenseRule()
        self.sys_b = LiabilityCapitalRevenueRule()
        self.journal_book = JournalEntryBook()

    def add_journal_entry(self, ledger_name, amount, is_debit, narration, date, invoice_number, journal_number):
        ledger_class, *_ = self.ledger.retrieve_ledger(ledger_name.strip().lower())
        rule_engine = self.sys_a if ledger_class in ['ASSET', 'EXPENSE'] else self.sys_b

        if is_debit:
            dr = rule_engine.debit_transaction(amount)
            cr = 0
        else:
            cr = rule_engine.credit_transaction(amount)
            dr = 0

        self.journal_book.add_entry(
            journal_number=journal_number,
            date=date,
            invoice_number=invoice_number,
            ledger_name=ledger_name,
            dr=dr,
            cr=cr,
            narration=narration
        )

    def process_entries(self):
        for i in range(len(self.df)):
            en = self.df.iloc[i]
            tx = en['Tax']
            date = en['Invoice Date']
            invoice_number = en['Invoice Number']
            journal_number = f"S{str(i).zfill(3)}"

            self.add_journal_entry(en['To'], en['Total'], True, 'Sales', date, invoice_number, journal_number)
            self.add_journal_entry(f'tax igst {tx}%', en['Tax IGST'], False, 'Sales', date, invoice_number, journal_number)
            self.add_journal_entry(f'tax cgst {tx}%', en['Tax CGST'], False, 'Sales', date, invoice_number, journal_number)

            if 'Tax SGST' in en and pd.notna(en['Tax SGST']):
                self.add_journal_entry(f'tax sgst {tx}%', en['Tax SGST'], False, 'Sales', date, invoice_number, journal_number)

            self.add_journal_entry('To Sales', en['Amount'], False, 'Sales', date, invoice_number, journal_number)

            print(f"Processed entry {i + 1}")
            print("=" * 75)

    def get_journal_entries(self):
        return self.journal_book.get_journal_entries()
