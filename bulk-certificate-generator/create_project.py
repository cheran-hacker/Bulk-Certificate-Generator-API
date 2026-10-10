import os

base_dir = "C:/Users/chera/Downloads/Desktop/BULK CERTIFICATE/bulk-certificate-generator"

files = {
    "requirements.txt": """fastapi[standard]>=0.110.0
uvicorn>=0.27.0
sqlalchemy>=2.0.27
alembic>=1.13.1
psycopg2-binary>=2.9.9
pydantic>=2.6.3
pydantic-settings>=2.2.1
email-validator>=2.1.1
reportlab>=4.1.0

# Testing
pytest>=8.0.2
pytest-asyncio>=0.23.5
httpx>=0.27.0
pytest-cov>=4.1.0
""",
    ".env.example": """DATABASE_URL=postgresql://postgres:postgres@db:5432/certificates
CERTIFICATE_STORAGE_PATH=generated_certificates
MAX_RECIPIENTS_PER_JOB=1000
APP_ENV=development
LOG_LEVEL=INFO
""",
    ".gitignore": """__pycache__/
*.py[cod]
*$py.class
.env
.venv
env/
venv/
generated_certificates/
.pytest_cache/
""",
    "Dockerfile": """FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
    "docker-compose.yml": """version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/certificates
      - CERTIFICATE_STORAGE_PATH=generated_certificates
      - APP_ENV=development
    volumes:
      - .:/app
      - ./generated_certificates:/app/generated_certificates
    depends_on:
      db:
        condition: service_healthy
    command: >
      sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=certificates
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
""",
    "alembic.ini": """[alembic]
script_location = migrations
prepend_sys_path = .
version_path_separator = os

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
""",
    "Makefile": """test:\n\tpytest\n\nrun:\n\tuvicorn app.main:app --reload\n\nup:\n\tdocker-compose up --build\n""",
    "app/__init__.py": "",
    "app/main.py": """from fastapi import FastAPI
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
""",
    "app/api/__init__.py": "",
    "app/api/dependencies.py": """from typing import Generator
from app.db.session import SessionLocal

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
""",
    "app/api/v1/__init__.py": "",
    "app/api/v1/router.py": """from fastapi import APIRouter
from app.api.v1 import health, jobs, certificates

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(jobs.router, tags=["jobs"])
api_router.include_router(certificates.router, tags=["certificates"])
""",
    "app/api/v1/health.py": """from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.dependencies import get_db

router = APIRouter()

@router.get("/health")
def check_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
        
    return {
        "success": True,
        "status": "ok",
        "database": db_status
    }
""",
    "app/api/v1/jobs.py": """from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import uuid

from app.api.dependencies import get_db
from app.schemas.job import JobCreateRequest, JobResponse, JobDetailResponse, CertificateListResponse
from app.services.job_service import JobService
from app.services.processing_service import ProcessingService
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/jobs")

@router.post("", response_model=JobResponse, status_code=202)
def create_job(
    request: JobCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    job_service = JobService(db)
    job = job_service.create_job(request)
    
    # Schedule background processing
    processing_service = ProcessingService(db)
    background_tasks.add_task(processing_service.process_job_background, job.id)
    
    return JobResponse(
        success=True,
        data={
            "job_id": job.id,
            "status": job.status,
            "total_recipients": job.total_recipients,
            "message": "Certificate generation job accepted"
        }
    )

@router.get("/{job_id}", response_model=JobDetailResponse)
def get_job(job_id: uuid.UUID, db: Session = Depends(get_db)):
    job_service = JobService(db)
    job = job_service.get_job(job_id)
    if not job:
        raise NotFoundException("Job not found")
        
    return JobDetailResponse(
        success=True,
        data={
            "job_id": job.id,
            "status": job.status,
            "total_recipients": job.total_recipients,
            "pending": job.pending_count,
            "processing": job.processing_count,
            "successful": job.success_count,
            "failed": job.failed_count,
            "progress_percentage": float(job.progress_percentage),
            "created_at": job.created_at,
            "started_at": job.started_at,
            "completed_at": job.completed_at
        }
    )

@router.get("/{job_id}/certificates", response_model=CertificateListResponse)
def get_job_certificates(
    job_id: uuid.UUID,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db)
):
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 50
        
    job_service = JobService(db)
    job = job_service.get_job(job_id)
    if not job:
        raise NotFoundException("Job not found")
        
    certs, total = job_service.get_job_certificates(job_id, page, page_size)
    
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    return CertificateListResponse(
        items=certs,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages
    )
""",
    "app/api/v1/certificates.py": """from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import uuid
import os

from app.api.dependencies import get_db
from app.schemas.certificate import CertificateDetailResponse
from app.services.certificate_service import CertificateService
from app.core.exceptions import NotFoundException, InvalidStateException
from app.db.models.certificate import CertificateStatus
from app.storage.local_storage import LocalStorage

router = APIRouter(prefix="/certificates")

@router.get("/{certificate_id}", response_model=CertificateDetailResponse)
def get_certificate(certificate_id: uuid.UUID, db: Session = Depends(get_db)):
    cert_service = CertificateService(db)
    cert = cert_service.get_certificate(certificate_id)
    if not cert:
        raise NotFoundException("Certificate not found")
        
    return cert

@router.get("/{certificate_id}/download")
def download_certificate(certificate_id: uuid.UUID, db: Session = Depends(get_db)):
    cert_service = CertificateService(db)
    cert = cert_service.get_certificate(certificate_id)
    
    if not cert:
        raise NotFoundException("Certificate not found")
        
    if cert.status == CertificateStatus.PENDING or cert.status == CertificateStatus.PROCESSING:
        raise InvalidStateException("Certificate is not ready yet")
        
    if cert.status == CertificateStatus.FAILED:
        raise InvalidStateException(f"Certificate generation failed: {cert.error_message}")
        
    if not cert.file_path:
        raise NotFoundException("Certificate file not found")
        
    storage = LocalStorage()
    if not storage.exists(cert.file_path):
        raise NotFoundException("Certificate file not found on disk")
        
    abs_path = storage.get_absolute_path(cert.file_path)
    filename = f"{cert.certificate_code}.pdf"
    
    return FileResponse(
        path=abs_path,
        media_type="application/pdf",
        filename=filename
    )
""",
    "app/core/__init__.py": "",
    "app/core/config.py": """from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql://postgres:postgres@db:5432/certificates"
    certificate_storage_path: str = "generated_certificates"
    max_recipients_per_job: int = 1000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
""",
    "app/core/logging.py": """import logging
from app.core.config import settings

def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(settings.log_level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s %(name)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger
""",
    "app/core/exceptions.py": """from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)

class BaseAppException(Exception):
    def __init__(self, message: str, code: str, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundException(BaseAppException):
    def __init__(self, message: str):
        super().__init__(message, "NOT_FOUND", 404)

class ValidationException(BaseAppException):
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR", 400)
        
class InvalidStateException(BaseAppException):
    def __init__(self, message: str):
        super().__init__(message, "INVALID_STATE", 400)

def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(BaseAppException)
    async def app_exception_handler(request: Request, exc: BaseAppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message
                }
            }
        )
        
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        details = []
        for error in exc.errors():
            loc = ".".join([str(l) for l in error.get("loc", [])])
            details.append({"field": loc, "message": error.get("msg")})
            
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": details
                }
            }
        )
        
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred."
                }
            }
        )
