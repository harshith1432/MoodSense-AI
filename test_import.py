import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

print("Attempting to import app_simple...")
try:
    from app_simple import app
    print("SUCCESS: app_simple imported correctly.")
except Exception as e:
    print("ERROR: Failed to import app_simple.")
    import traceback
    traceback.print_exc()
