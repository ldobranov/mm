// Use local IP if on local network, else use public IP
export const API_BASE_URL =
  window.location.hostname.startsWith('10.10.') || window.location.hostname === 'localhost'
    ? 'http://10.10.0.100:8887'
    : 'http://46.55.199.146:8887';