""",
    "app/db/__init__.py": "",
    "app/db/base.py": """from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
""",
    "app/db/session.py": """from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
""",
    "app/db/models/__init__.py": """from app.db.base import Base
from app.db.models.generation_job import GenerationJob
from app.db.models.certificate import CertificateRecord
""",
    "app/db/models/generation_job.py": """import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Enum, Numeric, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_ERRORS = "COMPLETED_WITH_ERRORS"
    FAILED = "FAILED"

class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(Enum(JobStatus, name="jobstatus_enum"), default=JobStatus.PENDING, nullable=False)
    certificate_title = Column(String, nullable=False)
    event_name = Column(String, nullable=False)
    organization_name = Column(String, nullable=False)
    issue_date = Column(DateTime(timezone=True), nullable=False)
    
    total_recipients = Column(Integer, default=0, nullable=False)
    pending_count = Column(Integer, default=0, nullable=False)
    processing_count = Column(Integer, default=0, nullable=False)
    success_count = Column(Integer, default=0, nullable=False)
    failed_count = Column(Integer, default=0, nullable=False)
    progress_percentage = Column(Numeric(5, 2), default=0.0, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    certificates = relationship("CertificateRecord", back_populates="job", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_generation_jobs_status", "status"),
        Index("idx_generation_jobs_created_at", "created_at"),
    )
""",
    "app/db/models/certificate.py": """import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Enum, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class CertificateStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class CertificateRecord(Base):
    __tablename__ = "certificate_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("generation_jobs.id"), nullable=False)
    certificate_code = Column(String, unique=True, nullable=False)
    
    recipient_name = Column(String, nullable=False)
    recipient_email = Column(String, nullable=False)
    
    status = Column(Enum(CertificateStatus, name="certificatestatus_enum"), default=CertificateStatus.PENDING, nullable=False)
    
    file_path = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    error_code = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    job = relationship("GenerationJob", back_populates="certificates")

    __table_args__ = (
        Index("idx_certificate_records_job_id", "job_id"),
        Index("idx_certificate_records_status", "status"),
        Index("idx_certificate_records_code", "certificate_code"),
        Index("idx_certificate_records_email", "recipient_email"),
    )
""",
    "app/schemas/__init__.py": "",
    "app/schemas/common.py": """from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List, Any

T = TypeVar("T")

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str

class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[List[ErrorDetail]] = None

class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[ErrorResponse] = None
""",
    "app/schemas/job.py": """from pydantic import BaseModel, Field, EmailStr, model_validator
from typing import List, Optional
from datetime import date, datetime
import uuid
from app.schemas.common import ApiResponse
from app.db.models.generation_job import JobStatus
from app.db.models.certificate import CertificateStatus

class RecipientSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr

    @model_validator(mode='after')
    def strip_whitespace(self) -> 'RecipientSchema':
        self.name = self.name.strip()
        return self

class JobCreateRequest(BaseModel):
    certificate_title: str = Field(..., min_length=1, max_length=150)
    event_name: str = Field(..., min_length=1, max_length=150)
    organization_name: str = Field(..., min_length=1, max_length=150)
    issue_date: date
    recipients: List[RecipientSchema] = Field(..., min_length=1, max_length=1000)

    @model_validator(mode='after')
    def strip_whitespace(self) -> 'JobCreateRequest':
        self.certificate_title = self.certificate_title.strip()
        self.event_name = self.event_name.strip()
        self.organization_name = self.organization_name.strip()
        # handle duplicates
        seen = set()
        unique_recipients = []
        for r in self.recipients:
            if r.email.lower() not in seen:
                seen.add(r.email.lower())
                unique_recipients.append(r)
        self.recipients = unique_recipients
        if not self.recipients:
            raise ValueError("Recipients list cannot be empty after deduplication")
        return self

class JobCreateData(BaseModel):
    job_id: uuid.UUID
    status: JobStatus
    total_recipients: int
    message: str

class JobResponse(ApiResponse[JobCreateData]):
    pass

class JobDetailData(BaseModel):
    job_id: uuid.UUID
    status: JobStatus
    total_recipients: int
    pending: int
    processing: int
    successful: int
    failed: int
    progress_percentage: float
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class JobDetailResponse(ApiResponse[JobDetailData]):
    pass

class CertificateItem(BaseModel):
    id: uuid.UUID
    certificate_code: str
    recipient_name: str
    recipient_email: str
    status: CertificateStatus
    file_availability: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class CertificateListResponse(BaseModel):
    items: List[CertificateItem]
    page: int
    page_size: int
    total: int
    total_pages: int
""",
    "app/schemas/certificate.py": """from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
from app.db.models.certificate import CertificateStatus

class CertificateDetailResponse(BaseModel):
    certificate_id: uuid.UUID
    certificate_code: str
    job_id: uuid.UUID
    recipient_name: str
    recipient_email: str
    status: CertificateStatus
    file_availability: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
""",
    "app/repositories/__init__.py": "",
    "app/repositories/job_repository.py": """from sqlalchemy.orm import Session
from sqlalchemy import select
import uuid
from app.db.models.generation_job import GenerationJob

class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, job: GenerationJob) -> GenerationJob:
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get(self, job_id: uuid.UUID) -> GenerationJob | None:
        return self.db.execute(select(GenerationJob).where(GenerationJob.id == job_id)).scalar_one_or_none()

    def update(self, job: GenerationJob) -> GenerationJob:
        self.db.commit()
        self.db.refresh(job)
        return job
