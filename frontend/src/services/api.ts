// Lightweight API Client Wrapper

const BASE_URL = '/api/v1';

interface RequestOptions {
  method?: string;
  body?: any;
  headers?: Record<string, string>;
}

async function request(endpoint: string, options: RequestOptions = {}) {
  const token = localStorage.getItem('access_token');
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config: RequestInit = {
    method: options.method || 'GET',
    headers,
  };

  if (options.body) {
    if (options.body instanceof URLSearchParams) {
      headers['Content-Type'] = 'application/x-www-form-urlencoded';
      config.body = options.body;
    } else {
      config.body = JSON.stringify(options.body);
    }
  }

  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, config);

    // Auto-logout if token is expired or unauthorized
    if (response.status === 401 && !endpoint.includes('/auth/login')) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
      throw new Error('Unauthorized');
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'API request failed');
    }

    // Handle empty response bodies
    if (response.status === 204) {
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    throw error;
  }
}

export const api = {
  get: (endpoint: string, headers?: Record<string, string>) => 
    request(endpoint, { method: 'GET', headers }),
    
  post: (endpoint: string, body?: any, headers?: Record<string, string>) => 
    request(endpoint, { method: 'POST', body, headers }),
    
  put: (endpoint: string, body?: any, headers?: Record<string, string>) => 
    request(endpoint, { method: 'PUT', body, headers }),
    
  delete: (endpoint: string, headers?: Record<string, string>) => 
    request(endpoint, { method: 'DELETE', headers }),
};
