from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from ..dependencies import get_db, get_current_user
from ..crud import get_expenses
from datetime import datetime
from ..models import User

reports_router = APIRouter()


@reports_router.get("/monthly", response_model=Dict[str, Any])
def get_monthly_report(month: int, year: int, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    expenses = get_expenses(db, owner_id=current_user.id)
    month_expenses = [e for e in expenses if e.date.month == month and e.date.year == year]

    total_spent = sum(e.amount for e in month_expenses)
    categorized_expenses = {}
    for e in month_expenses:
        if e.category not in categorized_expenses:
            categorized_expenses[e.category] = 0
        categorized_expenses[e.category] += e.amount

    return {
        "month": month,
        "year": year,
        "total_spent": total_spent,
        "categorized_expenses": categorized_expenses
    }


@reports_router.get("/insights", response_model=Dict[str, Any])
def get_spending_insights(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    expenses = get_expenses(db, owner_id=current_user.id)

    total_spent = sum(e.amount for e in expenses)
    categorized_expenses = {}
    monthly_trends = {}

    for e in expenses:
        if e.category not in categorized_expenses:
            categorized_expenses[e.category] = 0
        categorized_expenses[e.category] += e.amount

        month_year = f"{e.date.month}-{e.date.year}"
        if month_year not in monthly_trends:
            monthly_trends[month_year] = 0
        monthly_trends[month_year] += e.amount

    most_common_category = max(categorized_expenses, key=categorized_expenses.get)

    return {
        "total_spent": total_spent,
        "categorized_expenses": categorized_expenses,
        "monthly_trends": monthly_trends,
        "most_common_category": most_common_category
    }