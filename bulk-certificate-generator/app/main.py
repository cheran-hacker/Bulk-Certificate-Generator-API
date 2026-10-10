from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.api.v1.router import api_router
from app.core.exceptions import setup_exception_handlers
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Bulk Certificate Generator",
    description="API for bulk generating PDF certificates",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_exception_handlers(app)

app.include_router(api_router, prefix="/api/v1")
