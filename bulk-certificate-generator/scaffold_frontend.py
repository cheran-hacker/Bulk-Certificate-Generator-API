import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

directories = [
    "src/api",
    "src/components",
    "src/hooks",
    "src/pages",
    "src/styles",
    "src/utils"
]

for d in directories:
    os.makedirs(f"frontend/{d}", exist_ok=True)

api_client = """import axios from 'axios';
import toast from 'react-hot-toast';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An unexpected error occurred';
    toast.error(message);
    return Promise.reject(error);
  }
);
"""

api_health = """import { apiClient } from './client';

export const healthApi = {
  checkHealth: async () => {
    const response = await apiClient.get('/api/v1/health');
    return response.data;
  },
};
"""

api_jobs = """import { apiClient } from './client';

export const jobsApi = {
  createJob: async (data) => {
    const response = await apiClient.post('/api/v1/jobs', data);
    return response.data;
  },
  getJob: async (jobId) => {
    const response = await apiClient.get(`/api/v1/jobs/${jobId}`);
    return response.data;
  },
  getJobCertificates: async (jobId, skip = 0, limit = 100) => {
    const response = await apiClient.get(`/api/v1/jobs/${jobId}/certificates?skip=${skip}&limit=${limit}`);
    return response.data;
  },
};
"""

api_certificates = """import { apiClient } from './client';

export const certificatesApi = {
  getCertificate: async (certId) => {
    const response = await apiClient.get(`/api/v1/certificates/${certId}`);
    return response.data;
  },
  downloadCertificate: async (certId) => {
    const response = await apiClient.get(`/api/v1/certificates/${certId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },
};
"""

create_file("frontend/src/api/client.js", api_client)
create_file("frontend/src/api/health.js", api_health)
create_file("frontend/src/api/jobs.js", api_jobs)
create_file("frontend/src/api/certificates.js", api_certificates)

print("Scaffolded frontend directories and API files")
