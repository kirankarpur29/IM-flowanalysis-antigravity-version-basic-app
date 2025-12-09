from database import supabase
import sys

def test_connection():
    print("Testing Supabase Connection...")
    try:
        # Fetch 5 materials
        response = supabase.table("materials").select("*").limit(5).execute()
        
        # Check for data
        data = response.data
        if data:
            print(f"[SUCCESS] Connected! Found {len(data)} materials.")
            print("Sample:", data[0]['name'])
            return True
        else:
            print("[WARNING] Connected, but 'materials' table is empty. Did you run the SQL seed?")
            return False
            
    except Exception as e:
        print(f"[ERROR] Connection Failed: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
