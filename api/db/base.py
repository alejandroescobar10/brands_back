import os
from sqlalchemy.orm import  declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")  # viene de tu .env (Neon)
Base = declarative_base()
