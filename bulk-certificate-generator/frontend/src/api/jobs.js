import { apiClient } from './client';

export const jobsApi = {
  getJobs: async (skip = 0, limit = 50) => {
    const response = await apiClient.get(`/api/v1/jobs?skip=${skip}&limit=${limit}`);
    return response.data;
  },
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