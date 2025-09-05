# database/connection.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Define the path for the SQLite database file
# It will be created in the root of your project
DATABASE_FILE = "sql_app.db"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, DATABASE_FILE)}"

# Create a SQLAlchemy engine
# connect_args={"check_same_thread": False} is needed for SQLite when working with FastAPI
# because SQLite only allows one thread to communicate with it at a time.
# FastAPI often uses multiple threads, so this setting allows multiple requests
# to be processed by the same database session, preventing issues.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a SessionLocal class
# Each instance of SessionLocal will be a database session.
# The 'autocommit=False' means that the database session will not commit changes
# until explicitly told to do so.
# The 'autoflush=False' means that objects will not be flushed to the database
# until explicitly told to do so or a commit is performed.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our ORM models
# This will be inherited by all our SQLAlchemy models
Base = declarative_base()

# Dependency to get a database session
# This function will be used by FastAPI endpoints to get a database session
# and ensure it's closed after the request is finished.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create all tables defined in models.py
def create_db_tables():
    Base.metadata.create_all(bind=engine)
