# This file was missing from the article. It gives the app a "session"
# (a conversation with the database) connected to the MyFirstAPI database.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.connection import build_url, PROJECT_DATABASE

engine = create_engine(build_url(PROJECT_DATABASE), pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
