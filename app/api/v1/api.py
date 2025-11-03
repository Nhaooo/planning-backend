from fastapi import APIRouter
from app.api.v1.endpoints import health, employees, weeks, legend, auth, backup, simple_planning

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(employees.router, prefix="/employees", tags=["employees"])
api_router.include_router(weeks.router, prefix="/weeks", tags=["weeks"])
api_router.include_router(simple_planning.router, prefix="/planning", tags=["simple-planning"])
api_router.include_router(legend.router, prefix="/legend", tags=["legend"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(backup.router, prefix="/backup", tags=["backup"])