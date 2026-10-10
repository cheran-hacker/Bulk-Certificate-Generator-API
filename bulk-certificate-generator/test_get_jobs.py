import sys
import asyncio
sys.path.append("C:/Users/chera/Downloads/Desktop/BULK CERTIFICATE/bulk-certificate-generator")
from app.db.session import SessionLocal
from app.api.v1.jobs import get_jobs

db = SessionLocal()
try:
    response = get_jobs(skip=0, limit=100, db=db)
    print("SUCCESS")
    print(response)
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()
