# Frontend Integration Guide

Complete guide to integrate this FastAPI backend with your React + TypeScript frontend.

## 📋 Table of Contents
1. [Backend Setup](#backend-setup)
2. [Frontend Setup](#frontend-setup)
3. [API Service Layer](#api-service-layer)
4. [Authentication Flow](#authentication-flow)
5. [API Integration Examples](#api-integration-examples)
6. [TypeScript Types](#typescript-types)
7. [React Components Examples](#react-components-examples)
8. [Error Handling](#error-handling)

---

## 1. Backend Setup

### Ensure Backend is Running

```bash
# In backend directory (temp_BE)
cd /home/vishal/Downloads/temp_BE
source venv/bin/activate
./run_server.sh
```

Backend will run on: **http://127.0.0.1:8000**

### Verify CORS is Enabled

The backend is already configured to accept requests from `http://localhost:3000`

Check `app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 2. Frontend Setup

### Install Required Dependencies

```bash
cd your-frontend-directory
npm install axios
# Or if using fetch, no additional dependency needed
```

### Create Environment Variables

Create `.env` file in your frontend root:

```env
REACT_APP_API_BASE_URL=http://127.0.0.1:8000
```

---

## 3. API Service Layer

### Create API Configuration (`src/api/config.ts`)

```typescript
// src/api/config.ts

export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000';

export const API_ENDPOINTS = {
  // Auth
  REGISTER: '/auth/register',
  LOGIN: '/auth/login',
  ME: '/auth/me',
  
  // Friends
  FRIENDS: '/friends',
  
  // Expenses
  EXPENSES: '/expenses',
  EXPENSE_BALANCE: (friendId: string) => `/expenses/${friendId}/balance`,
  EXPENSES_WITH_FRIEND: (friendId: string) => `/expenses/${friendId}`,
};
```

### Create Axios Instance (`src/api/axios.ts`)

```typescript
// src/api/axios.ts

import axios from 'axios';
import { API_BASE_URL } from './config';

// Create axios instance
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add JWT token to requests
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
```

---

## 4. Authentication Flow

### Auth Service (`src/api/authService.ts`)

```typescript
// src/api/authService.ts

import axiosInstance from './axios';
import { API_ENDPOINTS } from './config';

export interface User {
  id: string;
  email: string;
  name?: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

class AuthService {
  // Register new user
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await axiosInstance.post<AuthResponse>(
      API_ENDPOINTS.REGISTER,
      data
    );
    
    // Store token and user data
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));
    
    return response.data;
  }

  // Login user
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await axiosInstance.post<AuthResponse>(
      API_ENDPOINTS.LOGIN,
      data
    );
    
    // Store token and user data
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));
    
    return response.data;
  }

  // Get current user
  async getCurrentUser(): Promise<User> {
    const response = await axiosInstance.get<User>(API_ENDPOINTS.ME);
    localStorage.setItem('user', JSON.stringify(response.data));
    return response.data;
  }

  // Logout
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }

  // Get stored user
  getStoredUser(): User | null {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }
}

export default new AuthService();
```

### Auth Context (`src/context/AuthContext.tsx`)

```typescript
// src/context/AuthContext.tsx

import React, { createContext, useContext, useState, useEffect } from 'react';
import authService, { User } from '../api/authService';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name?: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const storedUser = authService.getStoredUser();
    if (storedUser && authService.isAuthenticated()) {
      setUser(storedUser);
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const response = await authService.login({ email, password });
    setUser(response.user);
  };

  const register = async (email: string, password: string, name?: string) => {
    const response = await authService.register({ email, password, name });
    setUser(response.user);
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!user,
      }}
    >
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

## 5. API Integration Examples

### Friends Service (`src/api/friendsService.ts`)

```typescript
// src/api/friendsService.ts

import axiosInstance from './axios';
import { API_ENDPOINTS } from './config';

export interface Friend {
  id: string;
  email: string;
  name?: string;
}

export interface AddFriendRequest {
  email: string;
  name?: string;
}

class FriendsService {
  // Get all friends
  async getFriends(): Promise<Friend[]> {
    const response = await axiosInstance.get<Friend[]>(API_ENDPOINTS.FRIENDS);
    return response.data;
  }

  // Add a friend
  async addFriend(data: AddFriendRequest): Promise<Friend> {
    const response = await axiosInstance.post<Friend>(
      API_ENDPOINTS.FRIENDS,
      data
    );
    return response.data;
  }
}

export default new FriendsService();
```

### Expenses Service (`src/api/expensesService.ts`)

```typescript
// src/api/expensesService.ts

import axiosInstance from './axios';
import { API_ENDPOINTS } from './config';

export interface Expense {
  id: string;
  userAId: string;
  userBId: string;
  amount: number;
  description: string;
  paidByUserId: string;
  date: string;
}

export interface CreateExpenseRequest {
  friend_id: string;
  amount: number;
  description: string;
  paid_by_user_id: string;
  expense_date: string; // YYYY-MM-DD format
}

export interface Balance {
  balance: number;
}

class ExpensesService {
  // Get expenses with a friend
  async getExpensesWithFriend(friendId: string): Promise<Expense[]> {
    const response = await axiosInstance.get<Expense[]>(
      API_ENDPOINTS.EXPENSES_WITH_FRIEND(friendId)
    );
    return response.data;
  }

  // Create new expense
  async createExpense(data: CreateExpenseRequest): Promise<Expense> {
    const response = await axiosInstance.post<Expense>(
      API_ENDPOINTS.EXPENSES,
      data
    );
    return response.data;
  }

  // Get balance with a friend
  async getBalance(friendId: string): Promise<Balance> {
    const response = await axiosInstance.get<Balance>(
      API_ENDPOINTS.EXPENSE_BALANCE(friendId)
    );
    return response.data;
  }
}

export default new ExpensesService();
```

---

## 6. TypeScript Types

### Create Types File (`src/types/index.ts`)

```typescript
// src/types/index.ts

export interface User {
  id: string;
  email: string;
  name?: string;
}

export interface Friend {
  id: string;
  email: string;
  name?: string;
}

export interface Expense {
  id: string;
  userAId: string;
  userBId: string;
  amount: number;
  description: string;
  paidByUserId: string;
  date: string;
}

export interface Balance {
  balance: number;
}

export interface ApiError {
  detail: string | Array<{
    loc: string[];
    msg: string;
    type: string;
  }>;
}
```

---

## 7. React Components Examples

### Login Component (`src/components/Login.tsx`)

```typescript
// src/components/Login.tsx

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        {error && <div className="error">{error}</div>}
        <button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
    </div>
  );
};

export default Login;
```

### Friends List Component (`src/components/FriendsList.tsx`)

```typescript
// src/components/FriendsList.tsx

import React, { useEffect, useState } from 'react';
import friendsService, { Friend } from '../api/friendsService';

const FriendsList: React.FC = () => {
  const [friends, setFriends] = useState<Friend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadFriends();
  }, []);

  const loadFriends = async () => {
    try {
      const data = await friendsService.getFriends();
      setFriends(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load friends');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="friends-list">
      <h2>Friends</h2>
      {friends.length === 0 ? (
        <p>No friends yet. Add some friends to get started!</p>
      ) : (
        <ul>
          {friends.map((friend) => (
            <li key={friend.id}>
              <span>{friend.name || friend.email}</span>
              <button onClick={() => {/* Navigate to chat */}}>
                View Expenses
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default FriendsList;
```

### Add Friend Component (`src/components/AddFriend.tsx`)

```typescript
// src/components/AddFriend.tsx

import React, { useState } from 'react';
import friendsService from '../api/friendsService';

interface AddFriendProps {
  onFriendAdded: () => void;
}

const AddFriend: React.FC<AddFriendProps> = ({ onFriendAdded }) => {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setLoading(true);

    try {
      await friendsService.addFriend({ email, name: name || undefined });
      setSuccess(true);
      setEmail('');
      setName('');
      onFriendAdded();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add friend');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="add-friend">
      <h3>Add Friend</h3>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Friend's Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Friend's Name (optional)"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        {error && <div className="error">{error}</div>}
        {success && <div className="success">Friend added successfully!</div>}
        <button type="submit" disabled={loading}>
          {loading ? 'Adding...' : 'Add Friend'}
        </button>
      </form>
    </div>
  );
};

export default AddFriend;
```

### Expenses Component (`src/components/ExpensesView.tsx`)

```typescript
// src/components/ExpensesView.tsx

import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import expensesService, { Expense, Balance } from '../api/expensesService';
import { useAuth } from '../context/AuthContext';

const ExpensesView: React.FC = () => {
  const { friendId } = useParams<{ friendId: string }>();
  const { user } = useAuth();
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [balance, setBalance] = useState<number>(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (friendId) {
      loadExpenses();
      loadBalance();
    }
  }, [friendId]);

  const loadExpenses = async () => {
    try {
      const data = await expensesService.getExpensesWithFriend(friendId!);
      setExpenses(data);
    } catch (err) {
      console.error('Failed to load expenses', err);
    }
  };

  const loadBalance = async () => {
    try {
      const data = await expensesService.getBalance(friendId!);
      setBalance(data.balance);
    } catch (err) {
      console.error('Failed to load balance', err);
    } finally {
      setLoading(false);
    }
  };

  const formatBalance = (balance: number) => {
    if (balance > 0) {
      return `Friend owes you ₹${balance.toFixed(2)}`;
    } else if (balance < 0) {
      return `You owe friend ₹${Math.abs(balance).toFixed(2)}`;
    }
    return 'All settled up! ₹0';
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="expenses-view">
      <div className="balance-card">
        <h3>Balance</h3>
        <p className={balance > 0 ? 'positive' : balance < 0 ? 'negative' : 'zero'}>
          {formatBalance(balance)}
        </p>
      </div>

      <div className="expenses-list">
        <h3>Expenses</h3>
        {expenses.length === 0 ? (
          <p>No expenses yet</p>
        ) : (
          <ul>
            {expenses.map((expense) => (
              <li key={expense.id}>
                <div>
                  <strong>{expense.description}</strong>
                  <span>₹{expense.amount}</span>
                </div>
                <div>
                  <small>
                    {expense.paidByUserId === user?.id ? 'You paid' : 'Friend paid'}
                  </small>
                  <small>{new Date(expense.date).toLocaleDateString()}</small>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default ExpensesView;
```

### Add Expense Component (`src/components/AddExpense.tsx`)

```typescript
// src/components/AddExpense.tsx

import React, { useState } from 'react';
import expensesService from '../api/expensesService';
import { useAuth } from '../context/AuthContext';

interface AddExpenseProps {
  friendId: string;
  onExpenseAdded: () => void;
}

const AddExpense: React.FC<AddExpenseProps> = ({ friendId, onExpenseAdded }) => {
  const { user } = useAuth();
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [paidBy, setPaidBy] = useState<'me' | 'friend'>('me');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await expensesService.createExpense({
        friend_id: friendId,
        amount: parseFloat(amount),
        description,
        paid_by_user_id: paidBy === 'me' ? user!.id : friendId,
        expense_date: new Date().toISOString().split('T')[0], // Today's date
      });
      
      setAmount('');
      setDescription('');
      setPaidBy('me');
      onExpenseAdded();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add expense');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="add-expense">
      <h3>Add Expense</h3>
      <form onSubmit={handleSubmit}>
        <input
          type="number"
          step="0.01"
          placeholder="Amount"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          required
        />
        <select value={paidBy} onChange={(e) => setPaidBy(e.target.value as 'me' | 'friend')}>
          <option value="me">I paid</option>
          <option value="friend">Friend paid</option>
        </select>
        {error && <div className="error">{error}</div>}
        <button type="submit" disabled={loading}>
          {loading ? 'Adding...' : 'Add Expense'}
        </button>
      </form>
    </div>
  );
};

export default AddExpense;
```

---

## 8. Error Handling

### Global Error Handler (`src/utils/errorHandler.ts`)

```typescript
// src/utils/errorHandler.ts

import { AxiosError } from 'axios';

export const handleApiError = (error: unknown): string => {
  if (error instanceof AxiosError) {
    // Check if it's a validation error (422)
    if (error.response?.status === 422) {
      const details = error.response.data.detail;
      if (Array.isArray(details)) {
        return details.map(err => err.msg).join(', ');
      }
    }
    
    // Other API errors
    return error.response?.data?.detail || 'An error occurred';
  }
  
  // Network or other errors
  return 'Network error. Please check your connection.';
};
```

---

## 9. App Setup

### Main App Setup (`src/App.tsx`)

```typescript
// src/App.tsx

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) return <div>Loading...</div>;
  
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
```

---

## 10. Testing the Integration

### Test Checklist

1. **Backend Running**: ✅ `./run_server.sh`
2. **Frontend Running**: ✅ `npm start`
3. **Test Registration**: Create a new user
4. **Test Login**: Login with credentials
5. **Test Add Friend**: Add a friend by email
6. **Test View Friends**: See friends list
7. **Test Add Expense**: Create an expense
8. **Test View Expenses**: See expense history
9. **Test Balance**: Check balance calculation

### Quick Test Script

```bash
# Terminal 1 - Backend
cd /home/vishal/Downloads/temp_BE
source venv/bin/activate
./run_server.sh

# Terminal 2 - Frontend
cd your-frontend-directory
npm start
```

---

## 🎉 You're All Set!

Your React frontend should now be fully integrated with the FastAPI backend!

### Key Points to Remember:

1. **Backend URL**: http://127.0.0.1:8000
2. **Frontend URL**: http://localhost:3000
3. **Token Storage**: LocalStorage (`access_token`)
4. **CORS**: Already configured
5. **Error Handling**: Use try/catch with axios
6. **Auth**: JWT token in `Authorization: Bearer <token>` header

### Next Steps:

1. Style your components with CSS/Tailwind/Material-UI
2. Add loading states and better error messages
3. Implement real-time updates (optional: WebSockets)
4. Add expense editing/deletion features
5. Deploy to production!

Happy coding! 🚀

