from sqlalchemy.orm import Session
import uuid
from app.repositories.certificate_repository import CertificateRepository
from app.schemas.certificate import CertificateDetailResponse
from app.db.models.certificate import CertificateStatus

class CertificateService:
    def __init__(self, db: Session):
        self.db = db
        self.cert_repo = CertificateRepository(db)

    def get_all_certificates(self, limit: int = 50, offset: int = 0):
        from app.db.models.certificate import CertificateRecord
        return self.db.query(CertificateRecord).order_by(CertificateRecord.created_at.desc()).offset(offset).limit(limit).all()

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
