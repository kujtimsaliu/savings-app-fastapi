from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Any
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.database import engine, Base, get_db
from .routes import users_router, expenses_router, budget_router, reports_router
from .models import User
from .schemas import UserCreate, UserOut, Token, GoogleUserCreate, RefreshToken

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Security
SECRET_KEY = "verysecret"
REFRESH_SECRET_KEY = "veryrefresh"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
GOOGLE_CLIENT_ID = '347213759493-c7hdn80mephe4voo45ngsqvgldd6j6d6.apps.googleusercontent.com'

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.include_router(users_router, prefix="/users")
app.include_router(expenses_router, prefix="/expenses")
app.include_router(budget_router, prefix="/budget")
app.include_router(reports_router, prefix="/reports")


# Token creation
def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.now(timezone.utc) + expires_delta
    else:
        expires_delta = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: str, expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.now(timezone.utc) + expires_delta
    else:
        expires_delta = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt


# User authentication
def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.password:
        return False
    if not pwd_context.verify(password, user.password):
        return False
    return user


async def get_current_user(token: str = Security(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user = db.query(User).filter(User.id == user_id).first()

        if user is None:
            raise credentials_exception

        return user

    except JWTError:
        raise credentials_exception


@app.post("/user/refresh-token", tags=["Authentication"])
async def refresh_token(token_data: RefreshToken, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token_data.refresh_token, REFRESH_SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user = db.query(User).filter(User.id == user_id).first()

        if user is None:
            raise credentials_exception

        new_access_token = create_access_token(subject=user_id)
        new_refresh_token = create_refresh_token(subject=user_id)

        return {"access_token": new_access_token, "token_type": "bearer", "refresh_token": new_refresh_token}
    except jwt.JWTError:
        raise credentials_exception


@app.post("/users/signup")
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)
    new_user = User(email=user.email, password=hashed_password, name=user.name, income=user.income)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserOut.from_orm(new_user)


@app.post("/auth/google")
def google_auth(google_user: GoogleUserCreate, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.google_id == google_user.google_id).first()
        if not user:
            user = User(
                google_id=google_user.google_id,
                email=google_user.email,
                name=google_user.name,
                given_name=google_user.given_name,
                family_name=google_user.family_name,
                picture_url=google_user.picture_url
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        access_token = create_access_token(user.google_id)
        refresh_token = create_refresh_token(user.google_id)

        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer",
                "user": UserOut.from_orm(user)}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token")


# Protected route example
@app.get("/users/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return UserOut.from_orm(current_user)
