/**
 * CloudGuardian Frontend Configuration
 * 
 * Determines the API base URL based on the current environment.
 * - In production (Docker/Nginx), the API is served from the same origin (via reverse proxy).
 * - In development (opening HTML files directly or simple server), it defaults to localhost:8000.
 */

(function () {
    const hostname = window.location.hostname;

    // Check if we are in a development environment (localhost or local file)
    const isDev = hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '';

    // If accessing via file protocol or localhost without a proxy, use the local backend URL
    // If accessing via a domain or IP that serves both (via Nginx), use relative path (empty string)
    // Note: If you are running `python -m http.server` for frontend on port 8080 and backend on 8000, 
    // you still need the full URL.

    // We assume that if we are on localhost, we might be running them separately.
    // Ideally, for production build, we might want to inject this value.
    // For now, this logic works for the described setup:

    let apiBase = '';

    // If strictly opening file://, default to localhost:8000
    if (window.location.protocol === 'file:') {
        apiBase = 'http://localhost:8000';
    } else if (isDev && window.location.port !== '8000') {
        // If on localhost but NOT on port 8000 (e.g. 5500 via Live Server), assume backend is on 8000
        // If on port 8000, we are likely hitting Nginx or Backend directly (if backend served static).
        apiBase = 'http://localhost:8000';
    } else {
        // Production or Nginx on localhost:80 (default HTTP port)
        // We use /api prefix so Nginx can differentiate between frontend and backend requests
        apiBase = '/api';
    }

    // Expose to window
    window.API_BASE = apiBase;

    console.log('CloudGuardian Config: API_BASE set to', apiBase || '(relative)');
})();
