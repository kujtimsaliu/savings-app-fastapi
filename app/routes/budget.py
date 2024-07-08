from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..schemas import BudgetCreate, BudgetUpdate, Budget
from ..crud import create_budget, get_budget, update_budget
from ..dependencies import get_db, get_current_user
from ..models import User

budget_router = APIRouter()

@budget_router.post("/", response_model=Budget)
def set_budget(budget: BudgetCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_budget(db, budget, owner_id=current_user.id)

@budget_router.get("/", response_model=Budget)
def read_budget(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_budget(db, owner_id=current_user.id)

@budget_router.put("/", response_model=Budget)
def update_budget(budget: BudgetUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return update_budget(db, budget_id=budget.id, budget=budget)