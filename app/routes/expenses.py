from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..schemas import ExpenseCreate, ExpenseUpdate, Expense
from ..crud import create_expense, get_expenses, update_expense, delete_expense
from ..dependencies import get_db, get_current_user
from ..models import User

expenses_router = APIRouter()

@expenses_router.post("/", response_model=Expense)
def add_expense(expense: ExpenseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_expense(db, expense, owner_id=current_user.id)

@expenses_router.get("/", response_model=List[Expense])
def read_expenses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_expenses(db, owner_id=current_user.id)

@expenses_router.put("/{expense_id}", response_model=Expense)
def edit_expense(expense_id: int, expense: ExpenseUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return update_expense(db, expense_id, expense)

@expenses_router.delete("/{expense_id}")
def remove_expense(expense_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    delete_expense(db, expense_id)
    return {"detail": "Expense deleted"}