import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Thêm interceptor để xử lý token nếu cần (dành cho các request cần auth)
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const eventApi = {
  getAll: async (skip = 0, limit = 100) => {
    const response = await apiClient.get(`/events`, {
      params: { skip, limit },
    });
    return response.data;
  },
  getById: async (id: string) => {
    const response = await apiClient.get(`/events/${id}`);
    return response.data;
  },
  create: async (data: any) => {
    const { venue_id, ...eventData } = data;
    const response = await apiClient.post(`/venues/${venue_id}/events`, eventData);
    return response.data;
  },
  update: async (id: string, data: any) => {
    const response = await apiClient.put(`/events/${id}`, data);
    return response.data;
  },
  delete: async (id: string) => {
    const response = await apiClient.delete(`/events/${id}`);
    return response.data;
  },
};

export const showtimeApi = {
  getByEventId: async (eventId: string) => {
    const response = await apiClient.get(`/events/${eventId}/showtimes`);
    return response.data;
  },
  getById: async (id: string) => {
    const response = await apiClient.get(`/showtimes/${id}`);
    return response.data;
  },
  create: async (data: any) => {
    const response = await apiClient.post(`/showtimes/`, data);
    return response.data;
  },
  update: async (id: string, data: any) => {
    const response = await apiClient.put(`/showtimes/${id}`, data);
    return response.data;
  },
  delete: async (id: string) => {
    const response = await apiClient.delete(`/showtimes/${id}`);
    return response.data;
  },
};

export const venueApi = {
  getAll: async () => {
    const response = await apiClient.get('/venues/');
    return response.data;
  },
  getById: async (id: string) => {
    const response = await apiClient.get(`/venues/${id}`);
    return response.data;
  },
  create: async (data: any) => {
    const response = await apiClient.post(`/venues/`, data);
    return response.data;
  },
  update: async (id: string, data: any) => {
    const response = await apiClient.put(`/venues/${id}`, data);
    return response.data;
  },
  delete: async (id: string) => {
    const response = await apiClient.delete(`/venues/${id}`);
    return response.data;
  },
};

export const seatApi = {
  getByShowtimeId: async (showtimeId: string) => {
    const response = await apiClient.get(`/showtimes/${showtimeId}/seats`);
    return response.data;
  },
};

export const orderApi = {
  create: async (orderData: any) => {
    const response = await apiClient.post('/orders/', orderData);
    return response.data;
  },
  getById: async (id: string) => {
    const response = await apiClient.get(`/orders/${id}`);
    return response.data;
  },
};

export const paymentApi = {
  create: async (paymentData: any) => {
    const response = await apiClient.post('/payments/', paymentData);
    return response.data;
  },
  list: async () => {
    const response = await apiClient.get('/payments/');
    return response.data;
  },
};

export const authApi = {
  login: async (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', email); // FastAPI OAuth2 uses 'username'
    formData.append('password', password);
    
    const response = await apiClient.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },
  register: async (userData: any) => {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  },
  getMe: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },
};

export const lcChatApi = {
  ask: async (question: string) => {
    const token = localStorage.getItem('access_token');
    return fetch(`${API_BASE_URL}/lc-chat/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
      },
      body: JSON.stringify({ question }),
    });
  },
  getHistory: async () => {
    const response = await apiClient.get('/lc-chat/history');
    return response.data;
  },
  clearHistory: async () => {
    const response = await apiClient.delete('/lc-chat/history');
    return response.data;
  },
};

export default apiClient;
