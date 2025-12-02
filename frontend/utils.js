/* frontend/utils.js */

/**
 * Shows a non-blocking toast notification.
 * @param {string} message - The message to display.
 * @param {string} type - 'success' or 'error' (default: 'success')
 */
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerText = message;

  container.appendChild(toast);

  // Trigger animation
  setTimeout(() => {
    toast.classList.add('show');
  }, 10);

  // Remove after 3 seconds
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => {
      toast.remove();
    }, 300);
  }, 3000);
}

// ---------- DEVICE ID HELPER ----------

function getDeviceId() {
  let deviceId = localStorage.getItem('device_id');
  if (!deviceId) {
    // Generate a simple random ID if not present
    deviceId = 'device_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    localStorage.setItem('device_id', deviceId);
  }
  return deviceId;
}

// ---------- AUTH HELPERS ----------

function setAuthToken(token) {
  localStorage.setItem('auth_token', token);
}

function getAuthToken() {
  return localStorage.getItem('auth_token');
}

function clearAuthToken() {
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user_role');
  localStorage.removeItem('user_id');
}

function isLoggedIn() {
  return !!getAuthToken();
}

/**
 * Wrapper around fetch to automatically attach the JWT token.
 */
async function fetchWithAuth(url, options = {}) {
  const token = getAuthToken();

  if (!options.headers) {
    options.headers = {};
  }

  if (token) {
    options.headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, options);

  if (response.status === 401) {
    // Token expired or invalid
    showToast("Session expired. Please login again.", "error");
    clearAuthToken();
    setTimeout(() => window.location.href = "login.html", 1500);
    throw new Error("Unauthorized");
  }

  return response;
}