""",
    "app/repositories/certificate_repository.py": """from sqlalchemy.orm import Session
from sqlalchemy import select, update
import uuid
from typing import List
from app.db.models.certificate import CertificateRecord, CertificateStatus

class CertificateRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_bulk(self, certificates: List[CertificateRecord]):
        self.db.add_all(certificates)
        self.db.commit()

    def get(self, certificate_id: uuid.UUID) -> CertificateRecord | None:
        return self.db.execute(select(CertificateRecord).where(CertificateRecord.id == certificate_id)).scalar_one_or_none()

    def get_by_job_id(self, job_id: uuid.UUID, page: int, page_size: int) -> tuple[List[CertificateRecord], int]:
        offset = (page - 1) * page_size
        
        # Get total
        total = self.db.query(CertificateRecord).filter(CertificateRecord.job_id == job_id).count()
        
        # Get paginated
        certs = self.db.execute(
            select(CertificateRecord)
            .where(CertificateRecord.job_id == job_id)
            .order_by(CertificateRecord.created_at)
            .offset(offset)
            .limit(page_size)
        ).scalars().all()
        
        return certs, total

    def update(self, certificate: CertificateRecord) -> CertificateRecord:
        self.db.commit()
        self.db.refresh(certificate)
        return certificate
""",
    "app/services/__init__.py": "",
    "app/services/job_service.py": """from sqlalchemy.orm import Session
