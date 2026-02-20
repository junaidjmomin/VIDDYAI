
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

print("Testing imports...")
try:
    from services.validator import validate_pdf_content, validate_question
    print("✅ services.validator imported")
    
    # Mocking core modules to avoid full dependency load if needed, 
    # but let's try importing routers directly.
    # We might need to mock config/database if they connect on import.
    # Looking at main.py, it imports routers inside startup_event, 
    # but the routers themselves import dependencies at top level.
    # core.ingestion imports core.validator (which we replaced).
    
    from routers import ingest
    print("✅ routers.ingest imported")
    
    from routers import chat
    print("✅ routers.chat imported")
    
    print("\n🎉 ALL IMPORTS PASSED")

except ImportError as e:
    print(f"\n❌ IMPORT ERROR: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    sys.exit(1)
