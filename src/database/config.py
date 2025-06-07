from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.exceptions.exceptions import DatabaseError


load_dotenv()


main_dir = Path(__file__).resolve().parent
print(main_dir)


DATABASE_URI = getenv("DATABASE_URI")
engine = create_engine(DATABASE_URI)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(engine):
    sql_path = f"{main_dir}/table.sql"

    try:
        with open(sql_path, "r") as file:
            sql_script = file.read()
        
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(text(sql_script))
        print("Database initialization and migration complete")
    except Exception as e:
        raise DatabaseError(f"Error connecting database: {str(e)}")