import uuid
import secrets
from datetime import datetime, timezone
from app.repositories.job_repository import JobRepository
from app.repositories.certificate_repository import CertificateRepository
from app.db.models.generation_job import GenerationJob, JobStatus
from app.db.models.certificate import CertificateRecord, CertificateStatus
from app.schemas.job import JobCreateRequest
from app.core.logging import get_logger

logger = get_logger(__name__)

class JobService:
    def __init__(self, db: Session):
        self.db = db
        self.job_repo = JobRepository(db)
        self.cert_repo = CertificateRepository(db)

    def generate_cert_code(self, year: int) -> str:
        random_part = secrets.token_hex(4).upper()
        return f"CERT-{year}-{random_part}"

    def create_job(self, request: JobCreateRequest) -> GenerationJob:
        job_id = uuid.uuid4()
        
        total_recipients = len(request.recipients)
        job = GenerationJob(
            id=job_id,
            certificate_title=request.certificate_title,
            event_name=request.event_name,
            organization_name=request.organization_name,
            issue_date=datetime.combine(request.issue_date, datetime.min.time()).replace(tzinfo=timezone.utc),
            total_recipients=total_recipients,
            pending_count=total_recipients,
            status=JobStatus.PENDING
        )
        
        job = self.job_repo.create(job)
        
        year = request.issue_date.year
        certificates = []
        for r in request.recipients:
            cert_code = self.generate_cert_code(year)
            cert = CertificateRecord(
                id=uuid.uuid4(),
                job_id=job.id,
                certificate_code=cert_code,
                recipient_name=r.name,
                recipient_email=r.email.lower()
            )
            certificates.append(cert)
            
        self.cert_repo.create_bulk(certificates)
        logger.info(f"job_created job_id={job.id} recipients={total_recipients}")
        return job

    def get_job(self, job_id: uuid.UUID) -> GenerationJob | None:
        return self.job_repo.get(job_id)

    def get_job_certificates(self, job_id: uuid.UUID, page: int, page_size: int):
        certs, total = self.cert_repo.get_by_job_id(job_id, page, page_size)
        items = []
        for c in certs:
            items.append({
                "id": c.id,
                "certificate_code": c.certificate_code,
                "recipient_name": c.recipient_name,
                "recipient_email": c.recipient_email,
                "status": c.status,
                "file_availability": c.file_path is not None,
                "error_code": c.error_code,
                "error_message": c.error_message,
                "created_at": c.created_at,
                "completed_at": c.completed_at
            })
        return items, total
""",
    "app/services/certificate_service.py": """from sqlalchemy.orm import Session
import uuid
from app.repositories.certificate_repository import CertificateRepository
from app.schemas.certificate import CertificateDetailResponse
from app.db.models.certificate import CertificateStatus

class CertificateService:
    def __init__(self, db: Session):
        self.db = db
        self.cert_repo = CertificateRepository(db)

    def get_certificate(self, certificate_id: uuid.UUID):
        cert = self.cert_repo.get(certificate_id)
        if not cert:
            return None
            
        return CertificateDetailResponse(
            certificate_id=cert.id,
            certificate_code=cert.certificate_code,
            job_id=cert.job_id,
            recipient_name=cert.recipient_name,
            recipient_email=cert.recipient_email,
            status=cert.status,
            file_availability=cert.file_path is not None,
            error_code=cert.error_code,
            error_message=cert.error_message,
            created_at=cert.created_at,
            started_at=cert.started_at,
            completed_at=cert.completed_at
        )
