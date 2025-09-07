from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List



class AccountCreate(BaseModel):
    account_holder: str
    email: EmailStr
    contact_number: str
    # contact_number: int = Field(..., min_length=10, max_length=10, description="10-digit contact number")
    aadhar_number: int
    pancard: str
    pincode: int
    age: int
    balance: float = 0.0

class DepositWithdraw(BaseModel):
    name: str
    amount: Optional[float]
    
class RDScheme(BaseModel):
    account_holder: str
    duration: int
    amount: float
    initial_balance: float
    monthly_deposits: List[float] 

class FDScheme(BaseModel):
    account_holder: str
    # initial_balance: float
    duration: int
    amount: float
