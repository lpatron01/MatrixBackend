# User Management and Authentication API Documentation

## Authentication Endpoints

All authentication endpoints are prefixed with `/api/auth/`.

### 1. Register User

**Endpoint:** `POST /api/auth/register/`

**Authentication:** Not required

**Description:** Register a new user account.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student",
  "cin": 12345678,
  "date_of_birth": "2000-01-01",
  "place_of_birth": "Tunis"
}
```

**Fields:**

- `email` (required, string): User's email address (must be unique)
- `password` (required, string): Password (minimum 8 characters)
- `first_name` (optional, string): User's first name
- `last_name` (optional, string): User's last name
- `role` (optional, string): User role - choices: `student`, `teacher`, `administrator`, `club_manager` (default: `student`)
- `cin` (required, integer): User's CIN (must be unique)
- `date_of_birth` (optional, date): User's date of birth (YYYY-MM-DD)
- `place_of_birth` (optional, string): User's place of birth

**Response:** `201 Created`

```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student",
  "role_display": "Étudiant",
  "cin": 12345678,
  "date_of_birth": "2000-01-01",
  "place_of_birth": "Tunis",
  "is_active": true,
  "is_staff": false,
  "date_joined": "2025-11-26T22:43:57Z"
}
```

### 2. Login User

**Endpoint:** `POST /api/auth/login/`

**Authentication:** Not required

**Description:** Authenticate user and return JWT tokens.

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
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student",
    "role_display": "Étudiant",
    "cin": 12345678,
    "diploma": "Licence en Ingénierie des Systèmes Informatiques",
    "date_of_birth": "2000-01-01",
    "place_of_birth": "Tunis",
    "is_active": true,
    "is_staff": false,
    "date_joined": "2025-11-26T22:43:57Z",
    "education_histories": []
  }
}
```

### 3. Logout User

**Endpoint:** `POST /api/auth/logout/`

**Authentication:** Required (any authenticated user)

**Description:** Blacklist the refresh token to log out the user.

**Request Body:**

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** `204 No Content`

### 4. Get Current User Profile

**Endpoint:** `GET /api/auth/me/`

**Authentication:** Required (any authenticated user)

**Description:** Get the current authenticated user's profile information.

**Response:** `200 OK`

```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "first_name_arabic": "جون",
  "last_name_arabic": "دو",
  "role": "student",
  "role_display": "Étudiant",
  "cin": 12345678,
  "diploma": "Licence en Ingénierie des Systèmes Informatiques",
  "date_of_birth": "2000-01-01",
  "place_of_birth": "Tunis",
  "place_of_birth_arabic": "تونس",
  "is_active": true,
  "is_staff": false,
  "date_joined": "2025-11-26T22:43:57Z",
  "education_histories": []
}
```

### 5. Change Password

**Endpoint:** `PUT /api/auth/password/change/`

**Authentication:** Required (any authenticated user)

**Description:** Change the current user's password.

**Request Body:**

```json
{
  "old_password": "currentpassword123",
  "new_password": "newsecurepassword123"
}
```

**Response:** `200 OK`

```json
{
  "detail": "Password updated successfully."
}
```

### 6. Forgot Password

**Endpoint:** `POST /api/auth/password/forgot/`

**Authentication:** Not required

**Description:** Send a password reset email to the user.

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

### 7. Reset Password

**Endpoint:** `POST /api/auth/password/reset/`

**Authentication:** Not required

**Description:** Reset password using token from email.

**Request Body:**

```json
{
  "email": "user@example.com",
  "token": "reset-token-from-email",
  "new_password": "newsecurepassword123"
}
```

**Response:** `200 OK`

```json
{
  "detail": "Password has been reset."
}
```

---

## User Management Endpoints (CRUD)

All user management endpoints are prefixed with `/api/users/` and require **Admin** permissions.

#### 1. List All Users

**Endpoint:** `GET /api/users/`

**Authentication:** Required (Admin only)

**Description:** Retrieve a list of all users with optional filtering and search.

**Query Parameters:**

- `role` (optional): Filter by role (`student`, `teacher`, `administrator`, `club_manager, scolar_administrator`)
- `is_active` (optional): Filter by active status (`true` or `false`)
- `search` (optional): Search by email, first name, or last name

**Examples:**

```bash
# Get all users
GET /api/users/

# Get all students
GET /api/users/?role=student

# Get all active users
GET /api/users/?is_active=true

# Search for users
GET /api/users/?search=john
```

**Response:** `200 OK`