""",
    "app/services/processing_service.py": """import uuid
from datetime import datetime, timezone
import traceback
from app.db.session import SessionLocal
from app.db.models.generation_job import JobStatus, GenerationJob
from app.db.models.certificate import CertificateStatus, CertificateRecord
from app.workers.certificate_worker import generate_certificate_for_record
from app.core.logging import get_logger
from sqlalchemy.orm import Session
from sqlalchemy import select

logger = get_logger(__name__)

class ProcessingService:
    def __init__(self, db: Session):
        self.db = db

    def process_job_background(self, job_id: uuid.UUID):
        db = SessionLocal()
        try:
            job = db.execute(select(GenerationJob).where(GenerationJob.id == job_id)).scalar_one_or_none()
            if not job or job.status != JobStatus.PENDING:
                logger.warning(f"job_not_pending_or_missing job_id={job_id}")
                return

            job.status = JobStatus.PROCESSING
            job.started_at = datetime.now(timezone.utc)
            db.commit()
            logger.info(f"job_started job_id={job_id}")

            certs = db.execute(select(CertificateRecord).where(CertificateRecord.job_id == job_id)).scalars().all()
            
            for cert in certs:
                if cert.status != CertificateStatus.PENDING:
                    continue
                self.process_single_certificate(cert.id)
                self.update_job_counters(job_id)
            
            self.finalize_job(job_id)
            
        except Exception as e:
            logger.error(f"job_processing_failed job_id={job_id} error={str(e)}")
            job = db.execute(select(GenerationJob).where(GenerationJob.id == job_id)).scalar_one_or_none()
            if job:
                job.status = JobStatus.FAILED
                job.error_message = str(e)
                db.commit()
        finally:
            db.close()

    def process_single_certificate(self, cert_id: uuid.UUID):
        db = SessionLocal()
        try:
            cert = db.execute(select(CertificateRecord).where(CertificateRecord.id == cert_id)).scalar_one_or_none()
            if not cert:
                return
                
            cert.status = CertificateStatus.PROCESSING
            cert.started_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(cert)
            
            job = db.execute(select(GenerationJob).where(GenerationJob.id == cert.job_id)).scalar_one_or_none()
            
            try:
                logger.info(f"certificate_started certificate_id={cert.id}")
                
                # Introduce a fake failure case for testing the failure isolation
                if "INVALID RECIPIENT" in cert.recipient_name.upper():
                    raise ValueError("Simulated PDF generation error for invalid recipient")
                
                file_path, file_size = generate_certificate_for_record(
                    recipient_name=cert.recipient_name,
                    certificate_title=job.certificate_title,
                    event_name=job.event_name,
                    organization_name=job.organization_name,
                    issue_date=job.issue_date,
                    certificate_code=cert.certificate_code
                )
                
                cert.status = CertificateStatus.COMPLETED
                cert.file_path = file_path
                cert.file_size = file_size
                cert.completed_at = datetime.now(timezone.utc)
                db.commit()
                logger.info(f"certificate_completed certificate_id={cert.id}")
            except Exception as e:
                db.rollback()
                cert = db.execute(select(CertificateRecord).where(CertificateRecord.id == cert_id)).scalar_one_or_none()
                cert.status = CertificateStatus.FAILED
                cert.error_code = "PDF_GENERATION_ERROR"
                cert.error_message = str(e)
                cert.completed_at = datetime.now(timezone.utc)
                db.commit()
                logger.error(f"certificate_failed certificate_id={cert.id} error_code=PDF_GENERATION_ERROR error={str(e)}")
        finally:
            db.close()

    def update_job_counters(self, job_id: uuid.UUID):
        db = SessionLocal()
        try:
            job = db.execute(select(GenerationJob).where(GenerationJob.id == job_id)).scalar_one_or_none()
            if not job:
                return
                
            pending = db.query(CertificateRecord).filter(CertificateRecord.job_id == job_id, CertificateRecord.status == CertificateStatus.PENDING).count()
            processing = db.query(CertificateRecord).filter(CertificateRecord.job_id == job_id, CertificateRecord.status == CertificateStatus.PROCESSING).count()
            success = db.query(CertificateRecord).filter(CertificateRecord.job_id == job_id, CertificateRecord.status == CertificateStatus.COMPLETED).count()
            failed = db.query(CertificateRecord).filter(CertificateRecord.job_id == job_id, CertificateRecord.status == CertificateStatus.FAILED).count()
            
            job.pending_count = pending
            job.processing_count = processing
            job.success_count = success
            job.failed_count = failed
            
            completed_count = success + failed
            if job.total_recipients > 0:
                job.progress_percentage = round((completed_count / job.total_recipients) * 100, 2)
                
            db.commit()
        finally:
            db.close()
            
    def finalize_job(self, job_id: uuid.UUID):
        db = SessionLocal()
        try:
            job = db.execute(select(GenerationJob).where(GenerationJob.id == job_id)).scalar_one_or_none()
            if not job:
                return
                
            if job.failed_count > 0:
                job.status = JobStatus.COMPLETED_WITH_ERRORS
            else:
                job.status = JobStatus.COMPLETED
                
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
            logger.info(f"job_completed job_id={job.id} status={job.status.value}")
        finally:
            db.close()
