import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach Authorization header if token exists
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('cloudguard_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: async (email, password) => {
    const response = await apiClient.post('/auth/login', { email, password });
    if (response.data.access_token) {
      localStorage.setItem('cloudguard_token', response.data.access_token);
    }
    return response.data;
  },
  register: async (email, password, full_name) => {
    return (await apiClient.post('/auth/register', { email, password, full_name })).data;
  },
  getMe: async () => {
    return (await apiClient.get('/auth/me')).data;
  },
};

export const accountsAPI = {
  list: async () => (await apiClient.get('/accounts/')).data,
  create: async (accountData) => (await apiClient.post('/accounts/', accountData)).data,
  delete: async (accountId) => (await apiClient.delete(`/accounts/${accountId}`)).data,
};

export const scansAPI = {
  trigger: async (accountId) => (await apiClient.post('/scans/', { account_id: accountId })).data,
  list: async (accountId) => (await apiClient.get('/scans/', { params: { account_id: accountId } })).data,
  get: async (scanId) => (await apiClient.get(`/scans/${scanId}`)).data,
  getFindings: async (scanId, severity) => 
    (await apiClient.get(`/scans/${scanId}/findings`, { params: { severity } })).data,
};

export const dashboardAPI = {
  getOverview: async () => (await apiClient.get('/dashboard/overview')).data,
  getAllFindings: async (params) => (await apiClient.get('/findings/', { params })).data,
};

export default apiClient;
