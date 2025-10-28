# Frontend Quick Start - Integration Cheatsheet

Quick reference for integrating your React frontend with this FastAPI backend.

## 🚀 Setup (5 Minutes)

### 1. Backend
```bash
cd /home/vishal/Downloads/temp_BE
source venv/bin/activate
./run_server.sh
```
✅ Backend: http://127.0.0.1:8000

### 2. Frontend
```bash
cd your-frontend-app
npm install axios
echo "REACT_APP_API_BASE_URL=http://127.0.0.1:8000" > .env
npm start
```
✅ Frontend: http://localhost:3000

---

## 📁 Recommended Frontend Structure

```
your-frontend-app/
├── src/
│   ├── api/
│   │   ├── config.ts           # API base URL, endpoints
│   │   ├── axios.ts            # Axios instance with interceptors
│   │   ├── authService.ts      # Auth API calls
│   │   ├── friendsService.ts   # Friends API calls
│   │   └── expensesService.ts  # Expenses API calls
│   ├── context/
│   │   └── AuthContext.tsx     # Auth state management
│   ├── components/
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── FriendsList.tsx
│   │   ├── AddFriend.tsx
│   │   ├── ExpensesView.tsx
│   │   └── AddExpense.tsx
│   ├── types/
│   │   └── index.ts            # TypeScript interfaces
│   └── App.tsx
└── .env
```

---

## 🔑 Authentication (Copy-Paste Ready)

### Setup Axios with Auth

```typescript
// src/api/axios.ts
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;
```

### Login Function

```typescript
// Usage in your component
import api from './api/axios';

const login = async (email: string, password: string) => {
  const { data } = await api.post('/auth/login', { email, password });
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('user', JSON.stringify(data.user));
  return data.user;
};
```

### Register Function

```typescript
const register = async (email: string, password: string, name?: string) => {
  const { data } = await api.post('/auth/register', { email, password, name });
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('user', JSON.stringify(data.user));
  return data.user;
};
```

### Logout Function

```typescript
const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  window.location.href = '/login';
};
```

---

## 👥 Friends API (Copy-Paste Ready)

### Get All Friends

```typescript
import api from './api/axios';

const getFriends = async () => {
  const { data } = await api.get('/friends');
  return data; // Array of Friend objects
};
```

### Add Friend

```typescript
const addFriend = async (email: string, name?: string) => {
  const { data } = await api.post('/friends', { email, name });
  return data; // Friend object
};
```

---

## 💰 Expenses API (Copy-Paste Ready)

### Get Expenses with Friend

```typescript
const getExpenses = async (friendId: string) => {
  const { data } = await api.get(`/expenses/${friendId}`);
  return data; // Array of Expense objects
};
```

### Create Expense

```typescript
const createExpense = async (
  friendId: string,
  amount: number,
  description: string,
  paidByMe: boolean
) => {
  const userId = JSON.parse(localStorage.getItem('user')!).id;
  
  const { data } = await api.post('/expenses', {
    friend_id: friendId,
    amount,
    description,
    paid_by_user_id: paidByMe ? userId : friendId,
    expense_date: new Date().toISOString().split('T')[0],
  });
  return data;
};
```

### Get Balance

```typescript
const getBalance = async (friendId: string) => {
  const { data } = await api.get(`/expenses/${friendId}/balance`);
  return data.balance; // number: positive = friend owes you, negative = you owe friend
};
```

---

## 📝 TypeScript Interfaces

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
```

---

## 🎨 React Component Examples

### Login Component (Minimal)

```tsx
import { useState } from 'react';
import api from '../api/axios';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const { data } = await api.post('/auth/login', { email, password });
      localStorage.setItem('access_token', data.access_token);
      window.location.href = '/dashboard';
    } catch (error) {
      alert('Login failed');
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input type="email" value={email} onChange={e => setEmail(e.target.value)} />
      <input type="password" value={password} onChange={e => setPassword(e.target.value)} />
      <button type="submit">Login</button>
    </form>
  );
}
```

### Friends List Component (Minimal)

```tsx
import { useEffect, useState } from 'react';
import api from '../api/axios';

