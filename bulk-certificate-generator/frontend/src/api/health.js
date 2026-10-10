import { apiClient } from './client';

export const healthApi = {
  checkHealth: async () => {
    const response = await apiClient.get('/api/v1/health');
    return response.data;
  },
};
