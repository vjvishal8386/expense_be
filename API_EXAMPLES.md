# API Examples

Complete examples for testing all endpoints of the Expense Tracker API.

## Base URL
```
http://127.0.0.1:8000
```

## 1. Health Check

### Request
```bash
curl -X GET http://127.0.0.1:8000/health
```

### Response
```json
{
  "status": "healthy"
}
```

---

## 2. User Registration

### Request
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "vishal@gmail.com",
    "password": "securepassword123",
    "name": "Vishal"
  }'
```

### Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "vishal@gmail.com",
    "name": "Vishal"
  }
}
```

**Save the `access_token` for subsequent requests!**

---

## 3. User Login

### Request
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "vishal@gmail.com",
    "password": "securepassword123"
  }'
```

### Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "vishal@gmail.com",
    "name": "Vishal"
  }
}
```

---

## 4. Get Current User

### Request
```bash
curl -X GET http://127.0.0.1:8000/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Response
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "vishal@gmail.com",
  "name": "Vishal"
}
```

---

## 5. Add Friend

### Request
```bash
curl -X POST http://127.0.0.1:8000/friends \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "tushar@example.com",
    "name": "Tushar"
  }'
```

### Response
```json
{
  "id": "987e6543-e89b-12d3-a456-426614174001",
  "email": "tushar@example.com",
  "name": "Tushar"
}
```

**Save the friend's `id` for expense operations!**

### Notes
- If the friend doesn't exist as a user, a pending account is created
- Friendship is bidirectional (both users see each other as friends)
- Cannot add yourself as a friend

---

## 6. Get Friends List

### Request
```bash
curl -X GET http://127.0.0.1:8000/friends \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Response
```json
[
  {
    "id": "987e6543-e89b-12d3-a456-426614174001",
    "email": "tushar@example.com",
    "name": "Tushar"
  },
  {
    "id": "456e7890-e89b-12d3-a456-426614174002",
    "email": "amit@example.com",
    "name": "Amit"
  }
]
```

---

## 7. Create Expense

### Request
```bash
curl -X POST http://127.0.0.1:8000/expenses \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "friend_id": "987e6543-e89b-12d3-a456-426614174001",
    "amount": 500.50,
    "description": "Lunch at restaurant",
    "paid_by_user_id": "123e4567-e89b-12d3-a456-426614174000",
    "expense_date": "2025-10-28"
  }'
```

### Response
```json
{
  "id": "111e2222-e89b-12d3-a456-426614174003",
  "userAId": "123e4567-e89b-12d3-a456-426614174000",
  "userBId": "987e6543-e89b-12d3-a456-426614174001",
  "amount": 500.50,
  "description": "Lunch at restaurant",
  "paidByUserId": "123e4567-e89b-12d3-a456-426614174000",
  "date": "2025-10-28"
}
```

### Notes
- `paid_by_user_id` must be either current user or friend
- `amount` must be greater than 0
- `description` cannot be empty
- `expense_date` format: YYYY-MM-DD

---

## 8. Get Expenses with Friend

### Request
```bash
curl -X GET http://127.0.0.1:8000/expenses/987e6543-e89b-12d3-a456-426614174001 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Response
```json
[
  {
    "id": "111e2222-e89b-12d3-a456-426614174003",
    "userAId": "123e4567-e89b-12d3-a456-426614174000",
    "userBId": "987e6543-e89b-12d3-a456-426614174001",
    "amount": 500.50,
    "description": "Lunch at restaurant",
    "paidByUserId": "123e4567-e89b-12d3-a456-426614174000",
    "date": "2025-10-28"
  },
  {
    "id": "222e3333-e89b-12d3-a456-426614174004",
    "userAId": "987e6543-e89b-12d3-a456-426614174001",
    "userBId": "123e4567-e89b-12d3-a456-426614174000",
    "amount": 200.00,
    "description": "Coffee",
    "paidByUserId": "987e6543-e89b-12d3-a456-426614174001",
    "date": "2025-10-27"
  }
]
```

### Notes
- Returns expenses in descending order (newest first)
- Shows expenses regardless of who created them
- Works bidirectionally

---

## 9. Get Balance with Friend

