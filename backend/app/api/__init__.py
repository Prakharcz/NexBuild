from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.ingestion import router as ingestion_router
from app.api.transactions import router as transactions_router
from app.api.analytics import router as analytics_router
from app.api.forecasting import router as forecasting_router
from app.api.risk import router as risk_router
from app.api.goals import router as goals_router
from app.api.recommendations import router as recommendations_router

api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(ingestion_router)
api_router.include_router(transactions_router)
api_router.include_router(analytics_router)
api_router.include_router(forecasting_router)
api_router.include_router(risk_router)
api_router.include_router(goals_router)
api_router.include_router(recommendations_router)
