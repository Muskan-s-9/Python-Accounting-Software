from invoice_processor.invoice_processor_main import process_invoices_with_rag_and_cache

from journal_entry_processor.Passing_Journal_Entry import PassingJournalEntry
from journal_entry_processor.combine_all_journal_entry import merge_excel_files
from generate_report.generate_balance_sheet import generate_balance_sheet
from generate_report.generate_detail_balance_sheets import generate_detail_balance_sheets
from generate_report.generate_ledger_pivot import generate_ledger_pivot
from generate_report.generate_pnl_report import generate_pnl_report


process_invoices_with_rag_and_cache()

# def passing_journal_entry(entry_type):
#     PassingJournalEntry(entry_type).passing_entry()

# Main guard block
#if __name__ == "__main__":


# passing_journal_entry('sales')
# passing_journal_entry('purchase')
# passing_journal_entry('credit_note')
# passing_journal_entry('debit_note')

# merge_excel_files()
# generate_balance_sheet()
# generate_detail_balance_sheets()
# generate_ledger_pivot()
# generate_pnl_report()