export default function FriendsList() {
  const [friends, setFriends] = useState([]);

  useEffect(() => {
    api.get('/friends').then(res => setFriends(res.data));
  }, []);

  return (
    <ul>
      {friends.map((friend: any) => (
        <li key={friend.id}>{friend.name || friend.email}</li>
      ))}
    </ul>
  );
}
```

### Add Expense Component (Minimal)

```tsx
import { useState } from 'react';
import api from '../api/axios';

export default function AddExpense({ friendId, onAdded }: any) {
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [paidByMe, setPaidByMe] = useState(true);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const userId = JSON.parse(localStorage.getItem('user')!).id;
    
    await api.post('/expenses', {
      friend_id: friendId,
      amount: parseFloat(amount),
      description,
      paid_by_user_id: paidByMe ? userId : friendId,
      expense_date: new Date().toISOString().split('T')[0],
    });
    
    setAmount('');
    setDescription('');
    onAdded();
  };

  return (
    <form onSubmit={handleSubmit}>
      <input 
        type="number" 
        placeholder="Amount" 
        value={amount} 
        onChange={e => setAmount(e.target.value)} 
      />
      <input 
        type="text" 
        placeholder="Description" 
        value={description} 
        onChange={e => setDescription(e.target.value)} 
      />
      <select value={paidByMe ? 'me' : 'friend'} onChange={e => setPaidByMe(e.target.value === 'me')}>
        <option value="me">I paid</option>
        <option value="friend">Friend paid</option>
      </select>
      <button type="submit">Add Expense</button>
    </form>
  );
}
```

---

## ⚡ Quick Testing

### Test in Browser Console

```javascript
// Test login
fetch('http://127.0.0.1:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'test@example.com', password: 'test123' })
})
.then(r => r.json())
.then(data => {
  console.log('Token:', data.access_token);
  localStorage.setItem('access_token', data.access_token);
});

// Test get friends (after login)
fetch('http://127.0.0.1:8000/friends', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
})
.then(r => r.json())
.then(console.log);
```

---

## 🔧 Common Issues & Fixes

### CORS Error
✅ **Already fixed** - Backend has CORS enabled for localhost:3000

### 401 Unauthorized
```typescript
// Make sure token is included in headers
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
```

### Token Expired
```typescript
// Clear storage and redirect to login
localStorage.clear();
window.location.href = '/login';
```

---

## 📊 Balance Display Helper

```typescript
const formatBalance = (balance: number, friendName: string) => {
  if (balance > 0) {
    return `${friendName} owes you ₹${balance.toFixed(2)}`;
  } else if (balance < 0) {
    return `You owe ${friendName} ₹${Math.abs(balance).toFixed(2)}`;
  }
  return `All settled up with ${friendName}!`;
};
```

---

## 🎯 Complete Flow Example

```typescript
// 1. User registers
await api.post('/auth/register', { 
  email: 'user@example.com', 
  password: 'pass123' 
});

// 2. User adds friend
await api.post('/friends', { 
  email: 'friend@example.com', 
  name: 'Friend Name' 
});

// 3. Get friends list
const friends = await api.get('/friends');
const friendId = friends.data[0].id;

// 4. Create expense
await api.post('/expenses', {
  friend_id: friendId,
  amount: 500,
  description: 'Lunch',
  paid_by_user_id: userId,
  expense_date: '2025-10-28'
});

// 5. Get balance
const balance = await api.get(`/expenses/${friendId}/balance`);
console.log('Balance:', balance.data.balance);

// 6. Get expenses
const expenses = await api.get(`/expenses/${friendId}`);
console.log('Expenses:', expenses.data);
```

---

## 🚀 Ready to Code!

1. ✅ Backend running on http://127.0.0.1:8000
2. ✅ Frontend running on http://localhost:3000
3. ✅ Copy-paste the code snippets above
4. ✅ Test with Swagger UI: http://127.0.0.1:8000/docs

**Full integration guide**: See `FRONTEND_INTEGRATION.md`

Happy coding! 🎉

