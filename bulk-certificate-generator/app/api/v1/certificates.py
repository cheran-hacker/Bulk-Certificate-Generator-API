from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import uuid
import os

from app.api.dependencies import get_db
from app.schemas.certificate import CertificateDetailResponse
from app.schemas.job import CertificateListResponse
from app.services.certificate_service import CertificateService
from app.core.exceptions import NotFoundException, InvalidStateException
from app.db.models.certificate import CertificateStatus
from app.storage.local_storage import LocalStorage

router = APIRouter(prefix="/certificates")


@router.get("", response_model=CertificateListResponse)
def get_all_certificates(page: int = 1, page_size: int = 50, db: Session = Depends(get_db)):
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 50
    offset = (page - 1) * page_size
    
    cert_service = CertificateService(db)
    certs = cert_service.get_all_certificates(limit=page_size, offset=offset)
    
    from app.db.models.certificate import CertificateRecord
    total = db.query(CertificateRecord).count()
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    items = []
    for c in certs:
        items.append({
            "id": c.id,
            "certificate_code": c.certificate_code,
            "recipient_name": c.recipient_name,
            "recipient_email": c.recipient_email,
            "status": c.status.name if hasattr(c.status, 'name') else c.status,
            "file_availability": c.file_path is not None,
            "error_code": c.error_code,
            "error_message": c.error_message,
            "created_at": c.created_at,
            "completed_at": c.completed_at
        })
        
    return CertificateListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages
    )

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
