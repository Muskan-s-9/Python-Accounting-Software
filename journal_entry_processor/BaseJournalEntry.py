class BaseJournalEntry:
    def __init__(self, entry, journal_number, k, ledger_manager, sys_a, sys_b):
        self.entry = entry
        self.journal_number = journal_number
        self.k = k
        self.ledger = ledger_manager
        self.sys_a = sys_a
        self.sys_b = sys_b
        self.date = entry['Invoice Date']
        self.invoice = entry['Invoice Number']

    def append_entry(self, ledger_name, dr, cr, narration="Credit Notes"):
        self.k['J1 - Journal Number'].append(self.journal_number)
        self.k['J2 - Date'].append(self.date)
        self.k['J3 - Invoice_Ref_Number'].append(self.invoice)
        self.k['J4 - Ledger_Name'].append(ledger_name)
        self.k['J6 - Dr Amount'].append(dr)
        self.k['J7 - Cr Amount'].append(cr)
        self.k['J9 - Description/Narration'].append(narration)

    def process(self):
        raise NotImplementedError
