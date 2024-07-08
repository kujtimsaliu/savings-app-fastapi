from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    name: str
    income: float


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


class ExpenseBase(BaseModel):
    amount: float
    category: str
    date: datetime
    description: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(ExpenseBase):
    pass


class Expense(ExpenseBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True  # Updated for Pydantic v2


class BudgetBase(BaseModel):
    amount: float
    month: str


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BudgetBase):
    pass


class Budget(BudgetBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True  # Updated for Pydantic v2
