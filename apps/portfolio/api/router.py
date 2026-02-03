from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/api", tags=["api"])

@router.get("/healthz")
async def healthz():
    return {"status": "OK", "code": 200, "datetime": datetime.now().isoformat()}