### Request
```bash
curl -X GET http://127.0.0.1:8000/expenses/987e6543-e89b-12d3-a456-426614174001/balance \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Response
```json
{
  "balance": 300.50
}
```

### Balance Interpretation
- **Positive balance (e.g., 300.50)**: Friend owes you ₹300.50
- **Negative balance (e.g., -150.25)**: You owe friend ₹150.25
- **Zero balance (0)**: All settled up!

### Calculation Logic
```
balance = (expenses you paid) - (expenses friend paid)
```

Example:
- You paid ₹500.50 for lunch
- Friend paid ₹200.00 for coffee
- Balance = 500.50 - 200.00 = **₹300.50** (friend owes you)

---

## Complete Test Flow

### Step 1: Register two users

**User A (Vishal)**
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "vishal@gmail.com", "password": "pass123", "name": "Vishal"}'
```
Save token as `TOKEN_A`

**User B (Tushar)**
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "tushar@example.com", "password": "pass123", "name": "Tushar"}'
```
Save token as `TOKEN_B` and user ID as `USER_B_ID`

### Step 2: User A adds User B as friend

```bash
curl -X POST http://127.0.0.1:8000/friends \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"email": "tushar@example.com", "name": "Tushar"}'
```

### Step 3: User A creates expense (paid by A)

```bash
curl -X POST http://127.0.0.1:8000/expenses \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{
    "friend_id": "'$USER_B_ID'",
    "amount": 500,
    "description": "Lunch",
    "paid_by_user_id": "'$USER_A_ID'",
    "expense_date": "2025-10-28"
  }'
```

### Step 4: Check balance (User A perspective)

```bash
curl -X GET http://127.0.0.1:8000/expenses/$USER_B_ID/balance \
  -H "Authorization: Bearer $TOKEN_A"
```
**Expected**: `{"balance": 500}` (Tushar owes Vishal ₹500)

### Step 5: User B views expenses

```bash
curl -X GET http://127.0.0.1:8000/expenses/$USER_A_ID \
  -H "Authorization: Bearer $TOKEN_B"
```
**Expected**: Shows the lunch expense

### Step 6: User B creates expense (paid by B)

```bash
curl -X POST http://127.0.0.1:8000/expenses \
  -H "Authorization: Bearer $TOKEN_B" \
  -H "Content-Type: application/json" \
  -d '{
    "friend_id": "'$USER_A_ID'",
    "amount": 150,
    "description": "Coffee",
    "paid_by_user_id": "'$USER_B_ID'",
    "expense_date": "2025-10-28"
  }'
```

### Step 7: Check updated balance

```bash
curl -X GET http://127.0.0.1:8000/expenses/$USER_B_ID/balance \
  -H "Authorization: Bearer $TOKEN_A"
```
**Expected**: `{"balance": 350}` (500 - 150 = 350, Tushar owes Vishal ₹350)

---

## Error Responses

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

## Using Postman

### Import as Collection

1. Create new collection "Expense Tracker"
2. Add environment variable:
   - `base_url`: `http://127.0.0.1:8000`
   - `token`: (set after login)

3. For authenticated requests, add header:
   - Key: `Authorization`
   - Value: `Bearer {{token}}`

### Sample Postman Requests

**Register**
- Method: POST
- URL: `{{base_url}}/auth/register`
- Body: raw JSON

**Get Friends**
- Method: GET
- URL: `{{base_url}}/friends`
- Headers: `Authorization: Bearer {{token}}`

---

## Using Python Requests

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

# Register
response = requests.post(
    f"{BASE_URL}/auth/register",
    json={"email": "user@example.com", "password": "pass123"}
)
token = response.json()["access_token"]

# Get friends
response = requests.get(
    f"{BASE_URL}/friends",
    headers={"Authorization": f"Bearer {token}"}
)
friends = response.json()

# Create expense
response = requests.post(
    f"{BASE_URL}/expenses",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "friend_id": "friend-uuid",
        "amount": 100,
        "description": "Dinner",
        "paid_by_user_id": "your-uuid",
        "expense_date": "2025-10-28"
    }
)
```

---

## Tips

1. **Save tokens**: Store access tokens for testing multiple endpoints
2. **Use Swagger UI**: Visit `/docs` for interactive testing
3. **Check response codes**: 
   - 200/201 = Success
   - 400 = Bad request
   - 401 = Unauthorized
   - 404 = Not found
   - 422 = Validation error
4. **Date format**: Always use ISO format (YYYY-MM-DD)
5. **UUIDs**: Save user and friend IDs for creating expenses

---

## Quick Test Script

```bash
#!/bin/bash

BASE="http://127.0.0.1:8000"

# Register
TOKEN=$(curl -s -X POST $BASE/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' \
  | jq -r '.access_token')

echo "Token: $TOKEN"

# Get friends
curl -s -X GET $BASE/friends \
  -H "Authorization: Bearer $TOKEN" | jq

# Health check
curl -s $BASE/health | jq
```

Happy testing! 🚀

