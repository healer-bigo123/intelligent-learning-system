import sys
import traceback

try:
    print("Python:", sys.version)
    print("Step 1: import httpx...")
    import httpx
    print("  OK")
    
    print("Step 2: import video_search...")
    from app.core.video_search import video_match_service
    print("  OK")
    
    print("Step 3: import study_materials endpoint...")
    from app.api.v1.endpoints.study_materials import router
    print("  OK")
    
    print("Step 4: import main...")
    from main import app
    print("  OK")
    
    print("ALL IMPORTS SUCCESSFUL")
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