```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "first_name_arabic": "جون",
    "last_name_arabic": "دو",
    "role": "student",
    "role_display": "Étudiant",
    "cin": 12345678,
    "diploma": "Licence en Ingénierie des Systèmes Informatiques",
    "date_of_birth": "2000-01-01",
    "place_of_birth": "Tunis",
    "place_of_birth_arabic": "تونس",
    "education_histories": [],
    "is_active": true,
    "is_staff": false,
    "date_joined": "2025-11-26T22:43:57Z"
  },
  {
    "id": 2,
    "email": "teacher@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "first_name_arabic": "جين",
    "last_name_arabic": "سميث",
    "role": "teacher",
    "role_display": "Enseignant",
    "cin": 87654321,
    "diploma": "Master Recherche en data science",
    "date_of_birth": "1985-05-15",
    "place_of_birth": "Sfax",
    "place_of_birth_arabic": "صفاقس",
    "education_histories": [],
    "is_active": true,
    "is_staff": false,
    "date_joined": "2025-11-27T10:15:30Z"
  }
]
```

---

#### 2. Create User (Admin)

**Endpoint:** `POST /api/users/create/`

**Authentication:** Required (Admin only)

**Description:** Create a new user account. Unlike the registration endpoint, this allows admins to set additional fields like `is_active` and `is_staff`.

**Request Body:**

```json
{
  "email": "newuser@example.com",
  "password": "securepassword123",
  "first_name": "Alice",
  "last_name": "Johnson",
  "role": "teacher",
  "cin": 11223344,
  "diploma": "Licence en Ingénierie des Systèmes Informatiques",
  "date_of_birth": "1990-03-20",
  "place_of_birth": "Sousse",
  "is_active": true,
  "is_staff": false
}
```

**Fields:**

- `email` (required, string): User's email address (must be unique)
- `password` (optional, string): Password (minimum 8 characters). If not provided, a random password is generated
- `first_name` (optional, string): User's first name
- `last_name` (optional, string): User's last name
- `role` (optional, string): User role - choices: `student`, `teacher`, `administrator`, `club_manager` (default: `student`)
- `cin` (required, integer): User's CIN (must be unique)
- `diploma` (required, string): User's diploma (choices as defined in `User` model)
- `date_of_birth` (optional, date): User's date of birth (YYYY-MM-DD)
- `place_of_birth` (optional, string): User's place of birth
- `is_active` (optional, boolean): Whether the account is active (default: `true`)
- `is_staff` (optional, boolean): Whether the user can access admin panel (default: `false`)

**Response:** `201 Created`

```json
{
  "detail": "User created successfully.",
  "user": {
    "id": 3,
    "email": "newuser@example.com",
    "first_name": "Alice",
    "last_name": "Johnson",
    "role": "teacher",
    "role_display": "Enseignant",
    "cin": 11223344,
    "diploma": "Licence en Ingénierie des Systèmes Informatiques",
    "date_of_birth": "1990-03-20",
    "place_of_birth": "Sousse",
    "education_histories": [],
    "is_active": true,
    "is_staff": false,
    "date_joined": "2025-11-27T20:10:00Z"
  }
}
```

**Error Responses:**

- `400 Bad Request`: Invalid data or duplicate email

```json
{
  "email": ["User with this email already exists."]
}
```

---

#### 3. Get User Details

**Endpoint:** `GET /api/users/<id>/`

**Authentication:** Required (Admin only)

**Description:** Retrieve detailed information about a specific user by their ID.

**Example:**

```bash
GET /api/users/1/
```

**Response:** `200 OK`

```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "first_name_arabic": "جون",
  "last_name_arabic": "دو",
  "role": "student",
  "role_display": "Étudiant",
  "cin": 12345678,
  "diploma": "Licence en Ingénierie des Systèmes Informatiques",
  "date_of_birth": "2000-01-01",
  "place_of_birth": "Tunis",
  "place_of_birth_arabic": "تونس",
  "education_histories": [
    {
      "id": 1,
      "academic_year": "2023-2024",
      "registration_id": 12345,
      "grade": "1",
      "grade_display": "Première année",
      "specialty": "Informatique",
      "class_name": "L3-A",
      "session": "principale",
      "session_display": "Principale",
      "result": "tres_bien",
      "result_display": "Très Bien"
    }
  ],
  "is_active": true,
  "is_staff": false,
  "date_joined": "2025-11-26T22:43:57Z"
}
```

**Error Responses:**

- `404 Not Found`: User with specified ID does not exist

```json
{
  "detail": "Not found."
}
```

