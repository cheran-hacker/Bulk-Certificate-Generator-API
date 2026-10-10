from sqlalchemy.orm import Session
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
