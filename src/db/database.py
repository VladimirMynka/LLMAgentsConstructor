# Import necessary modules
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

url = os.getenv("POSTGRES_URL")


# Step 2: Set up the database URL
connection_string = f"postgresql+asyncpg://{url}"

# Step 3: Create a SQLAlchemy engine
engine = create_engine(connection_string, echo=True)


# Step 4: Define a base class
class Base(DeclarativeBase):
    pass


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
