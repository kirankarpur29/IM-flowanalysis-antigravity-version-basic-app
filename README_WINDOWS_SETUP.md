# Windows Setup Requirements

## Critical Missing Dependency: GTK3 Runtime
Your system is missing the **GTK3 Runtime**, which is required for generating PDF reports (WeasyPrint). Without this, the "Export PDF" feature will fail.

### How to Install
1.  **Download the Installer:**
    *   Go to: [https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases)
    *   Download the latest `.exe` (e.g., `gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe`).

2.  **Run the Installer:**
    *   Double-click the downloaded file.
    *   **IMPORTANT:** During installation, ensure the option **"Set up PATH environment variable"** is CHECKED. This is crucial.

3.  **Restart Terminals:**
    *   After installation, you **MUST** close and reopen your VS Code / Terminal windows for the changes to take effect.
    *   Restart the backend: `.\venv\Scripts\uvicorn backend.main:app --reload --port 8000`

## Verification
After installing, the system check should pass, and PDF generation will work.

## Other Components
- **Python & Node.js:** ✅ Installed and correct versions.
- **Gmsh (STP Support):** ✅ Installed and working.
- **3D Graphics:** ✅ WebGL is handled by your browser (Chrome/Edge).
