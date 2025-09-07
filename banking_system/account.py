import time
import sqlite3

class BankAccount:
    def __init__(self, account_holder, initial_balance=0.0):
        self.account_holder = account_holder
        self.initial_balance = initial_balance 
        self.email = None
        self.contact_number = None
        self.pincode = None
        self.aadhar_number = None
        self.age = None
        self.pancard = None

        self._setup_db()
        
    def _setup_db(self):
        conn = sqlite3.connect("bank_data.db")
        cur =  conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_holder TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            contact_number TEXT NOT NULL,
            aadhar_number INTEGER NOT NULL UNIQUE,
            pancard TEXT NOT NULL,
            pincode INTEGER,
            balance INTEGER,
            age INTEGER
            )""")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS rd_schemes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_holder TEXT NOT NULL,
                duration INTEGER NOT NULL,
                amount REAL NOT NULL,
                start_date TEXT DEFAULT CURRENT_TIMESTAMP
                )""")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS fd_schemes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_holder TEXT NOT NULL,
                duration INTEGER NOT NULL,
                amount REAL NOT NULL,
                start_date TEXT DEFAULT CURRENT_TIMESTAMP
                )""")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_holder TEXT NOT NULL,
                txn_type TEXT NOT NULL,
                amount REAL NOT NULL,
                txn_time TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """)

        conn.commit()
        conn.close()


        
    def create_account(self, email, contact_number, aadhar_number, pancard, balance, pincode, age):
        if not aadhar_number or not pancard or age < 18:
            raise ValueError("Invalid identity details or age not eligible")
        self.email = email
        self.contact_number = contact_number
        self.pincode = pincode
        self.balance = balance
        self.aadhar_number=aadhar_number
        self.age = age
        self.pancard = pancard

        conn = sqlite3.connect("bank_data.db")
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO accounts (account_holder, email, contact_number, aadhar_number, pancard, pincode, age, balance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.account_holder, self.email, self.contact_number, self.aadhar_number,
            self.pancard, self.pincode, self.age, self.balance
        ))
        conn.commit()
        conn.close()

        print(f" Account created for {self.account_holder}")
        
    def _update_balance(self):
        conn = sqlite3.connect("bank_data.db")
        cur = conn.cursor()
        cur.execute("""
        UPDATE accounts SET balance = ? WHERE account_holder = ?
        """, (self.balance, self.account_holder))
        conn.commit()
        conn.close()  
        
    def _log_transaction(self, txn_type, amount):
        conn = sqlite3.connect("bank_data.db")
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO transactions (account_holder, txn_type, amount)
        VALUES (?, ?, ?)
        """, (self.account_holder, txn_type, amount))
        conn.commit()
        conn.close()
       
    def deposit(self, amount):
        if amount <= 0:
            print("Deposit amount must be positive.")
            return
        
        conn = sqlite3.connect("bank_data.db")
        cur = conn.cursor()
        cur.execute("SELECT balance FROM accounts WHERE account_holder = ?", (self.account_holder,))
        row = cur.fetchone()
        if not row:
            conn.close()
            raise ValueError("Account not found.")

        current_balance=row[0]
        new_balance = current_balance+amount
        self.balance = new_balance
        cur.execute("""
        UPDATE accounts SET balance = ? WHERE account_holder = ?
    """, (new_balance, self.account_holder))
        cur.execute("""
        INSERT INTO transactions (account_holder, txn_type, amount)
        VALUES (?, ?, ?)
    """, (self.account_holder, "Deposit", amount))

        conn.commit()
        conn.close()
        print(f"Deposited ₹{amount:.2f}. New balance: ₹{new_balance:.2f}")

    
    def withdraw(self, amount):
        if amount <= 0:
            print("Withdrawal amount must be positive.")
            return {"message": "Withdrawal amount must be positive."}

        conn = sqlite3.connect("bank_data.db")
        cur = conn.cursor()

        cur.execute("SELECT balance FROM accounts WHERE account_holder = ?", (self.account_holder,))
        row = cur.fetchone()

        if not row:
            conn.close()
            raise ValueError("Account not found.")

        current_balance = row[0]
        if amount > current_balance:
            conn.close()
            print("Insufficient balance!")
            return {"message": "Insufficient balance!"}

        new_balance = current_balance - amount
        self.balance = new_balance

        cur.execute("UPDATE accounts SET balance = ? WHERE account_holder = ?", (new_balance, self.account_holder))
        cur.execute("INSERT INTO transactions (account_holder, txn_type, amount) VALUES (?, ?, ?)",
                    (self.account_holder, "Withdraw", amount))

        conn.commit()
        conn.close()
        print(f"Withdrawn ₹{amount:.2f}. New balance: ₹{new_balance:.2f}")

        return {
            "message": f"₹{amount:.2f} withdrawn.",
            "balance": new_balance
        }
                
    
    def get_balance(self):
        conn = sqlite3.connect("bank_data.db")
        cur = conn.cursor()

        cur.execute("SELECT balance FROM accounts WHERE account_holder = ?", (self.account_holder,))
        row = cur.fetchone()
        conn.close()

        if not row:
            raise ValueError("Account not found.")

        self.balance = row[0]
        return {"balance": self.balance}
    
    # get_balance()
    

class rd(BankAccount):
  def __init__(self, account_holder, initial_balance, duration, amount):
    super().__init__(account_holder, initial_balance)
    self.duration=duration
    self.amount=amount
    self.total_amt=0
    self.deposit_history=[]
  
  def mechanism(self, monthly_deposits: list):
        if len(monthly_deposits) < self.duration:
            raise ValueError("Monthly deposit count doesn't match duration")

        for i in range(self.duration):
            amount = monthly_deposits[i]
            self.deposit(amount)
            self.total_amt += amount
            self.deposit_history.append(amount)
            print(f"Month {i+1}: ₹{amount} added. Total so far: ₹{self.total_amt}")
            time.sleep(1)

        self._save_rd_to_db()
        return self.total_amt
    
  def _save_rd_to_db(self):
        conn = sqlite3.connect("bank_data.db")
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO rd_schemes (account_holder, duration, amount)
        VALUES (?, ?, ?)
        """, (self.account_holder, self.duration, self.amount))
        conn.commit()
        conn.close()  
        
  def open_deposite_rd(self):
    print("Your recuuring deposits details: ")
    print(f"Holder: {self.account_holder}, Amount: ₹{self.amount}, Duration: {self.duration} months")

