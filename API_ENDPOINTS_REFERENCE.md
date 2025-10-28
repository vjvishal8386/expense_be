# API Endpoints Reference Card

Quick reference for all available API endpoints.

**Base URL**: `http://127.0.0.1:8000`

---

## 🔐 Authentication Endpoints

### Register User
```
POST /auth/register
```
**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe" // optional
}
```
**Response:** (201)
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

---

### Login
```
POST /auth/login
```
**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
**Response:** (200)
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

---

### Get Current User
```
GET /auth/me
Headers: Authorization: Bearer {token}
```
**Response:** (200)
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe"
}
```

---

## 👥 Friends Endpoints

### Get All Friends
```
GET /friends
Headers: Authorization: Bearer {token}
```
**Response:** (200)
```json
[
  {
    "id": "uuid",
    "email": "friend@example.com",
    "name": "Friend Name"
  }
]
```

---

### Add Friend
```
POST /friends
Headers: Authorization: Bearer {token}
```
**Request Body:**
```json
{
  "email": "friend@example.com",
  "name": "Friend Name" // optional
}
```
**Response:** (201)
```json
{
  "id": "uuid",
  "email": "friend@example.com",
  "name": "Friend Name"
}
```

---

## 💰 Expenses Endpoints

### Get Expenses with Friend
```
GET /expenses/{friend_id}
Headers: Authorization: Bearer {token}
```
**Response:** (200)
```json
[
  {
    "id": "uuid",
    "userAId": "uuid",
    "userBId": "uuid",
    "amount": 500.50,
    "description": "Lunch",
    "paidByUserId": "uuid",
    "date": "2025-10-28"
  }
]
```

---

### Create Expense
```
POST /expenses
Headers: Authorization: Bearer {token}
```
**Request Body:**
```json
{
  "friend_id": "uuid",
  "amount": 500.50,
  "description": "Lunch at restaurant",
  "paid_by_user_id": "uuid", // must be current user or friend
  "expense_date": "2025-10-28" // YYYY-MM-DD format
}
```
**Response:** (201)
```json
{
  "id": "uuid",
  "userAId": "uuid",
  "userBId": "uuid",
  "amount": 500.50,
  "description": "Lunch at restaurant",
  "paidByUserId": "uuid",
  "date": "2025-10-28"
}
```

---

### Get Balance with Friend
```
GET /expenses/{friend_id}/balance
Headers: Authorization: Bearer {token}
```
**Response:** (200)
```json
{
  "balance": 300.50
}
```
**Balance Interpretation:**
- **Positive** (e.g., 300.50): Friend owes you ₹300.50
- **Negative** (e.g., -150.00): You owe friend ₹150.00
- **Zero** (0): All settled up!

---

## 🛠️ Utility Endpoints

### Root / API Info
```
GET /
```
**Response:** (200)
```json
{
  "message": "Expense Tracker API is running",
  "version": "1.0.0",
  "docs": "/docs"
}
```

---

### Health Check
```
GET /health
```
**Response:** (200)
```json
{
  "status": "healthy"
}
```

---

## 📖 Interactive Documentation

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

---

## ❌ Common Error Responses

### 400 Bad Request
```json
{
  "detail": "Email already registered"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Friend not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "amount"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

---

## 🔑 Authentication Header Format

All protected endpoints require:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 📝 Notes

- All dates use **ISO 8601 format** (YYYY-MM-DD)
- All amounts are **numbers** (decimals allowed)
- Tokens expire after **7 days**
- UUIDs are **version 4** format
- Timestamps use **UTC timezone**

---

## 🚀 Quick cURL Examples

### Register
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

### Login
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

### Get Friends
```bash
curl -X GET http://127.0.0.1:8000/friends \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create Expense
```bash
curl -X POST http://127.0.0.1:8000/expenses \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "friend_id":"FRIEND_UUID",
    "amount":500,
    "description":"Lunch",
    "paid_by_user_id":"YOUR_UUID",
    "expense_date":"2025-10-28"
  }'
```

---

**Full documentation**: See README.md and FRONTEND_INTEGRATION.md

