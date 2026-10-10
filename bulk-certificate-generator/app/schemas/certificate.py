from pydantic import BaseModel
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
