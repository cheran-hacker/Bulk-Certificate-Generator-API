import os

router_path = 'app/api/v1/jobs.py'
with open(router_path, 'r') as f:
    router_content = f.read()

if '@router.get("/{job_id}/download-zip"' not in router_content:
    imports_to_add = "import io\nimport zipfile\nfrom fastapi.responses import StreamingResponse\nfrom app.storage.local_storage import LocalStorage\n"
    
    # We will just insert it at the top after standard imports
    router_content = router_content.replace('from fastapi import APIRouter', imports_to_add + 'from fastapi import APIRouter')
    
    zip_endpoint = '''
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
'''
    
    router_content += zip_endpoint
    with open(router_path, 'w') as f:
        f.write(router_content)

print("ZIP endpoint added")
