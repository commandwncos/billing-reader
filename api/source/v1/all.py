from fastapi import APIRouter
from api.source.v1.routes import billing


API_ROUTER = APIRouter()
API_ROUTER.include_router(billing.router, prefix='/api/v1/billing', tags=['Billing Reader'])
