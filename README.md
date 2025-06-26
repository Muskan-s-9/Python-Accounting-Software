## 🧾 Accounting Software – End-to-End Workflow

```python
from invoice_processor.invoice_processor_main import process_invoices_with_rag_and_cache
from journal_entry_processor.Passing_Journal_Entry import PassingJournalEntry
from journal_entry_processor.combine_all_journal_entry import merge_excel_files
from generate_report.generate_balance_sheet import generate_balance_sheet
from generate_report.generate_detail_balance_sheets import generate_detail_balance_sheets
from generate_report.generate_ledger_pivot import generate_ledger_pivot
from generate_report.generate_pnl_report import generate_pnl_report

# Step 1: Extract structured accounting data from invoices using RAG + Caching
process_invoices_with_rag_and_cache()

# Step 2: Pass journal entries for core transaction types
def passing_journal_entry(entry_type: str) -> None:
    """Generates journal entries for a specific entry type."""
    PassingJournalEntry(entry_type).passing_entry()

for entry in ['sales', 'purchase', 'credit_note', 'debit_note']:
    passing_journal_entry(entry)

# Step 3: Merge all journal entries into a unified Excel file
merge_excel_files()

# Step 4: Generate comprehensive financial reports
generate_balance_sheet()
generate_detail_balance_sheets()
generate_ledger_pivot()
generate_pnl_report()
