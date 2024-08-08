from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID



class UserBase(BaseModel):
    email: EmailStr
    name: str
    income: Optional[float] = None


class UserCreate(UserBase):
    password: str


class GoogleUserCreate(BaseModel):
    google_id: str
    email: EmailStr
    name: str
    given_name: str
    family_name: str
    picture_url: str


class UserOut(UserBase):
    id: UUID
    google_id: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture_url: Optional[str] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


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
        from_attributes = True


class BudgetBase(BaseModel):
    amount: float
    month: str
    day: str


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BudgetBase):
    pass


class Budget(BudgetBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True


class RefreshToken(BaseModel):
    refresh_token: str
