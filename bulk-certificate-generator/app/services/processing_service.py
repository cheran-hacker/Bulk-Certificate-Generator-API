import uuid
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
