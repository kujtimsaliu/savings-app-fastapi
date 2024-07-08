from sqlalchemy.orm import Session
from .models import User, Expense, Budget
from .schemas import UserCreate, ExpenseCreate, ExpenseUpdate, BudgetCreate, BudgetUpdate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

# User CRUD
def create_user(db: Session, user: UserCreate):
    db_user = User(email=user.email, name=user.name, income=user.income, password=get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# Expense CRUD
def create_expense(db: Session, expense: ExpenseCreate, owner_id: int):
    db_expense = Expense(**expense.dict(), owner_id=owner_id)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def get_expenses(db: Session, owner_id: int):
    return db.query(Expense).filter(Expense.owner_id == owner_id).all()

def update_expense(db: Session, expense_id: int, expense: ExpenseUpdate):
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    for key, value in expense.dict().items():
        setattr(db_expense, key, value)
    db.commit()
    return db_expense

def delete_expense(db: Session, expense_id: int):
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    db.delete(db_expense)
    db.commit()

# Budget CRUD
def create_budget(db: Session, budget: BudgetCreate, owner_id: int):
    db_budget = Budget(**budget.dict(), owner_id=owner_id)
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

def get_budget(db: Session, owner_id: int):
    return db.query(Budget).filter(Budget.owner_id == owner_id).first()

def update_budget(db: Session, budget_id: int, budget: BudgetUpdate):
    db_budget = db.query(Budget).filter(Budget.id == budget_id).first()
    for key, value in budget.dict().items():
        setattr(db_budget, key, value)
    db.commit()
    return db_budget