---

#### 4. Update User

**Endpoint:** `PUT /api/users/<id>/update/` or `PATCH /api/users/<id>/update/`

**Authentication:** Required (Admin only)

**Description:** Update user details. Use `PUT` for full updates or `PATCH` for partial updates.

**Request Body (PUT - all fields required except password):**

```json
{
  "first_name": "John",
  "last_name": "Doe Updated",
  "role": "teacher",
  "is_active": true,
  "is_staff": false
}
```

**Request Body (PATCH - only fields to update):**

```json
{
  "role": "administrator",
  "cin": 99887766,
  "is_staff": true
}
```

**Fields:**

- `email` (read-only): Email cannot be changed
- `password` (optional, string): New password (minimum 8 characters)
- `first_name` (optional, string): User's first name
- `last_name` (optional, string): User's last name
- `first_name_arabic` (optional, string): User's first name in Arabic
- `last_name_arabic` (optional, string): User's last name in Arabic
- `role` (optional, string): User role
- `cin` (optional, integer): User's CIN
- `diploma` (optional, string): User's diploma
- `date_of_birth` (optional, date): User's date of birth
- `place_of_birth` (optional, string): User's place of birth
- `is_active` (optional, boolean): Account active status
- `is_staff` (optional, boolean): Admin panel access

**Response:** `200 OK`

```json
{
  "detail": "User updated successfully.",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe Updated",
    "first_name_arabic": "جون",
    "last_name_arabic": "دو",
    "role": "teacher",
    "role_display": "Enseignant",
    "cin": 11223344,
    "diploma": "Licence en Ingénierie des Systèmes Informatiques",
    "date_of_birth": "1990-03-20",
    "place_of_birth": "Sousse",
    "place_of_birth_arabic": "سوسة",
    "education_histories": [],
    "is_active": true,
    "is_staff": false,
    "date_joined": "2025-11-26T22:43:57Z"
  }
}
```

**Error Responses:**

- `404 Not Found`: User does not exist
- `400 Bad Request`: Invalid data

---

#### 5. Delete User

**Endpoint:** `DELETE /api/users/<id>/delete/`

**Authentication:** Required (Admin only)

**Description:** Permanently delete a user account.

**Example:**

```bash
DELETE /api/users/1/delete/
```

**Response:** `200 OK`

```json
{
  "detail": "User 'user@example.com' deleted successfully."
}
```

**Error Responses:**

- `404 Not Found`: User with specified ID does not exist

```json
{
  "detail": "Not found."
}
```

**Warning:** This action is permanent and cannot be undone. Consider deactivating users instead by setting `is_active` to `false`.

---

### Education History Endpoints

All education history endpoints are prefixed with `/api/users/<user_pk>/education-history/` and require **Admin** permissions.

#### 1. List All Education History Records for a User

**Endpoint:** `GET /api/users/<user_pk>/education-history/`

**Authentication:** Required (Admin only)

**Description:** Retrieve a list of all education history records for a specific user. The `<user_pk>` in the URL should be replaced with the ID of the user.

**Example:**

```bash
GET /api/users/1/education-history/
```

**Response:** `200 OK`

```json
[
  {
    "id": 1,
    "academic_year": "2023-2024",
    "registration_id": 12345,
    "grade": "1",
    "grade_display": "Première année",
    "specialty": "Informatique",
    "class_name": "L3-A",
    "session": "principale",
    "session_display": "Principale",
    "result": "tres_bien",
    "result_display": "Très Bien"
  }
]
```

---

#### 2. Create Education History Record for a User

**Endpoint:** `POST /api/users/<user_pk>/education-history/create/`

**Authentication:** Required (Admin only)

**Description:** Create a new education history record for a specific user. Only students can have education history. The `<user_pk>` in the URL should be replaced with the ID of the student.

**Request Body:**

```json
{
  "academic_year": "2024-2025",
  "registration_id": 67890,
  "grade": "2",
  "specialty": "Informatique",
  "class_name": "L3-B",
  "session": "principale",
  "result": "bien"
}
```

**Fields:**

- `academic_year` (required, string): Academic year (e.g., "2023-2024")
- `registration_id` (required, integer): Registration ID
- `grade` (required, string): Grade (choices: `1`, `2`, `3`)
- `specialty` (required, string): Specialty
- `class_name` (required, string): Class name
- `session` (required, string): Session (choices: `principale`, `controle`)
- `result` (required, string): Result (choices: `tres_bien`, `bien`, `assez_bien`, `passable`, `ajourne`)

