from pydantic import BaseModel, Field, EmailStr, model_validator
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


class JobListItem(BaseModel):
    id: uuid.UUID
    status: str
    total_recipients: int
    success_count: int
    failed_count: int
    progress_percentage: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class JobListResponse(BaseModel):
    items: List[JobListItem]
    total: int
