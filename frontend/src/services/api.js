import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: attach bearer token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: catch 401s
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token and trigger auth redirect if not already on login
      if (!window.location.pathname.includes('/login')) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (email, password, full_name) => api.post('/auth/register', { email, password, full_name }),
  getMe: () => api.get('/auth/me'),
};

export const ingestionService = {
  uploadCSV: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/ingestion/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export const transactionService = {
  getTransactions: (params) => api.get('/transactions', { params }),
  createTransaction: (data) => api.post('/transactions', data),
  updateTransaction: (id, data) => api.patch(`/transactions/${id}`, data),
  deleteTransaction: (id) => api.delete(`/transactions/${id}`),
};

export const analyticsService = {
  getSummary: () => api.get('/analytics/summary'),
  getCategories: () => api.get('/analytics/categories'),
  getMonthlyTrends: () => api.get('/analytics/monthly'),
  getRecurring: () => api.get('/analytics/recurring'),
};

export const forecastService = {
  getForecast: (days = 30) => api.get('/forecasting', { params: { days } }),
};

export const riskService = {
  getRiskScore: () => api.get('/risk/score'),
};

export const goalService = {
  getGoals: () => api.get('/goals'),
  createGoal: (data) => api.post('/goals', data),
  updateGoal: (id, data) => api.patch(`/goals/${id}`, data),
  deleteGoal: (id) => api.delete(`/goals/${id}`),
};

export const recommendationService = {
  getRecommendations: (statusFilter) => api.get('/recommendations', { params: { status_filter: statusFilter } }),
  generateRecommendations: () => api.post('/recommendations/generate'),
  actOnRecommendation: (id, action, user_notes) =>
    api.post(`/recommendations/${id}/action`, { action, user_notes }),
  getAuditLogs: () => api.get('/recommendations/audit-logs'),
};

export default api;
