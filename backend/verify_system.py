import sys
import subprocess
import importlib.util
import os

def check_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, result.stderr.strip()
    except Exception as e:
        return False, str(e)

def check_import(module_name):
    if importlib.util.find_spec(module_name) is not None:
        try:
            module = __import__(module_name)
            return True, f"Installed ({module.__file__})"
        except Exception as e:
            return False, f"Import failed: {e}"
    return False, "Not installed"

def check_weasyprint_gtk():
    try:
        import weasyprint
        return True, "WeasyPrint loaded successfully"
    except OSError as e:
        if "cairo" in str(e).lower() or "pango" in str(e).lower() or "dlopen" in str(e).lower():
            return False, "GTK3 runtime missing (Required for PDF generation)"
        return False, str(e)
    except Exception as e:
        return False, str(e)

def check_gmsh():
    try:
        import gmsh
        gmsh.initialize()
        gmsh.finalize()
        return True, "Gmsh initialized successfully"
    except Exception as e:
        return False, f"Gmsh failed: {e}"

print("=== System Verification Report ===")

# 1. Core Runtimes
print("\n[Core Runtimes]")
py_ver = sys.version.split()[0]
print(f"Python: {py_ver} (OK)")

node_ok, node_ver = check_command("node --version")
print(f"Node.js: {'OK' if node_ok else 'MISSING'} - {node_ver}")

npm_ok, npm_ver = check_command("npm --version")
print(f"npm: {'OK' if npm_ok else 'MISSING'} - {npm_ver}")

# 2. Python Packages
print("\n[Python Packages]")
packages = ["fastapi", "uvicorn", "numpy", "scipy", "trimesh", "sqlmodel"]
for pkg in packages:
    ok, msg = check_import(pkg)
    print(f"{pkg}: {'OK' if ok else 'MISSING'} - {msg}")

# 3. Critical External Dependencies
print("\n[Critical External Dependencies]")

# Gmsh (for STP conversion)
gmsh_ok, gmsh_msg = check_gmsh()
print(f"Gmsh (STP Support): {'OK' if gmsh_ok else 'FAIL'} - {gmsh_msg}")

# WeasyPrint (for PDF Reports)
weasy_ok, weasy_msg = check_weasyprint_gtk()
print(f"WeasyPrint (PDF Support): {'OK' if weasy_ok else 'FAIL'} - {weasy_msg}")

print("\n=== End Report ===")
