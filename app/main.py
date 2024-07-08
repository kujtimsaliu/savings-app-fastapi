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
class TokenRequest(BaseModel):
    id_token: str

@app.post("/auth/google")
async def google_auth(token_request: TokenRequest, db: Session = Depends(get_db)):
    try:
        idinfo = id_token.verify_oauth2_token(token_request.id_token, requests.Request(), GOOGLE_CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        google_id = idinfo['sub']
        email = idinfo['email']
        name = idinfo.get('name', '')

        # Check if user exists
        user = db.query(User).filter(User.google_id == google_id).first()
        if not user:
            # Create new user
            user = User(google_id=google_id, email=email, name=name)
            db.add(user)
            db.commit()
            db.refresh(user)

        # Return user info
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "income": user.income if user.income else 0,
            "google_id": user.google_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))