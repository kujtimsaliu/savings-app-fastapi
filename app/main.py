from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from google.oauth2 import id_token
from google.auth.transport import requests
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from .models import User
from .routes.users import users_router
from .routes.expenses import expenses_router
from .routes.budget import budget_router
from .routes.reports import reports_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

GOOGLE_CLIENT_ID = '347213759493-c7hdn80mephe4voo45ngsqvgldd6j6d6.apps.googleusercontent.com'

app.include_router(users_router, prefix="/users")
app.include_router(expenses_router, prefix="/expenses")
app.include_router(budget_router, prefix="/budget")
app.include_router(reports_router, prefix="/reports")

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/auth",
    tokenUrl="https://oauth2.googleapis.com/token",
)

class UserCreate(BaseModel):
    google_id: str
    email: str
    name: str
    given_name: str
    family_name: str
    picture_url: str

@app.post("/users")
async def create_or_fetch_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.google_id == user.google_id).first()
        if db_user:
            # User exists, return their data
            return {
                "id": db_user.id,
                "google_id": db_user.google_id,
                "email": db_user.email,
                "name": db_user.name,
                "given_name": db_user.given_name,
                "family_name": db_user.family_name,
                "picture_url": db_user.picture_url,
                "income": db_user.income
            }
        else:
            # Create new user
            new_user = User(
                google_id=user.google_id,
                email=user.email,
                name=user.name,
                given_name=user.given_name,
                family_name=user.family_name,
                picture_url=user.picture_url
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return {
                "id": new_user.id,
                "google_id": new_user.google_id,
                "email": new_user.email,
                "name": new_user.name,
                "given_name": new_user.given_name,
                "family_name": new_user.family_name,
                "picture_url": new_user.picture_url,
                "income": new_user.income
            }
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))