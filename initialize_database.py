from sqlalchemy import create_engine
from app.models import Base

SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:kujtim123@localhost/savings-app'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

Base.metadata.create_all(bind=engine)
