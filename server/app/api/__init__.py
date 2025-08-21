from fastapi import APIRouter

from app.api.v1 import routers as v1_routers

api_router = APIRouter()


for router, tag in v1_routers:
    api_router.include_router(router, prefix="/api/v1", tags=[tag])