""",
    "app/workers/__init__.py": "",
    "app/workers/certificate_worker.py": """from datetime import datetime
from app.templates.certificate_template import generate_pdf
from app.storage.local_storage import LocalStorage

def generate_certificate_for_record(
    recipient_name: str,
    certificate_title: str,
    event_name: str,
    organization_name: str,
    issue_date: datetime,
    certificate_code: str
) -> tuple[str, int]:
    
    storage = LocalStorage()
    
    filename = f"{certificate_code}.pdf"
    
    pdf_bytes = generate_pdf(
        recipient_name=recipient_name,
        certificate_title=certificate_title,
        event_name=event_name,
        organization_name=organization_name,
        issue_date=issue_date.strftime("%B %d, %Y"),
        certificate_code=certificate_code
    )
    
    file_path = storage.save(filename, pdf_bytes)
    file_size = len(pdf_bytes)
    
    return file_path, file_size
""",
    "app/templates/__init__.py": "",
    "app/templates/certificate_template.py": """import io
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def generate_pdf(
    recipient_name: str,
    certificate_title: str,
    event_name: str,
    organization_name: str,
    issue_date: str,
    certificate_code: str
) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    c.setStrokeColor(colors.HexColor("#2c3e50"))
    c.setLineWidth(10)
    c.rect(30, 30, width - 60, height - 60)

    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(colors.HexColor("#2c3e50"))
    c.drawCentredString(width / 2, height - 120, organization_name)

    c.setFont("Helvetica", 36)
    c.setFillColor(colors.HexColor("#e74c3c"))
    c.drawCentredString(width / 2, height - 200, certificate_title)

    c.setFont("Helvetica", 16)
    c.setFillColor(colors.HexColor("#7f8c8d"))
    c.drawCentredString(width / 2, height - 260, "This is proudly presented to")

    c.setFont("Helvetica-Bold", 42)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height - 330, recipient_name)

    c.setFont("Helvetica", 16)
    c.setFillColor(colors.HexColor("#7f8c8d"))
    c.drawCentredString(width / 2, height - 390, f"for successful participation in {event_name}")

    c.setFont("Helvetica", 14)
    c.setFillColor(colors.black)
    c.drawString(120, 100, f"Date: {issue_date}")

    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#95a5a6"))
    c.drawRightString(width - 120, 100, f"Certificate Code: {certificate_code}")

    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
""",
    "app/storage/__init__.py": "",
    "app/storage/local_storage.py": """import os
from app.core.config import settings

class LocalStorage:
    def __init__(self):
        self.base_path = settings.certificate_storage_path
        os.makedirs(self.base_path, exist_ok=True)

    def get_absolute_path(self, relative_path: str) -> str:
        return os.path.abspath(os.path.join(self.base_path, relative_path))

    def save(self, filename: str, data: bytes) -> str:
        safe_filename = os.path.basename(filename)
        path = os.path.join(self.base_path, safe_filename)
        with open(path, 'wb') as f:
            f.write(data)
        return safe_filename

    def exists(self, filename: str) -> bool:
        safe_filename = os.path.basename(filename)
        path = os.path.join(self.base_path, safe_filename)
        return os.path.exists(path)
"""
}

# Add test files

files["tests/conftest.py"] = """import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

from app.main import app
from app.db.base import Base
from app.api.dependencies import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function", autouse=True)
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client():
    with TestClient(app) as c:
        yield c
        
