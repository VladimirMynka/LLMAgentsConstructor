# Import necessary modules
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

database = os.getenv("POSTGRES_DATABASE")
user = os.getenv("POSTGRES_USERNAME")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")


# Step 2: Set up the database URL
connection_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

# Step 3: Create a SQLAlchemy engine
engine = create_engine(connection_string, echo=True)


# Step 4: Define a base class
class Base(DeclarativeBase):
    pass


def init_db():
    with engine.begin() as conn:
        Base.metadata.create_all(conn)
