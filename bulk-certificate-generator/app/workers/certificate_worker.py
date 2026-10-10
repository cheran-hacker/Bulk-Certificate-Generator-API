from datetime import datetime
from app.templates.certificate_template import generate_pdf
from app.storage.local_storage import LocalStorage

def generate_certificate_for_record(
    recipient_name: str,
    certificate_title: str,
    event_name: str,
    organization_name: str,
    issue_date: datetime,
    certificate_code: str
) -> tuple[str, int]:
    
    storage = LocalStorage()
    
    filename = f"{certificate_code}.pdf"
    
    pdf_bytes = generate_pdf(
        recipient_name=recipient_name,
        certificate_title=certificate_title,
        event_name=event_name,
        organization_name=organization_name,
        issue_date=issue_date.strftime("%B %d, %Y"),
        certificate_code=certificate_code
    )
    
    file_path = storage.save(filename, pdf_bytes)
    file_size = len(pdf_bytes)
    
    return file_path, file_size
