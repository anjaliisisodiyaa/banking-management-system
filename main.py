from fastapi import FastAPI, HTTPException
from banking_system.schemas import AccountCreate, DepositWithdraw, RDScheme, FDScheme
from banking_system.account import BankAccount, rd, fd
import sqlite3
app = FastAPI()

users = {}  
# accm=BankAccount()
@app.get("/")
def read_root():
    return {"message": "Welcome to my Banking Management System!"}

@app.post("/create-account/")
def create_account(data: AccountCreate):
    if data.account_holder in users:
        raise HTTPException(status_code=400, detail="Account already exists.")

    acc = BankAccount(data.account_holder)
    try:
        acc.create_account(
            email=data.email,
            contact_number=data.contact_number,
            aadhar_number=data.aadhar_number,
            pancard=data.pancard,
            pincode=data.pincode,
            balance=data.balance,
            age=data.age
        )
        
        users[data.account_holder] = acc
        return {"message": "Account created successfully!"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/deposit/")
def deposit_money(data: DepositWithdraw):

    acc = BankAccount(account_holder=data.name)
    acc.deposit(data.amount)
    if not data.name:
        raise HTTPException(status_code=404, detail="User not found")

    acc.deposit(data.amount)
    return {
        "message": f"₹{data.amount} deposited.",
        "balance": acc.get_balance()
    }

@app.post("/withdraw/")
def withdraw_money(data: DepositWithdraw):
    
    acc = BankAccount(account_holder=data.name)
    acc.withdraw(data.amount)

    if not data.name:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        balance = acc.withdraw(data.amount)
        return {"message": f"₹{data.amount} withdrawn.", "balance": balance}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/balance/{name}")
def check_balance(name: str):
    acc = BankAccount(account_holder=name)
    # user = users.get(name)
    if not name:
        raise HTTPException(status_code=404, detail="User not found")
    return {"balance": acc.get_balance()}

@app.post("/deposit/rd/")
def open_rd(data: RDScheme):
    r = rd(account_holder=data.account_holder,
           initial_balance=data.initial_balance,
           duration=data.duration,
           amount=data.amount
    )
    total = r.mechanism(data.monthly_deposits)
    return {"message": "RD completed.",
            "total_amount": total
        }

@app.post("/deposit/fd/")
def open_fd(data: FDScheme):
    f = fd(account_holder=data.account_holder,
        #    initial_balance=data.initial_balance, 
           duration=data.duration, 
           amount=data.amount)
    invested = f.open_deposite_fd()
    return {"message": "FD created", "invested_amount": invested}


