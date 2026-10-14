import csv
from datetime import datetime
import hashlib
import os
import sys


def hash_pin(pin: str, salt: str = None) -> tuple[str, str]:
    """Hashes a PIN using SHA-256 with a unique salt."""
    if salt is None:
        salt = os.urandom(16).hex()
    hased = hashlib.sha256((salt + pin).encode()).hexdigest()
    return hased, salt

class Transaction:
    def __init__(self, tx_type: str, amount: float, balance_after: float, note: str = ""):
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.tx_type = tx_type
        self.amount = amount
        self.balance_after = balance_after
        self.note = note

    def to_row(self) -> list:
        return [self.timestamp, self.tx_type, f"{self.amount: .2f}", f"{self.balance_after:.2f}", self.note]
    

class BankAccount:
    def __init__(self, account_number: str, holder_name: str, pin: str, initial_balance: float = 0.0):
        self.account_number = account_number
        self.holder_name = holder_name
        self.pin_hash, self.salt = hash_pin(pin)
        self.balance = float(initial_balance)
        self.history: list[Transaction] = []

        if initial_balance > 0:
            self._log_transaction("INITIAL_DEPOSIT", initial_balance, "Account opened")

    def verify_pin(self, entered_pin: str) -> bool:
        check_hash, _ = hash_pin(entered_pin, self.salt)
        return check_hash == self.pin_hash
    
    def _log_transaction(self, tx_type: str, amount: float, note: str = ""):
        tx = Transaction(tx_type, amount, self.balance, note)
        self.history.append(tx)

    def deposit(self, amount: float, note: str = "Deposit") -> bool:
        if amount <= 0:
            print("Error: Deposit amount must be positive. ")
            return False
        self.balance += amount
        self._log_transaction("DEPOSIT", amount, note)
        return True
    
    def withdraw(self, amount: float, note: str = "withdrawal") -> bool:
        if amount <= 0:
            print("Error: Withdrawal amount must be positive. ")
            return False
        if amount > self.balance:
            print("Error: Insufficient funds. ")
            return False
        self.balance -= amount
        self._log_transaction("WITHDRAWAL", amount, note)
        return True
    
    def display_history(self):
        if not self.history:
            print("No transactions on record.")
            return
        
        print("\n" + "=" * 70)
        print(f"{'Timestamp':<20} | {'Type':<15} | {'Amount':<10} | {'Balance':<10} | {'Note'}")
        print("-" * 70)
        for tx in self.history:
            print(f"{tx.timestamp:<20} | {tx.tx_type:<15} | {tx.amount:<10.2f} | {tx.balance_after:<10.2f} | {tx.note}")
        print("=" * 70 + "\n")

    def export_history_to_csv(self, filename: str = None) -> str:
        if not filename:
            filename = f"statement_{self.account_number}.csv"

        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Type", "Amount", "Balance After", "Note"])
            for tx in self.history:
                writer.writerow(tx.to_row())
        
        return filename

class SavingsAccount(BankAccount):
    def __init__(self, account_number: str, holder_name: str, pin: str, initial_balance: float = 0.0, 
                 interest_rate: float = 0.04, min_balance: float = 100.0):
        super().__init__(account_number, holder_name, pin, initial_balance)
        self.interest_rate = interest_rate  # 4% annual interest
        self.min_balance = min_balance

    def apply_interest(self) -> float:
        """Calculates and credits monthly interest (Annual Rate / 12)."""
        monthly_interest = self.balance * (self.interest_rate / 12)
        if monthly_interest > 0:
            self.balance += monthly_interest
            self._log_transaction("INTEREST", monthly_interest, f"Monthly yield at {self.interest_rate*100:.1f}% APR")
            return monthly_interest
        return 0.0

    def withdraw(self, amount: float, note: str = "Withdrawal") -> bool:
        if self.balance - amount < self.min_balance:
            print(f"Error: Minimum balance of ${self.min_balance:.2f} required for Savings Account.")
            return False
        return super().withdraw(amount, note)


class CheckingAccount(BankAccount):
    def __init__(self, account_number: str, holder_name: str, pin: str, initial_balance: float = 0.0, 
                 overdraft_limit: float = 500.0):
        super().__init__(account_number, holder_name, pin, initial_balance)
        self.overdraft_limit = overdraft_limit

    def withdraw(self, amount: float, note: str = "Withdrawal") -> bool:
        if amount <= 0:
            print("Error: Withdrawal amount must be positive.")
            return False
        if self.balance - amount < -self.overdraft_limit:
            print(f"Error: Exceeds overdraft limit of ${self.overdraft_limit:.2f}.")
            return False
        
        self.balance -= amount
        self._log_transaction("WITHDRAWAL", amount, note)
        return True


