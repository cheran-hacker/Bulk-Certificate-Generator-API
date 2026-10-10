from sqlalchemy.orm import Session
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

    def get_all_jobs(self, limit: int = 50, offset: int = 0):
        return self.db.query(GenerationJob).order_by(GenerationJob.created_at.desc()).offset(offset).limit(limit).all()

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
