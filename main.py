from invoice_processor.invoice_processor_main import process_invoices_with_rag_and_cache

from journal_entry_processor.Passing_Journal_Entry import PassingJournalEntry
from journal_entry_processor.combine_all_journal_entry import merge_excel_files
from generate_report.generate_balance_sheet import generate_balance_sheet
from generate_report.generate_detail_balance_sheets import generate_detail_balance_sheets
from generate_report.generate_ledger_pivot import generate_ledger_pivot
from generate_report.generate_pnl_report import generate_pnl_report

#scrap the accounting data from the invoices
process_invoices_with_rag_and_cache()

#passing sales,purchase,credit_note,debit_note journal entry
def passing_journal_entry(entry_type):
    PassingJournalEntry(entry_type).passing_entry()

passing_journal_entry('sales')
passing_journal_entry('purchase')
passing_journal_entry('credit_note')
passing_journal_entry('debit_note')

#generate balance sheet
merge_excel_files()
generate_balance_sheet()
generate_detail_balance_sheets()
generate_ledger_pivot()
generate_pnl_report()
