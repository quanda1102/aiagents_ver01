// API Configuration
const API_CONFIG = {
  // Auto-detect environment
  BASE_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://localhost:8000'
    : 'https://api.aagents.vn',
  
  // API endpoints
  ENDPOINTS: {
    LOGIN: '/api/v1/auth/login',
    REGISTER: '/api/v1/auth/register', 
    ME: '/api/v1/auth/me',
    USERS: '/api/v1/users',
    QUIZ: '/api/v1/quiz',
    CHAT: '/api/v1/chat',
    LECTURES: '/api/v1/lectures'
  }
};

// Helper function to get full API URL
function getApiUrl(endpoint) {
  return API_CONFIG.BASE_URL + API_CONFIG.ENDPOINTS[endpoint];
}

// Export for use in other scripts
window.API_CONFIG = API_CONFIG;
window.getApiUrl = getApiUrl;