# Frontend Authentication Integration Guide

Complete guide to integrate Registration and Login APIs with OTP verification in your frontend application.

## 📋 Table of Contents

1. [Overview](#overview)
2. [API Endpoints](#api-endpoints)
3. [Authentication Flow](#authentication-flow)
4. [Setup Instructions](#setup-instructions)
5. [TypeScript Types](#typescript-types)
6. [API Service Layer](#api-service-layer)
7. [React Components](#react-components)
8. [Error Handling](#error-handling)
9. [Token Management](#token-management)
10. [Complete Examples](#complete-examples)

---

## Overview

The authentication system uses a **two-step verification process**:

1. **Registration**: User registers → OTP sent to email → User verifies OTP → Account activated
2. **Login**: User logs in with email/password (email must be verified)

### Key Features

- ✅ Email verification with OTP (6-digit code)
- ✅ JWT token-based authentication
- ✅ Password minimum 8 characters
- ✅ OTP expires in 10 minutes
- ✅ Resend OTP functionality

---

## API Endpoints

### Base URL
```
http://127.0.0.1:8000
```
(Update for production: `https://your-api-domain.com`)

### Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/verify-otp` | Verify OTP and activate account | No |
| POST | `/auth/resend-otp` | Resend OTP code | No |
| POST | `/auth/login` | Login user | No |
| GET | `/auth/me` | Get current user info | Yes |

---

## Authentication Flow

### Registration Flow

```
1. User fills registration form
   ↓
2. POST /auth/register
   - Request: { email, password, name? }
   - Response: { user_id, email, message }
   ↓
3. OTP sent to user's email
   ↓
4. User enters OTP from email
   ↓
5. POST /auth/verify-otp
   - Request: { user_id, otp }
   - Response: { access_token, token_type, user }
   ↓
6. Save token → User logged in
```

### Login Flow

```
1. User fills login form
   ↓
2. POST /auth/login
   - Request: { email, password }
   - Response: { access_token, token_type, user }
   ↓
3. Save token → User logged in
```

**Note**: Login requires email to be verified. If not verified, user must verify OTP first.

---

## Setup Instructions

### Step 1: Install Dependencies

```bash
# If using React with TypeScript
npm install axios

# Or if using vanilla JavaScript
# No additional dependencies needed (use fetch API)
```

### Step 2: Create Environment Variables

Create `.env` file in your frontend root:

```env
REACT_APP_API_BASE_URL=http://127.0.0.1:8000
```

For production:
```env
REACT_APP_API_BASE_URL=https://your-api-domain.com
```

### Step 3: Create API Configuration

Create `src/api/config.ts`:

```typescript
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000';

export const API_ENDPOINTS = {
  REGISTER: '/auth/register',
  VERIFY_OTP: '/auth/verify-otp',
  RESEND_OTP: '/auth/resend-otp',
  LOGIN: '/auth/login',
  ME: '/auth/me',
};
```

---

## TypeScript Types

Create `src/types/auth.ts`:

```typescript
// Request Types
export interface RegisterRequest {
  email: string;
  password: string;
  name?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface OTPVerifyRequest {
  user_id: string;
  otp: string;
}

export interface OTPResendRequest {
  user_id: string;
  email: string;
}

// Response Types
export interface User {
  id: string;
  email: string;
  name?: string;
  email_verified: boolean;
}

export interface RegisterResponse {
  message: string;
  user_id: string;
  email: string;
  email_verified: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ApiError {
  detail: string;
}
```

---

## API Service Layer

### Option 1: Using Axios (Recommended)

Create `src/api/authService.ts`:

```typescript
import axios from 'axios';
import { API_BASE_URL, API_ENDPOINTS } from './config';
import type {
  RegisterRequest,
  LoginRequest,
  OTPVerifyRequest,
  OTPResendRequest,
  RegisterResponse,
  TokenResponse,
  User,
} from '../types/auth';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors (token expired)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth Service Functions
export const authService = {
  /**
   * Register a new user
   */
  async register(data: RegisterRequest): Promise<RegisterResponse> {
    const response = await api.post<RegisterResponse>(
      API_ENDPOINTS.REGISTER,
      data
    );
    return response.data;
  },

  /**
   * Verify OTP and activate account
   */
  async verifyOTP(data: OTPVerifyRequest): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>(
      API_ENDPOINTS.VERIFY_OTP,
      data
    );
    return response.data;
  },

  /**
   * Resend OTP code
   */
  async resendOTP(data: OTPResendRequest): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>(
      API_ENDPOINTS.RESEND_OTP,
      data
    );
    return response.data;
  },

  /**
   * Login user
   */
  async login(data: LoginRequest): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>(
      API_ENDPOINTS.LOGIN,
      data
    );
    return response.data;
  },

  /**
   * Get current user information
   */
  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>(API_ENDPOINTS.ME);
    return response.data;
  },

  /**
   * Logout user
   */
  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },

  /**
   * Get stored token
   */
  getToken(): string | null {
    return localStorage.getItem('access_token');
  },
};

export default api;
```

### Option 2: Using Fetch API

Create `src/api/authService.ts`:

```typescript
import { API_BASE_URL, API_ENDPOINTS } from './config';
import type {
  RegisterRequest,
  LoginRequest,
  OTPVerifyRequest,
  OTPResendRequest,
  RegisterResponse,
  TokenResponse,
  User,
} from '../types/auth';

// Helper function for API calls
async function apiCall<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'An error occurred');
  }

  return response.json();
}

// Auth Service Functions
export const authService = {
  async register(data: RegisterRequest): Promise<RegisterResponse> {
    return apiCall<RegisterResponse>(API_ENDPOINTS.REGISTER, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async verifyOTP(data: OTPVerifyRequest): Promise<TokenResponse> {
    return apiCall<TokenResponse>(API_ENDPOINTS.VERIFY_OTP, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async resendOTP(data: OTPResendRequest): Promise<{ message: string }> {
    return apiCall<{ message: string }>(API_ENDPOINTS.RESEND_OTP, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async login(data: LoginRequest): Promise<TokenResponse> {
    return apiCall<TokenResponse>(API_ENDPOINTS.LOGIN, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async getCurrentUser(): Promise<User> {
    return apiCall<User>(API_ENDPOINTS.ME);
  },

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },

  getToken(): string | null {
    return localStorage.getItem('access_token');
  },
};
```

---

## React Components

### Registration Component with OTP Verification

Create `src/components/Register.tsx`:

```typescript
import React, { useState } from 'react';
import { authService } from '../api/authService';
import type { RegisterRequest, OTPVerifyRequest } from '../types/auth';

const Register: React.FC = () => {
  const [step, setStep] = useState<'register' | 'verify'>('register');
  const [formData, setFormData] = useState<RegisterRequest>({
    email: '',
    password: '',
    name: '',
  });
  const [otp, setOtp] = useState('');
  const [userId, setUserId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  // Handle registration
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      // Validate password length
      if (formData.password.length < 8) {
        throw new Error('Password must be at least 8 characters long');
      }

      const response = await authService.register(formData);
      setUserId(response.user_id);
      setMessage('Registration successful! Check your email for OTP code.');
      setStep('verify');
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  // Handle OTP verification
  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    if (!userId) {
      setError('User ID not found. Please register again.');
      return;
    }

    try {
      const response = await authService.verifyOTP({
        user_id: userId,
        otp: otp,
      });

      // Save token and user data
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));

      setMessage('Email verified successfully! Redirecting...');
      
      // Redirect to dashboard or home page
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 1500);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Invalid OTP');
    } finally {
      setLoading(false);
    }
  };

  // Handle resend OTP
  const handleResendOTP = async () => {
    if (!userId || !formData.email) {
      setError('Cannot resend OTP. Please register again.');
      return;
    }

    setError(null);
    setLoading(true);

    try {
      await authService.resendOTP({
        user_id: userId,
        email: formData.email,
      });
      setMessage('OTP has been resent to your email.');
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to resend OTP');
    } finally {
      setLoading(false);
    }
  };

  if (step === 'register') {
    return (
      <div className="register-container">
        <h2>Register</h2>
        {error && <div className="error">{error}</div>}
        {message && <div className="success">{message}</div>}
        
        <form onSubmit={handleRegister}>
          <div>
            <label>Email:</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
            />
          </div>
          
          <div>
            <label>Password (min 8 characters):</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required
              minLength={8}
            />
          </div>
          
          <div>
            <label>Name (optional):</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          </div>
          
          <button type="submit" disabled={loading}>
            {loading ? 'Registering...' : 'Register'}
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="verify-otp-container">
      <h2>Verify Email</h2>
      {error && <div className="error">{error}</div>}
      {message && <div className="success">{message}</div>}
      
      <p>Enter the 6-digit OTP code sent to <strong>{formData.email}</strong></p>
      
      <form onSubmit={handleVerifyOTP}>
        <div>
          <label>OTP Code:</label>
          <input
            type="text"
            value={otp}
            onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
            placeholder="123456"
            maxLength={6}
            required
          />
        </div>
        
        <button type="submit" disabled={loading || otp.length !== 6}>
          {loading ? 'Verifying...' : 'Verify OTP'}
        </button>
      </form>
      
      <button 
        type="button" 
        onClick={handleResendOTP} 
        disabled={loading}
        className="resend-btn"
      >
        Resend OTP
      </button>
      
      <button 
        type="button" 
        onClick={() => setStep('register')}
        className="back-btn"
      >
        Back to Registration
      </button>
    </div>
  );
};

export default Register;
```

### Login Component

Create `src/components/Login.tsx`:

```typescript
import React, { useState } from 'react';
import { authService } from '../api/authService';
import type { LoginRequest } from '../types/auth';

const Login: React.FC = () => {
  const [formData, setFormData] = useState<LoginRequest>({
    email: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await authService.login(formData);

      // Save token and user data
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));

      // Redirect to dashboard
      window.location.href = '/dashboard';
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Login failed';
      setError(errorMessage);
      
      // If email not verified, show link to resend OTP
      if (err.response?.status === 403) {
        setError(errorMessage + ' You may need to verify your email first.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      {error && <div className="error">{error}</div>}
      
      <form onSubmit={handleLogin}>
        <div>
          <label>Email:</label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            required
          />
        </div>
        
        <div>
          <label>Password:</label>
          <input
            type="password"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            required
          />
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
    </div>
  );
};

export default Login;
```

---

## Error Handling

### Common Error Responses

```typescript
// Registration Errors
{
  "detail": "Email already registered"  // 400
}
{
  "detail": "Password must be at least 8 characters long"  // 400
}

// OTP Verification Errors
{
  "detail": "Invalid or expired OTP"  // 400
}
{
  "detail": "User not found"  // 404
}
{
  "detail": "Email already verified"  // 400
}

// Login Errors
{
  "detail": "Incorrect email or password"  // 401
}
{
  "detail": "Please verify your email before logging in..."  // 403
}
```

### Error Handling Utility

Create `src/utils/errorHandler.ts`:

```typescript
export const handleApiError = (error: any): string => {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unexpected error occurred';
};

export const isEmailNotVerifiedError = (error: any): boolean => {
  return error.response?.status === 403 && 
         error.response?.data?.detail?.includes('verify your email');
};
```

---

## Token Management

### Save Token After Login/Verification

```typescript
// After successful login or OTP verification
const response = await authService.login(loginData);
// or
const response = await authService.verifyOTP(otpData);

// Save to localStorage
localStorage.setItem('access_token', response.access_token);
localStorage.setItem('user', JSON.stringify(response.user));
```

### Use Token in API Requests

The axios interceptor (or fetch headers) automatically adds the token:

```typescript
// Token is automatically added by interceptor
const user = await authService.getCurrentUser();
```

### Check Authentication Status

```typescript
import { authService } from './api/authService';

// Check if user is logged in
if (authService.isAuthenticated()) {
  // User is authenticated
} else {
  // Redirect to login
}
```

### Logout

```typescript
import { authService } from './api/authService';

const handleLogout = () => {
  authService.logout();
  window.location.href = '/login';
};
```

---

## Complete Examples

### Example: Protected Route Component

Create `src/components/ProtectedRoute.tsx`:

```typescript
import React from 'react';
import { authService } from '../api/authService';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  if (!authService.isAuthenticated()) {
    window.location.href = '/login';
    return null;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
```

### Example: Auth Context (Optional)

Create `src/context/AuthContext.tsx`:

```typescript
import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../api/authService';
import type { User } from '../types/auth';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on mount
    const token = authService.getToken();
    const storedUser = localStorage.getItem('user');
    
    if (token && storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        authService.logout();
      }
    }
    setLoading(false);
  }, []);

  const login = (token: string, userData: User) => {
    localStorage.setItem('access_token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

---

## Testing the Integration

### 1. Test Registration Flow

```typescript
// Register user
const registerData = {
  email: 'test@example.com',
  password: 'password123',
  name: 'Test User'
};

const registerResponse = await authService.register(registerData);
console.log('User ID:', registerResponse.user_id);
// Check email for OTP

// Verify OTP
const verifyResponse = await authService.verifyOTP({
  user_id: registerResponse.user_id,
  otp: '123456' // From email
});
console.log('Token:', verifyResponse.access_token);
```

### 2. Test Login

```typescript
const loginData = {
  email: 'test@example.com',
  password: 'password123'
};

const loginResponse = await authService.login(loginData);
console.log('Token:', loginResponse.access_token);
```

### 3. Test Protected Endpoint

```typescript
// Token is automatically added by interceptor
const user = await authService.getCurrentUser();
console.log('Current user:', user);
```

---

## Quick Start Checklist

- [ ] Install dependencies (`axios` or use `fetch`)
- [ ] Create `.env` file with `REACT_APP_API_BASE_URL`
- [ ] Create TypeScript types (`src/types/auth.ts`)
- [ ] Create API config (`src/api/config.ts`)
- [ ] Create auth service (`src/api/authService.ts`)
- [ ] Create Register component
- [ ] Create Login component
- [ ] Add error handling
- [ ] Test registration flow
- [ ] Test login flow
- [ ] Test protected routes

---

## Troubleshooting

### OTP Not Received
- Check spam folder
- In development, OTP is printed to backend console
- Use `/auth/resend-otp` endpoint

### Login Fails with "Email not verified"
- User must verify OTP first
- Use resend OTP if OTP expired

### Token Not Working
- Check if token is saved in localStorage
- Verify token format: `Bearer <token>`
- Check if token expired (default: 7 days)

### CORS Errors
- Ensure backend CORS allows your frontend origin
- Check `app/main.py` CORS configuration

---

## Production Considerations

1. **Environment Variables**: Use different API URLs for dev/prod
2. **Token Storage**: Consider using httpOnly cookies for better security
3. **Token Refresh**: Implement refresh token mechanism if needed
4. **Error Logging**: Add error tracking (Sentry, etc.)
5. **Loading States**: Show proper loading indicators
6. **Form Validation**: Add client-side validation
7. **Rate Limiting**: Handle rate limit errors gracefully

---

## Support

For API documentation, visit:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

For issues or questions, check the backend logs or API documentation.

