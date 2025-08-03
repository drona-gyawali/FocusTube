from fastapi import APIRouter
from app.config.logger import get_logger

logger = get_logger("[api/v1/info]")

router = APIRouter()

@router.get("/info")
def get_info():
    logger.info("INFO: API is live")
    return {"version": "v1", "info": "This is v1"}
