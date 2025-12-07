from sqlmodel import Session, select, func
from backend.database import engine
from backend.models import Material, Machine

def check_counts():
    with Session(engine) as session:
        mat_count = session.exec(select(func.count(Material.id))).one()
        mach_count = session.exec(select(func.count(Machine.id))).one()
        print(f"Materials: {mat_count}")
        print(f"Machines: {mach_count}")

if __name__ == "__main__":
    check_counts()
