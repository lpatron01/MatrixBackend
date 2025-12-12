

### User Management Endpoints (CRUD)

All user management endpoints are prefixed with `/api/users/` and require **Admin** permissions.

#### 1. List All Users

**Endpoint:** `GET /api/users/`

**Authentication:** Required (Admin only)

**Description:** Retrieve a list of all users with optional filtering and search.

**Query Parameters:**
- `role` (optional): Filter by role (`student`, `teacher`, `administrator`, `club_manager`)
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
    "role": "student",
    "role_display": "Étudiant",
    "cin": 12345678,
    "speciality": "Informatique",
    "class_name": "L3-A",
    "date_of_birth": "2000-01-01",
    "place_of_birth": "Tunis",
    "modules": [...],
    "is_active": true,
    "is_staff": false,
    "date_joined": "2025-11-26T22:43:57Z"
  },
  {
    "id": 2,
    "email": "teacher@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "role": "teacher",
    "role_display": "Enseignant",
    "cin": 87654321,
    "speciality": "Mathématiques",
    "class_name": "",
    "date_of_birth": "1985-05-15",
    "place_of_birth": "Sfax",
    "modules": [...],
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
  "speciality": "Physique",
  "class_name": "",
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
- `speciality` (optional, string): User's speciality
- `class_name` (optional, string): User's class name
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
    "speciality": "Physique",
    "class_name": "",
    "date_of_birth": "1990-03-20",
    "place_of_birth": "Sousse",
    "modules": [...],
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
  "role": "student",
  "role_display": "Étudiant",
  "cin": 12345678,
  "speciality": "Informatique",
  "class_name": "L3-A",
  "date_of_birth": "2000-01-01",
  "place_of_birth": "Tunis",
  "modules": [
    {
      "code": "reclamations",
      "label": "Réclamations anonymes sécurisées",
      "description": "Soumettre, suivre et traiter les tickets sensibles avec chiffrement et audit."
    }
    // ... other modules
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
- `role` (optional, string): User role
- `cin` (optional, integer): User's CIN
- `speciality` (optional, string): User's speciality
- `class_name` (optional, string): User's class name
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
    "role": "teacher",
    "role_display": "Enseignant",
    "cin": 11223344,
    "speciality": "Physique",
    "class_name": "",
    "date_of_birth": "1990-03-20",
    "place_of_birth": "Sousse",
    "modules": [...],
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

## User Model

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Unique identifier (auto-generated) |
| `email` | String | User's email address (unique, used for login) |
| `first_name` | String | User's first name (optional) |
| `last_name` | String | User's last name (optional) |
| `role` | String | User role: `student`, `teacher`, `administrator`, `club_manager` |
| `role_display` | String | Human-readable role name (read-only) |
| `modules` | Array | Available modules based on role (read-only) |
| `is_active` | Boolean | Whether the user account is active |
| `is_staff` | Boolean | Whether the user can access admin panel |
| `date_joined` | DateTime | Account creation timestamp |
| `cin` | Integer | User's CIN (unique) |
| `speciality` | String | User's speciality |
| `class_name` | String | User's class name |
| `date_of_birth` | Date | User's date of birth |
| `place_of_birth` | String | User's place of birth |



