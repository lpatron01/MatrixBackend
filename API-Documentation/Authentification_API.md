# API Documentation

## Overview

This is a Django REST Framework API that provides authentication and user management functionality for an educational platform. The API uses JWT (JSON Web Tokens) for authentication and supports role-based access control with different user types.

## Base URL

```
http://localhost:8000/api
```

## Technology Stack

- **Framework**: Django 5.0+ with Django REST Framework 3.15+
- **Authentication**: JWT (djangorestframework-simplejwt 5.3+)
- **Database**: PostgreSQL (via psycopg2-binary)
- **CORS**: django-cors-headers 4.4+
- **Environment Management**: django-environ 0.11+

## Authentication

The API uses JWT token-based authentication. Most endpoints require authentication via Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Token Structure

JWT tokens include the following claims:
- `email`: User's email address
- `role`: User's role (student, teacher, administrator, club_manager)

## User Roles & Permissions

The system supports four user roles with different module access:

### 1. Student (`student`)
**Access to modules:**
- Réclamations (Anonymous secure complaints)
- Documents (Administrative documents & certificates)
- Clubs (Clubs & events)
- Classrooms (Course space)
- Logistics (Equipment & reservations)
- Notifications (Notifications & alerts)

### 2. Teacher (`teacher`)
**Access to modules:**
- Classrooms (Course space)
- Réclamations (Anonymous secure complaints)
- Documents (Administrative documents)
- Notifications (Notifications & alerts)

### 3. Administrator (`administrator`)
**Access to modules:**
- All modules (full access)

### 4. Club Manager (`club_manager`)
**Access to modules:**
- Clubs (Clubs & events)
- Logistics (Equipment & reservations)
- Notifications (Notifications & alerts)

## API Endpoints

### Authentication Endpoints

All authentication endpoints are prefixed with `/api/auth/`

#### 1. Register User

**Endpoint:** `POST /api/auth/register/`

**Authentication:** Not required

**Description:** Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student"
}
```

**Fields:**
- `email` (required, string): User's email address (must be unique)
- `password` (required, string): Password (minimum 8 characters)
- `first_name` (optional, string): User's first name
- `last_name` (optional, string): User's last name
- `role` (optional, string): User role - choices: `student`, `teacher`, `administrator`, `club_manager` (default: `student`)

**Response:** `201 Created`
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student",
  "role_display": "Étudiant",
  "modules": [
    {
      "code": "reclamations",
      "label": "Réclamations anonymes sécurisées",
      "description": "Soumettre, suivre et traiter les tickets sensibles avec chiffrement et audit."
    },
    // ... other modules
  ],
  "is_active": true,
  "is_staff": false,
  "date_joined": "2025-11-26T22:43:57Z"
}
```

---

#### 2. Login

**Endpoint:** `POST /api/auth/login/`

**Authentication:** Not required

**Description:** Authenticate user and receive JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** `200 OK`
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student",
    "role_display": "Étudiant",
    "modules": [...],
    "is_active": true,
    "is_staff": false,
    "date_joined": "2025-11-26T22:43:57Z"
  }
}
```

**Token Usage:**
- `access`: Short-lived token for API requests (include in Authorization header)
- `refresh`: Long-lived token to obtain new access tokens

---

#### 3. Logout

**Endpoint:** `POST /api/auth/logout/`

**Authentication:** Required (Bearer token)

**Description:** Invalidate the refresh token (blacklist it).

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `204 No Content`

**Error Responses:**
- `400 Bad Request`: Missing or invalid refresh token
```json
{
  "detail": "Refresh token is required."
}
```

---

#### 4. Get Current User

**Endpoint:** `GET /api/auth/me/`

**Authentication:** Required (Bearer token)

**Description:** Retrieve the authenticated user's profile information.

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student",
  "role_display": "Étudiant",
  "modules": [
    {
      "code": "reclamations",
      "label": "Réclamations anonymes sécurisées",
      "description": "Soumettre, suivre et traiter les tickets sensibles avec chiffrement et audit."
    }
    // ... other modules based on role
  ],
  "is_active": true,
  "is_staff": false,
  "date_joined": "2025-11-26T22:43:57Z"
}
```

---

#### 5. Change Password

**Endpoint:** `PUT /api/auth/password/change/`

**Authentication:** Required (Bearer token)

**Description:** Change the authenticated user's password.

**Request Body:**
```json
{
  "old_password": "currentpassword123",
  "new_password": "newsecurepassword456"
}
```

**Response:** `200 OK`
```json
{
  "detail": "Password updated successfully."
}
```

**Error Responses:**
- `400 Bad Request`: Invalid old password or weak new password
```json
{
  "old_password": ["Incorrect current password."]
}
```

---

#### 6. Forgot Password

**Endpoint:** `POST /api/auth/password/forgot/`

**Authentication:** Not required

**Description:** Request a password reset email with a reset link.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:** `200 OK`
```json
{
  "detail": "Password reset email sent."
}
```

**Notes:**
- An email will be sent to the user with a reset link containing `uid` and `token` parameters
- The reset link format: `/api/auth/password/reset/?uid=<uid>&token=<token>&email=<email>`
- In development, emails are printed to the console (configured in `.env`)

**Error Responses:**
- `400 Bad Request`: User with email does not exist
```json
{
  "email": ["User with this email does not exist."]
}
```

---

#### 7. Reset Password

**Endpoint:** `POST /api/auth/password/reset/`

**Authentication:** Not required

**Description:** Reset password using the token from the forgot password email.

**Request Body:**
```json
{
  "email": "user@example.com",
  "token": "abc123-token-from-email",
  "new_password": "newsecurepassword789"
}
```

**Response:** `200 OK`
```json
{
  "detail": "Password has been reset."
}
```

**Error Responses:**
- `400 Bad Request`: Invalid or expired token
```json
{
  "token": ["Token is invalid or expired."]
}
