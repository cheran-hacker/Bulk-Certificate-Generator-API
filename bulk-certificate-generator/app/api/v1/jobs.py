import io
import zipfile
from fastapi.responses import StreamingResponse
from app.storage.local_storage import LocalStorage
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import uuid

from app.api.dependencies import get_db
from app.schemas.job import JobCreateRequest, JobResponse, JobDetailResponse, CertificateListResponse, JobListResponse
from app.services.job_service import JobService
from app.services.processing_service import ProcessingService
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/jobs")

@router.post("", response_model=JobResponse, status_code=202)
def create_job(
    request: JobCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    job_service = JobService(db)
    job = job_service.create_job(request)
    
    # Schedule background processing
    processing_service = ProcessingService(db)
    background_tasks.add_task(processing_service.process_job_background, job.id)
    
    return JobResponse(
        success=True,
        data={
            "job_id": job.id,
            "status": job.status,
            "total_recipients": job.total_recipients,
            "message": "Certificate generation job accepted"
        }
    )


@router.get("", response_model=JobListResponse)
def get_jobs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    from app.db.models.generation_job import GenerationJob
    job_service = JobService(db)
    jobs = job_service.get_all_jobs(limit=limit, offset=skip)
    total = db.query(GenerationJob).count()
    return JobListResponse(items=[
        {
            "id": j.id,
            "status": j.status.name if hasattr(j.status, 'name') else j.status,
            "total_recipients": j.total_recipients,
            "success_count": j.success_count,
            "failed_count": j.failed_count,
            "progress_percentage": float(j.progress_percentage),
            "created_at": j.created_at
        } for j in jobs
    ], total=total)

@router.get("/{job_id}", response_model=JobDetailResponse)
def get_job(job_id: uuid.UUID, db: Session = Depends(get_db)):
    job_service = JobService(db)
    job = job_service.get_job(job_id)
    if not job:
        raise NotFoundException("Job not found")
        
    return JobDetailResponse(
        success=True,
        data={
            "job_id": job.id,
            "status": job.status,
            "total_recipients": job.total_recipients,
            "pending": job.pending_count,
            "processing": job.processing_count,
            "successful": job.success_count,
            "failed": job.failed_count,
            "progress_percentage": float(job.progress_percentage),
            "created_at": job.created_at,
            "started_at": job.started_at,
            "completed_at": job.completed_at
        }
    )

@router.get("/{job_id}/certificates", response_model=CertificateListResponse)
def get_job_certificates(
    job_id: uuid.UUID,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db)
):
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 50
        
    job_service = JobService(db)
    job = job_service.get_job(job_id)
    if not job:
        raise NotFoundException("Job not found")
        
    certs, total = job_service.get_job_certificates(job_id, page, page_size)
    
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    return CertificateListResponse(
        items=certs,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages
    )

@router.get("/{job_id}/download-zip")
def download_job_zip(job_id: uuid.UUID, db: Session = Depends(get_db)):
    job_service = JobService(db)
    job = job_service.get_job(job_id)
    if not job:
        raise NotFoundException("Job not found")
        
    certs, _ = job_service.get_job_certificates(job_id, 1, 10000)
    
    storage = LocalStorage()
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        count = 0
        for c in certs:
            if c["status"].name == "COMPLETED" or c["status"] == "COMPLETED":
                # Need the actual model or just lookup path
                # To keep it simple, we just read from the local storage
                # Since certs from get_job_certificates doesn't have file_path, we fetch it via cert repo
                cert_record = job_service.cert_repo.get(c["id"])
                if cert_record and cert_record.file_path and storage.exists(cert_record.file_path):
                    abs_path = storage.get_absolute_path(cert_record.file_path)
                    filename = f"{cert_record.recipient_name.replace(' ', '_')}_{cert_record.certificate_code}.pdf"
                    zip_file.write(abs_path, arcname=filename)
                    count += 1
                    
        if count == 0:
            raise NotFoundException("No generated certificates found for this job")
            
    zip_buffer.seek(0)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename=Job_{str(job_id)[:8]}_Certificates.zip"}
    )