**Response:** `201 Created`

```json
{
  "id": 2,
  "academic_year": "2024-2025",
  "registration_id": 67890,
  "grade": "2",
  "grade_display": "Deuxième année",
  "specialty": "Informatique",
  "class_name": "L3-B",
  "session": "principale",
  "session_display": "Principale",
  "result": "bien",
  "result_display": "Bien"
}
```

**Error Responses:**

- `400 Bad Request`: Invalid data or user is not a student.

---

#### 3. Get Education History Details for a User

**Endpoint:** `GET /api/users/<user_pk>/education-history/<pk>/`

**Authentication:** Required (Admin only)

**Description:** Retrieve detailed information about a specific education history record for a user. The `<user_pk>` in the URL should be replaced with the ID of the user, and `<pk>` with the ID of the education history record.

**Example:**

```bash
GET /api/users/1/education-history/1/
```

**Response:** `200 OK`

```json
{
  "id": 1,
  "academic_year": "2023-2024",
  "registration_id": 12345,
  "grade": "1",
  "grade_display": "Première année",
  "specialty": "Informatique",
  "class_name": "L3-A",
  "session": "principale",
  "session_display": "Principale",
  "result": "tres_bien",
  "result_display": "Très Bien"
}
```

**Error Responses:**

- `404 Not Found`: Education history record not found.

---

#### 4. Update Education History Record for a User

**Endpoint:** `PUT /api/users/<user_pk>/education-history/<pk>/update/` or `PATCH /api/users/<user_pk>/education-history/<pk>/update/`

**Authentication:** Required (Admin only)

**Description:** Update an education history record for a specific user. Use `PUT` for full updates or `PATCH` for partial updates. The `<user_pk>` in the URL should be replaced with the ID of the user, and `<pk>` with the ID of the education history record.

**Request Body (PATCH - only fields to update):**

```json
{
  "result": "assez_bien"
}
```

**Fields:** (Same as create, all are optional for PATCH, all are required for PUT except `student`)

**Response:** `200 OK`

```json
{
  "id": 1,
  "academic_year": "2023-2024",
  "registration_id": 12345,
  "grade": "1",
  "grade_display": "Première année",
  "specialty": "Informatique",
  "class_name": "L3-A",
  "session": "principale",
  "session_display": "Principale",
  "result": "assez_bien",
  "result_display": "Assez Bien"
}
```

**Error Responses:**

- `404 Not Found`: Education history record not found.
- `400 Bad Request`: Invalid data.

---

#### 5. Delete Education History Record for a User

**Endpoint:** `DELETE /api/users/<user_pk>/education-history/<pk>/delete/`

**Authentication:** Required (Admin only)

**Description:** Delete a specific education history record for a user. The `<user_pk>` in the URL should be replaced with the ID of the user, and `<pk>` with the ID of the education history record.

**Example:**

```bash
DELETE /api/users/1/education-history/1/delete/
```

**Response:** `200 OK`

```json
{
  "detail": "Education history record for 'user@example.com' for academic year '2023-2024' deleted successfully."
}
```

**Error Responses:**

- `404 Not Found`: Education history record not found.

---

## User Model

### Fields

| Field                     | Type     | Description                                                             |
| ------------------------- | -------- | ----------------------------------------------------------------------- |
| `id`                    | Integer  | Unique identifier (auto-generated)                                      |
| `email`                 | String   | User's email address (unique, used for login)                           |
| `first_name`            | String   | User's first name (optional)                                            |
| `last_name`             | String   | User's last name (optional)                                             |
| `first_name_arabic`     | String   | User's first name in Arabic (optional)                                  |
| `last_name_arabic`      | String   | User's last name in Arabic (optional)                                   |
| `role`                  | String   | User role:`student`, `teacher`, `administrator`, `club_manager` |
| `role_display`          | String   | Human-readable role name (read-only)                                    |
| `cin`                   | Integer  | User's CIN (unique)                                                     |
| `diploma`               | String   | User's diploma                                                          |
| `date_of_birth`         | Date     | User's date of birth                                                    |
| `place_of_birth`        | String   | User's place of birth                                                   |
| `place_of_birth_arabic` | String   | User's place of birth in Arabic (optional)                              |
| `education_histories`   | Array    | List of education history records (read-only)                           |
| `is_active`             | Boolean  | Whether the user account is active                                      |
| `is_staff`              | Boolean  | Whether the user can access admin panel                                 |
| `date_joined`           | DateTime | Account creation timestamp                                              |
