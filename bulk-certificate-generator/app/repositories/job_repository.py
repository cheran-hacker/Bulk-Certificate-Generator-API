from sqlalchemy.orm import Session
from sqlalchemy import select
import uuid
from app.db.models.generation_job import GenerationJob

class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, job: GenerationJob) -> GenerationJob:
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get(self, job_id: uuid.UUID) -> GenerationJob | None:
        return self.db.execute(select(GenerationJob).where(GenerationJob.id == job_id)).scalar_one_or_none()

    def update(self, job: GenerationJob) -> GenerationJob:
        self.db.commit()
        self.db.refresh(job)
        return job
