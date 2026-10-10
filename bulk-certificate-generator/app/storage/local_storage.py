import os
from app.core.config import settings

class LocalStorage:
    def __init__(self):
        self.base_path = settings.certificate_storage_path
        os.makedirs(self.base_path, exist_ok=True)

    def get_absolute_path(self, relative_path: str) -> str:
        return os.path.abspath(os.path.join(self.base_path, relative_path))

    def save(self, filename: str, data: bytes) -> str:
        safe_filename = os.path.basename(filename)
        path = os.path.join(self.base_path, safe_filename)
        with open(path, 'wb') as f:
            f.write(data)
        return safe_filename

    def exists(self, filename: str) -> bool:
        safe_filename = os.path.basename(filename)
        path = os.path.join(self.base_path, safe_filename)
        return os.path.exists(path)