@pytest.fixture(autouse=True)
def set_env():
    os.environ["CERTIFICATE_STORAGE_PATH"] = "test_certificates"
    yield
    import shutil
    if os.path.exists("test_certificates"):
        shutil.rmtree("test_certificates")
"""

files["tests/test_health.py"] = """def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["success"] == True
"""

files["tests/test_validation.py"] = """def test_create_job_invalid_email(client):
    data = {
        "certificate_title": "Test",
        "event_name": "Event",
        "organization_name": "Org",
        "issue_date": "2026-10-10",
        "recipients": [
            {"name": "Cheran", "email": "invalid_email"}
        ]
    }
    response = client.post("/api/v1/jobs", json=data)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"

def test_create_job_missing_fields(client):
    data = {
        "recipients": [{"name": "Cheran", "email": "cheran@test.com"}]
    }
    response = client.post("/api/v1/jobs", json=data)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
"""

files["tests/test_job_creation.py"] = """import uuid

def test_create_job_success(client):
    data = {
        "certificate_title": "Test",
        "event_name": "Event",
        "organization_name": "Org",
        "issue_date": "2026-10-10",
        "recipients": [
            {"name": "Cheran", "email": "cheran@test.com"},
            {"name": "Ezhil", "email": "ezhil@test.com"}
        ]
    }
    response = client.post("/api/v1/jobs", json=data)
    assert response.status_code == 202
    res_data = response.json()
    assert res_data["success"] == True
    assert "job_id" in res_data["data"]
    assert res_data["data"]["status"] == "PENDING"
    assert res_data["data"]["total_recipients"] == 2
"""

files["tests/test_processing.py"] = """from app.services.processing_service import ProcessingService
from app.db.models.generation_job import JobStatus
from app.db.models.certificate import CertificateStatus
import os

def test_job_processing(client, db_session):
    data = {
        "certificate_title": "Test Certificate",
        "event_name": "Test Event",
        "organization_name": "Test Org",
        "issue_date": "2026-10-10",
        "recipients": [
            {"name": "Cheran S", "email": "cheran@test.com"},
            {"name": "Ezhil", "email": "ezhil@test.com"}
        ]
    }
    response = client.post("/api/v1/jobs", json=data)
    job_id = response.json()["data"]["job_id"]
    
    processor = ProcessingService(db_session)
    processor.process_job_background(job_id)
    
    job_resp = client.get(f"/api/v1/jobs/{job_id}")
    job_data = job_resp.json()["data"]
    assert job_data["status"] == "COMPLETED"
    assert job_data["successful"] == 2
    assert job_data["failed"] == 0
    assert job_data["progress_percentage"] == 100.0
"""

files["tests/test_failure_isolation.py"] = """from app.services.processing_service import ProcessingService
from app.db.models.generation_job import JobStatus

def test_failure_isolation(client, db_session):
    data = {
        "certificate_title": "Test Certificate",
        "event_name": "Test Event",
        "organization_name": "Test Org",
        "issue_date": "2026-10-10",
        "recipients": [
            {"name": "Valid Name 1", "email": "user1@test.com"},
            {"name": "Invalid Recipient", "email": "invalid@test.com"},
            {"name": "Valid Name 2", "email": "user2@test.com"}
        ]
    }
    response = client.post("/api/v1/jobs", json=data)
    job_id = response.json()["data"]["job_id"]
    
    processor = ProcessingService(db_session)
    processor.process_job_background(job_id)
    
    job_resp = client.get(f"/api/v1/jobs/{job_id}")
    job_data = job_resp.json()["data"]
    assert job_data["status"] == "COMPLETED_WITH_ERRORS"
    assert job_data["successful"] == 2
    assert job_data["failed"] == 1
    assert job_data["progress_percentage"] == 100.0
    
    cert_resp = client.get(f"/api/v1/jobs/{job_id}/certificates")
    certs = cert_resp.json()["items"]
    
    success_count = sum(1 for c in certs if c["status"] == "COMPLETED")
    fail_count = sum(1 for c in certs if c["status"] == "FAILED")
    
    assert success_count == 2
    assert fail_count == 1
    
    failed_cert = next(c for c in certs if c["status"] == "FAILED")
    assert failed_cert["error_code"] == "PDF_GENERATION_ERROR"
"""

for path, content in files.items():
    full_path = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Project generated successfully.")
