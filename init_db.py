from sqlmodel import SQLModel
from backend.database import engine
from backend.models import Material, Machine, Project # Explicit import to register models

def init_db():
    print("Creating tables...")
    SQLModel.metadata.create_all(engine)
    print("Tables created.")

if __name__ == "__main__":
    print(f"Registered tables: {SQLModel.metadata.tables.keys()}")
    init_db()
