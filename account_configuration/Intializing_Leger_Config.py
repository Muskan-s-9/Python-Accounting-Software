from  Accounting_Ledgers_Configuration import Accounting_Ledgers_Configuration
from Configuration import config_1, config_2
import pandas as pd

class Inializing_Leger_Config:
    
    def __init__(self):
        self.path  = 'Account_Configuration//Ledger_config_data//'
        self.ledger_config = Accounting_Ledgers_Configuration(config_1,config_2)
        
    def generate_config(self, Flag=False):
        if Flag:
            ledger_config.get_ledger_configs_dataframe(path)
     