class BankSystem:
    def __init__(self):
        self.accounts: dict[str, BankAccount] = {}

    def create_account(self, acc_type: str, holder_name: str, pin: str, initial_deposit: float) -> str:
        acc_num = f"ACC{len(self.accounts) + 1001}"
        if acc_type.lower() == "savings":
            acc = SavingsAccount(acc_num, holder_name, pin, initial_deposit)
        elif acc_type.lower() == "checking":
            acc = CheckingAccount(acc_num, holder_name, pin, initial_deposit)
        else:
            raise ValueError("Unsupported account type.")
        
        self.accounts[acc_num] = acc
        return acc_num

    def authenticate(self, acc_num: str, pin: str) -> BankAccount | None:
        account = self.accounts.get(acc_num)
        if account and account.verify_pin(pin):
            return account
        return None

    def transfer(self, source_acc: BankAccount, target_acc_num: str, amount: float) -> bool:
        if target_acc_num not in self.accounts:
            print("Error: Beneficiary account not found.")
            return False
        if source_acc.account_number == target_acc_num:
            print("Error: Cannot transfer to self.")
            return False
        
        target_acc = self.accounts[target_acc_num]
        
        # Perform atomic transfer
        if source_acc.withdraw(amount, note=f"Transfer to {target_acc_num}"):
            target_acc.deposit(amount, note=f"Transfer from {source_acc.account_number}")
            print(f"Successfully transferred ${amount:.2f} to {target_acc_num}.")
            return True
        return False


def run_cli():
    bank = BankSystem()

    # Pre-seed sample accounts for testing
    bank.create_account("savings", "Alice Smith", "1234", 1500.0)
    bank.create_account("checking", "Bob Jones", "4321", 500.0)

    while True:
        print("\n--- BANK PORTAL ---")
        print("1. Open Account")
        print("2. Login")
        print("3. Exit")
        choice = input("Select an option (1-3): ").strip()

        if choice == "1":
            name = input("Enter account holder name: ").strip()
            acc_type = input("Account type ('savings' or 'checking'): ").strip().lower()
            pin = input("Set a 4-digit PIN: ").strip()
            try:
                deposit = float(input("Initial deposit: "))
                acc_num = bank.create_account(acc_type, name, pin, deposit)
                print(f"Account successfully created! Your Account Number is: {acc_num}")
            except ValueError:
                print("Invalid input values. Please try again.")

        elif choice == "2":
            acc_num = input("Enter Account Number: ").strip()
            pin = input("Enter PIN: ").strip()
            account = bank.authenticate(acc_num, pin)

            if not account:
                print("Authentication failed: Invalid Account Number or PIN.")
                continue

            print(f"\nWelcome back, {account.holder_name}!")
            while True:
                print(f"\n--- Account Menu [{account.account_number}] ---")
                print(f"Current Balance: ${account.balance:.2f}")
                print("1. Deposit")
                print("2. Withdraw")
                print("3. Transfer Funds")
                print("4. View Transaction History")
                print("5. Export History to CSV")
                if isinstance(account, SavingsAccount):
                    print("6. Calculate & Apply Monthly Interest")
                print("0. Logout")

                sub_choice = input("Select an option: ").strip()

                if sub_choice == "1":
                    amt = float(input("Deposit amount: $"))
                    if account.deposit(amt):
                        print(f"Deposited ${amt:.2f}. New Balance: ${account.balance:.2f}")

                elif sub_choice == "2":
                    amt = float(input("Withdrawal amount: $"))
                    if account.withdraw(amt):
                        print(f"Withdrew ${amt:.2f}. Remaining Balance: ${account.balance:.2f}")

                elif sub_choice == "3":
                    target = input("Target Account Number: ").strip()
                    amt = float(input("Transfer amount: $"))
                    bank.transfer(account, target, amt)

                elif sub_choice == "4":
                    account.display_history()

                elif sub_choice == "5":
                    fname = account.export_history_to_csv()
                    print(f"Transaction history exported to '{fname}'.")

                elif sub_choice == "6" and isinstance(account, SavingsAccount):
                    earned = account.apply_interest()
                    print(f"Credited ${earned:.2f} in interest. New Balance: ${account.balance:.2f}")

                elif sub_choice == "0":
                    print("Logged out successfully.")
                    break
                else:
                    print("Invalid option selected.")

        elif choice == "3":
            print("Shutting down bank system. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid selection.")


if __name__ == "__main__":
    run_cli()
        


