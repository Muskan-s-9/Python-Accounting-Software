from journal_entry_processor.Purchase_Journal_Entry import PurchaseJournalEntryProcessor
from journal_entry_processor.Credit_Note_Journal_Entry import CreditNoteJournalEntryProcessor
from journal_entry_processor.Debit_Note_Journal_Entry import DebitNoteJournalEntryProcessor
from journal_entry_processor.Sales_Journal_Entry import SalesJournalEntryProcessor
import os
import pandas as pd

class PassingJournalEntry:
    
    def __init__(self,journal_type):
        self.journal_type  = journal_type
        
        
    def passing_entry(self):
        
        if self.journal_type.lower()=="purchase":
            file_path  = 'invoices_scraped_data\Purchase_Invoices_data\Purchase_Common_Template.xlsx'
            entry_df = pd.read_excel(file_path,engine='openpyxl')
            pass_journal = PurchaseJournalEntryProcessor(entry_df)
            pass_journal.process_entries()
            entries = pass_journal.get_journal_entries()
            df = pd.DataFrame(entries)
            print(df)
            output_path = f'journal_entry_processed_data/Purchase_Invoices_Results_data/{self.journal_type}_journal_entry_result.xlsx'
            df.to_excel(output_path, index=False)
            
            
        if self.journal_type.lower()=="sales":
            file_path  = 'invoices_scraped_data\Sales_Invoices_data\Sales_Common_Template.xlsx'
            entry_df = pd.read_excel(file_path,engine='openpyxl')
            pass_journal = SalesJournalEntryProcessor(entry_df)
            print(entry_df)
            pass_journal.process_entries()
            entries = pass_journal.get_journal_entries()
            df = pd.DataFrame(entries)
            print(df)
            output_path = f'journal_entry_processed_data/Sales_Invoices_Results_data/{self.journal_type}_journal_entry_result.xlsx'
            df.to_excel(output_path, index=False)
            
            
        if self.journal_type.lower()=="credit_note":
            file_path  = 'invoices_scraped_data\Credit_Note_Invoices_data\Credit_Note_Common_Template.xlsx'
            entry_df = pd.read_excel(file_path,engine='openpyxl')
            pass_journal = CreditNoteJournalEntryProcessor(entry_df)
            pass_journal.process_entries()
            entries = pass_journal.get_journal_entries()
            df = pd.DataFrame(entries)
            output_path = f'journal_entry_processed_data/Credit_Note_Invoices_Results_data/{self.journal_type}_journal_entry_result.xlsx'
            df.to_excel(output_path, index=False)
            
            
            
        if self.journal_type.lower()=="debit_note":
            file_path  = 'invoices_scraped_data\Debit_Note_Invoices_data\Debit_Note_Common_Template.xlsx'
            entry_df = pd.read_excel(file_path,engine='openpyxl')
            pass_journal = DebitNoteJournalEntryProcessor(entry_df)
            pass_journal.process_entries()
            entries = pass_journal.get_journal_entries()
            df = pd.DataFrame(entries)
            output_path = f'journal_entry_processed_data/Debit_Note_Invoices_Results_data/{self.journal_type}_journal_entry_result.xlsx'
            df.to_excel(output_path, index=False)
            
            
            