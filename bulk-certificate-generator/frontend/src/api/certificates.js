import { apiClient } from './client';

export const certificatesApi = {
  getCertificates: async (page = 1, pageSize = 50) => {
    const response = await apiClient.get(`/api/v1/certificates?page=${page}&page_size=${pageSize}`);
    return response.data;
  },
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