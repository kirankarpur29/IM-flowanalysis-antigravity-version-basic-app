from backend.models import Material
print("Material imported successfully")
try:
    m = Material(name="Test", type="Generic", family="ABS", melt_temp_min=200, melt_temp_max=240, mold_temp_min=40, mold_temp_max=80, viscosity_class="Medium", shrinkage_min=0.004, shrinkage_max=0.007, density=1.04)
    print("Material instantiated:", m)
except Exception as e:
    print("Error:", e)
