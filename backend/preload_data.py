from sqlmodel import Session, select
from backend.database import engine, create_db_and_tables
from backend.models import Material, Machine

def create_materials(session: Session):
    materials = [
        # Commodity Plastics
        Material(name="ABS General Purpose", type="Generic", family="ABS", melt_temp_min=220, melt_temp_max=260, mold_temp_min=40, mold_temp_max=80, viscosity_class="Medium", shrinkage_min=0.004, shrinkage_max=0.007, density=1.04, max_flow_length_ratio=150),
        Material(name="PP Homopolymer", type="Generic", family="PP", melt_temp_min=200, melt_temp_max=250, mold_temp_min=20, mold_temp_max=60, viscosity_class="Low", shrinkage_min=0.010, shrinkage_max=0.020, density=0.90, max_flow_length_ratio=250),
        Material(name="PE-HD (High Density Polyethylene)", type="Generic", family="PE", melt_temp_min=200, melt_temp_max=280, mold_temp_min=20, mold_temp_max=60, viscosity_class="Low", shrinkage_min=0.015, shrinkage_max=0.030, density=0.95, max_flow_length_ratio=200),
        Material(name="PE-LD (Low Density Polyethylene)", type="Generic", family="PE", melt_temp_min=180, melt_temp_max=240, mold_temp_min=20, mold_temp_max=60, viscosity_class="Low", shrinkage_min=0.015, shrinkage_max=0.035, density=0.92, max_flow_length_ratio=220),
        Material(name="PS (Polystyrene) General Purpose", type="Generic", family="PS", melt_temp_min=180, melt_temp_max=250, mold_temp_min=20, mold_temp_max=60, viscosity_class="Low", shrinkage_min=0.004, shrinkage_max=0.007, density=1.05, max_flow_length_ratio=200),
        Material(name="PVC Rigid", type="Generic", family="PVC", melt_temp_min=170, melt_temp_max=210, mold_temp_min=30, mold_temp_max=60, viscosity_class="High", shrinkage_min=0.002, shrinkage_max=0.005, density=1.35, max_flow_length_ratio=100),

        # Engineering Plastics
        Material(name="PA6 (Nylon 6)", type="Generic", family="PA6", melt_temp_min=230, melt_temp_max=280, mold_temp_min=60, mold_temp_max=90, viscosity_class="Low", shrinkage_min=0.005, shrinkage_max=0.015, density=1.13, max_flow_length_ratio=180),
        Material(name="PA66 (Nylon 66)", type="Generic", family="PA66", melt_temp_min=275, melt_temp_max=295, mold_temp_min=60, mold_temp_max=90, viscosity_class="Low", shrinkage_min=0.010, shrinkage_max=0.020, density=1.14, max_flow_length_ratio=200),
        Material(name="PC (Polycarbonate)", type="Generic", family="PC", melt_temp_min=280, melt_temp_max=320, mold_temp_min=80, mold_temp_max=120, viscosity_class="High", shrinkage_min=0.005, shrinkage_max=0.007, density=1.20, max_flow_length_ratio=100),
        Material(name="PC/ABS Blend", type="Generic", family="PC/ABS", melt_temp_min=240, melt_temp_max=280, mold_temp_min=60, mold_temp_max=90, viscosity_class="Medium", shrinkage_min=0.005, shrinkage_max=0.007, density=1.15, max_flow_length_ratio=130),
        Material(name="POM (Acetal) Copolymer", type="Generic", family="POM", melt_temp_min=190, melt_temp_max=210, mold_temp_min=80, mold_temp_max=100, viscosity_class="Medium", shrinkage_min=0.018, shrinkage_max=0.022, density=1.41, max_flow_length_ratio=150),
        Material(name="PBT Unfilled", type="Generic", family="PBT", melt_temp_min=240, melt_temp_max=270, mold_temp_min=60, mold_temp_max=90, viscosity_class="Low", shrinkage_min=0.015, shrinkage_max=0.020, density=1.31, max_flow_length_ratio=180),
        Material(name="PET Unfilled", type="Generic", family="PET", melt_temp_min=260, melt_temp_max=290, mold_temp_min=120, mold_temp_max=140, viscosity_class="Low", shrinkage_min=0.012, shrinkage_max=0.020, density=1.35, max_flow_length_ratio=180),
        Material(name="PMMA (Acrylic)", type="Generic", family="PMMA", melt_temp_min=210, melt_temp_max=250, mold_temp_min=60, mold_temp_max=90, viscosity_class="High", shrinkage_min=0.002, shrinkage_max=0.006, density=1.18, max_flow_length_ratio=120),

        # High Performance / Elastomers
        Material(name="TPE (Thermoplastic Elastomer)", type="Generic", family="TPE", melt_temp_min=170, melt_temp_max=220, mold_temp_min=20, mold_temp_max=50, viscosity_class="Medium", shrinkage_min=0.010, shrinkage_max=0.020, density=1.10, max_flow_length_ratio=150),
        Material(name="TPU (Thermoplastic Polyurethane)", type="Generic", family="TPU", melt_temp_min=190, melt_temp_max=230, mold_temp_min=20, mold_temp_max=50, viscosity_class="Medium", shrinkage_min=0.010, shrinkage_max=0.015, density=1.20, max_flow_length_ratio=150),
        Material(name="PEEK Unfilled", type="Generic", family="PEEK", melt_temp_min=360, melt_temp_max=400, mold_temp_min=160, mold_temp_max=200, viscosity_class="Medium", shrinkage_min=0.012, shrinkage_max=0.015, density=1.32, max_flow_length_ratio=120),
        Material(name="PSU (Polysulfone)", type="Generic", family="PSU", melt_temp_min=330, melt_temp_max=390, mold_temp_min=100, mold_temp_max=160, viscosity_class="High", shrinkage_min=0.007, shrinkage_max=0.008, density=1.24, max_flow_length_ratio=100),
    ]
    
    for mat in materials:
        existing = session.exec(select(Material).where(Material.name == mat.name)).first()
        if not existing:
            session.add(mat)
            print(f"Added material: {mat.name}")
    session.commit()

def create_machines(session: Session):
    machines = [
        Machine(name="80T Standard", clamp_tonnage=80, max_shot_volume=120, tie_bar_spacing_x=360, tie_bar_spacing_y=360),
        Machine(name="120T Standard", clamp_tonnage=120, max_shot_volume=210, tie_bar_spacing_x=410, tie_bar_spacing_y=410),
        Machine(name="180T Standard", clamp_tonnage=180, max_shot_volume=350, tie_bar_spacing_x=510, tie_bar_spacing_y=510),
        Machine(name="250T Standard", clamp_tonnage=250, max_shot_volume=550, tie_bar_spacing_x=610, tie_bar_spacing_y=610),
        Machine(name="350T Standard", clamp_tonnage=350, max_shot_volume=900, tie_bar_spacing_x=710, tie_bar_spacing_y=710),
    ]
    
    for mach in machines:
        existing = session.exec(select(Machine).where(Machine.name == mach.name)).first()
        if not existing:
            session.add(mach)
            print(f"Added machine: {mach.name}")
    session.commit()

def main():
    create_db_and_tables()
    with Session(engine) as session:
        create_materials(session)
        create_machines(session)

if __name__ == "__main__":
    main()
