import os

cert_service_path = 'app/services/certificate_service.py'
with open(cert_service_path, 'r') as f:
    cert_service = f.read()

if 'def get_all_certificates(' not in cert_service:
    cert_service = cert_service.replace(
        'def get_certificate(self, certificate_id: uuid.UUID) -> CertificateRecord | None:',
        'def get_all_certificates(self, limit: int = 50, offset: int = 0):\n        return self.db.query(CertificateRecord).order_by(CertificateRecord.created_at.desc()).offset(offset).limit(limit).all()\n\n    def get_certificate(self, certificate_id: uuid.UUID) -> CertificateRecord | None:'
    )
    with open(cert_service_path, 'w') as f:
        f.write(cert_service)

cert_router_path = 'app/api/v1/certificates.py'
with open(cert_router_path, 'r') as f:
    cert_router = f.read()

if '@router.get("", response_model=' not in cert_router:
    # Need to import CertificateListResponse
    cert_router = cert_router.replace(
        'from app.schemas.certificate import CertificateDetailResponse',
        'from app.schemas.certificate import CertificateDetailResponse\nfrom app.schemas.job import CertificateListResponse'
    )
    
    endpoint = '''
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

@router.get("/{certificate_id}", response_model=CertificateDetailResponse)'''
    
    cert_router = cert_router.replace('@router.get("/{certificate_id}", response_model=CertificateDetailResponse)', endpoint)
    with open(cert_router_path, 'w') as f:
        f.write(cert_router)

print("Certificates endpoint added")
