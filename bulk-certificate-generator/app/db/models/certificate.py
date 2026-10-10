import uuid
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
