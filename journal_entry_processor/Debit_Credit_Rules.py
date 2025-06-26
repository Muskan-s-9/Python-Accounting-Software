class AssetExpenseRule:
    def __init__(self, opening_balance: float = 0.0):
        self.opening_balance = opening_balance
        self.debit_balance = opening_balance
        self.credit_balance = opening_balance

    def credit_transaction(self, credit_amount: float) -> float:
        self.credit_balance = self.opening_balance - credit_amount
        return self.credit_balance

    def debit_transaction(self, debit_amount: float) -> float:
        self.debit_balance = self.opening_balance + debit_amount
        return self.debit_balance

    def get_balance(self) -> tuple:
        return self.opening_balance, self.debit_balance, self.credit_balance


class LiabilityCapitalRevenueRule:
    def __init__(self, opening_balance: float = 0.0):
        self.opening_balance = opening_balance
        self.debit_balance = opening_balance
        self.credit_balance = opening_balance

    def credit_transaction(self, credit_amount: float) -> float:
        self.credit_balance = self.opening_balance + credit_amount
        return self.credit_balance

    def debit_transaction(self, debit_amount: float) -> float:
        self.debit_balance = self.opening_balance - debit_amount
        return self.debit_balance

    def get_balance(self) -> tuple:
        return self.opening_balance, self.debit_balance, self.credit_balance
