import uuid
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
