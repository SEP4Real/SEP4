const API_URL = 'http://127.0.0.1:8000';

export async function register(userData) {
  const response = await fetch(`${API_URL}/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(userData)
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Registration error');
  }

  return await response.json();
}

export async function login(credentials) {
  const response = await fetch(`${API_URL}/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      username: credentials.email, // send email like username for Python
      password: credentials.password
    })
  });

  if (!response.ok) {
    const errorBody = await response.json();
    throw new Error(errorBody.detail || 'Authentication error');
  }

  const data = await response.json();

  // Save token in localStorage
  if (data.access_token) {
    localStorage.setItem('token', data.access_token);
    const userToSave = { 
        email: credentials.email || "student", 
        role: "Student" 
    };
  
    localStorage.setItem('user', JSON.stringify(userToSave));
  }

  return data;
}

export function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
}