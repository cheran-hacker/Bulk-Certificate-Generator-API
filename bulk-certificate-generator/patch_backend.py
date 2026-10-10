import os

# Update JobService
with open('app/services/job_service.py', 'r') as f:
    content = f.read()

if 'def get_all_jobs' not in content:
    content = content.replace(
        'def get_job(self, job_id: uuid.UUID) -> Optional[GenerationJob]:',
        'def get_all_jobs(self, limit: int = 50, offset: int = 0):\n        return self.db.query(GenerationJob).order_by(GenerationJob.created_at.desc()).offset(offset).limit(limit).all()\n\n    def get_job(self, job_id: uuid.UUID) -> Optional[GenerationJob]:'
    )
    with open('app/services/job_service.py', 'w') as f:
        f.write(content)

# Update schemas
with open('app/schemas/job.py', 'r') as f:
    schemas = f.read()

if 'JobListResponse' not in schemas:
    schema_code = '''

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
'''
    schemas += schema_code
    with open('app/schemas/job.py', 'w') as f:
        f.write(schemas)

# Update router
with open('app/api/v1/jobs.py', 'r') as f:
    router_content = f.read()

if 'def get_jobs' not in router_content:
    router_content = router_content.replace(
        'from app.schemas.job import JobCreateRequest, JobResponse, JobDetailResponse, CertificateListResponse',
        'from app.schemas.job import JobCreateRequest, JobResponse, JobDetailResponse, CertificateListResponse, JobListResponse'
    )
    
    endpoint_code = '''
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

@router.get("/{job_id}"'''
    
    router_content = router_content.replace('@router.get("/{job_id}"', endpoint_code)
    
    with open('app/api/v1/jobs.py', 'w') as f:
        f.write(router_content)
print('Backend updated successfully')
