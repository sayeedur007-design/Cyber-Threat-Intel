import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000, // Increased timeout to 300s (5 minutes) for slow local LLM processing
});

// Add a request interceptor to inject the token
apiClient.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

/**
 * Handle API Errors consistently
 */
const handleApiError = (error: any, fallbackMessage: string) => {
  if (error.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    let detail = error.response.data?.detail;
    if (Array.isArray(detail)) {
      detail = detail.map((d: any) => `${d.loc?.join('.')} - ${d.msg}`).join(', ');
    }
    throw new Error(detail || error.response.data?.message || fallbackMessage);
  } else if (error.request) {
    // The request was made but no response was received
    throw new Error(error.code === 'ECONNABORTED' ? 'API Request Timed Out' : 'No response received from the server. Check if backend is running.');
  } else {
    // Something happened in setting up the request that triggered an Error
    throw new Error(error.message || fallbackMessage);
  }
};

export const ctiApi = {
  /**
   * Auth: Login
   */
  login: async (credentials: any) => {
    try {
      // OAuth2PasswordBearer expects form data
      const formData = new URLSearchParams();
      formData.append('username', credentials.email);
      formData.append('password', credentials.password);
      
      const response = await apiClient.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      return response.data;
    } catch (error) {
      return handleApiError(error, 'Login failed. Please check your credentials.');
    }
  },

  /**
   * Auth: Register
   */
  register: async (userData: any) => {
    try {
      const response = await apiClient.post('/auth/register', userData);
      return response.data;
    } catch (error) {
      return handleApiError(error, 'Registration failed.');
    }
  },

  /**
   * Auth: Get Current User
   */
  getMe: async () => {
    try {
      const response = await apiClient.get('/auth/me');
      return response.data;
    } catch (error) {
      return handleApiError(error, 'Failed to fetch user profile.');
    }
  },

  /**
   * History: Get user queries
   */
  getHistory: async () => {
    try {
      const response = await apiClient.get('/history');
      return response.data;
    } catch (error) {
      return handleApiError(error, 'Failed to fetch query history.');
    }
  },

  /**
   * History: Delete entry
   */
  deleteHistory: async (id: number) => {
    try {
      const response = await apiClient.delete(`/history/${id}`);
      return response.data;
    } catch (error) {
      return handleApiError(error, 'Failed to delete history entry.');
    }
  },

  /**
   * Reports: Generate PDF
   */
  generateReport: async (data: any) => {
    try {
      const response = await apiClient.post('/report/generate', data, {
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      return handleApiError(error, 'Failed to generate PDF report.');
    }
  },

  /**
   * RAG Query
   * @param query The user question
   */
  ragQuery: async (query: string) => {
    try {
      const response = await apiClient.post('/rag-query', { question: query });
      return response.data;
    } catch (error) {
      return handleApiError(error, 'Failed to execute RAG query.');
    }
  },

  /**
   * Classify Text
   * @param text The threat intelligence text to classify
   */
  classifyText: async (text: string) => {
    try {
      const response = await apiClient.post('/classify', { text });
      return response.data;
    } catch (error) {
      return handleApiError(error, 'Failed to classify threat intelligence text.');
    }
  },

  /**
   * Get Vulnerability Details
   * @param cveId The specific CVE identifier (e.g., CVE-2024-12345)
   */
  getVulnerability: async (cveId: string) => {
    try {
      const response = await apiClient.get(`/vuln/${cveId}`);
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        throw new Error(`Vulnerability ${cveId} not found in the database.`);
      }
      return handleApiError(error, 'Failed to retrieve vulnerability information.');
    }
  },

  /**
   * Index Documents via file upload (Kept for existing functionality)
   * @param files Array of files to upload
   */
  indexDocuments: async (files: File[]) => {
    try {
      const formData = new FormData();
      files.forEach((file) => {
        formData.append('files', file);
      });

      const response = await apiClient.post('/index', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    } catch (error) {
      return handleApiError(error, 'Failed to index documents.');
    }
  },
};