class fd(BankAccount):
    def __init__(self, account_holder, duration, amount):
      super().__init__(account_holder)
      self.duration=duration
      self.amount=amount

    def open_deposite_fd(self):
      print("Your fix deposit details: ")
      print(f"Holder: {self.account_holder}, Amount: ₹{self.amount}, Duration: {self.duration} months")
      self._save_fd_to_db() 
      invested = self.initial_balance + self.amount
      return invested 
      
    def _save_fd_to_db(self):
        conn = sqlite3.connect("bank_data.db")
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO fd_schemes (account_holder, duration, amount)
        VALUES (?, ?, ?)
        """, (self.account_holder,self.duration, self.amount))
        conn.commit()
        conn.close()    
        
        
    # def display_account(self):
    #     print(f"Account Holder: {self.account_holder}")
    #     print(f"Current Balance: ₹{self.__balance:.2f}")
    

    
    # def save_to_excel(self, filename='data_store/transaction_history.xlsx'):
    #         os.makedirs(os.path.dirname(filename), exist_ok=True)

    #         if not os.path.exists(filename):
    #             wb = Workbook()
    #             ws_user = wb.active
    #             ws_user.title = "User Details"
    #             ws_user.append(["Account Holder", "Email", "Contact Number", "Pincode", "Balance"])

    #             wb.create_sheet(title="Transactions")
    #             # ws_user.append(ws_txn)
    #             wb.save(filename)

    #         wb = load_workbook(filename)
    #         ws_user = wb["User Details"]

    #         user_exists = False
    #         for row in ws_user.iter_rows(min_row=2, values_only=True):
    #             if row[0] == self.account_holder and row[1] == self.email:
    #                 user_exists = True
    #                 break

    #         if not user_exists:
    #             ws_user.append([
    #                 self.account_holder,
    #                 self.email,
    #                 self.contact_number,
    #                 self.pincode,
    #                 f"{self.__balance:.2f}"
    #             ])

    #         wb.save(filename)
    #         print(f"User data saved to '{filename}' in 'User Details' sheet.")

    # def log_transaction(self, txn_type, amount, filename='data_store/transaction_history.xlsx'):
    #     self.save_to_excel(filename)

    #     wb = load_workbook(filename)
    #     ws_txn = wb["Transactions"]

    #     ws_txn.append([
    #         self.account_holder,
    #         self.email,
    #         self.contact_number,
    #         self.pincode,
    #         txn_type,
    #         f"₹{amount:.2f}",
    #         f"₹{self.__balance:.2f}"
    #     ])

    #     wb.save(filename)
    #     print(f"{txn_type} logged to '{filename}' in 'Transactions' sheet.")  
    
    
        
        


# choice = input("Do you want to open a bank account? (yes/no): ").strip().lower()
# if choice == "yes":
#     name = input("Enter account holder name: ")
#     email = input("Enter account holder mail: ")
#     age = int(input("Enter your age: "))
#     contact = int(input("Enter account holder contact number: "))
#     pincode = int(input("Enter the pincode of your location: "))
#     aadhar = input("Enter your aadhar number: ")
#     pancard = input("Enter your pancard number: ")
    
#     c = BankAccount(name, 0.0)
#     c.create_account(name,email,contact_number=contact)
#     c.create_account(aadhar_number=aadhar,pancard=pancard,pincode=pincode,age=age)

#     c.save_to_csv()

#     while True:
#         print("\nChoose an option:")
#         print("1. Deposit")
#         print("2. Withdraw")
#         print("3. Show Balance")
#         print("4. Exit")

#         option = input("Enter your choice (1/2/3/4): ")

#         if option == "1":
#             amount = float(input("Enter amount to deposit: ₹"))
#             c.deposit(amount)

#         elif option == "2":
#             amount = float(input("Enter amount to withdraw: ₹"))
#             c.withdraw(amount)

#         elif option == "3":
#             c.display_account()

#         elif option == "4":
#             print("Thank you! Visit again.")
#             break

#         else:
#             print("Invalid choice. Try again.")

# else:
#     print("Okay, maybe later! ")
   
# choice = input("Are you interested in deposit ?\nWhich deposit do you want to open? (RD/FD): ").strip().upper()

# if choice == "RD":
#     r = rd(
#         account_holder=input("Enter the Name of Account Holder:"),
#         initial_balance=0.0,
#         recurring_deposit=True,
#         duration=int(input("Duration: ")),
#         amount=int(input("Enter the amount for RD: "))
#     )
#     r.open_deposite()
#     r.mechanism()
#     r.display_account()

# elif choice == "FD":
#     f = fd(
#         account_holder=input("Enter the Name of Account Holder:"),
#         initial_balance=5000.0,
#         fix_deposit=True,
#         duration=int(input("Duration: ")),
#         amount=int(input("Enter the amount for FD: "))
#     )
#     f.open_deposite()
#     f.deposit(f.amount)
#     f.display_account()

# else:
#     print("Invalid choice! Please select 'RD' or 'FD'.")

