# Schedule & Attendance API Documentation

## Base URL
`/api/schedule/`

## Authentication
All endpoints require JWT authentication (`Bearer <token>`).

---

## Endpoints Overview

### Student Groups
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/groups/` | List all groups | All users |
| POST | `/groups/` | Create a group | Admin only |
| GET | `/groups/{id}/` | Get group details | Admin only |
| PUT/PATCH | `/groups/{id}/` | Update a group | Admin only |
| DELETE | `/groups/{id}/` | Delete a group | Admin only |

### Subjects
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/subjects/` | List all subjects | All users |
| POST | `/subjects/` | Create a subject | Admin only |
| GET | `/subjects/{id}/` | Get subject details | Admin only |
| PUT/PATCH | `/subjects/{id}/` | Update a subject | Admin only |
| DELETE | `/subjects/{id}/` | Delete a subject | Admin only |

### Sessions (Schedule)
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/sessions/` | List sessions (filtered by role) | All users |
| POST | `/sessions/` | Create a session | Admin only |
| GET | `/sessions/{id}/` | Get session details | Admin only |
| PUT/PATCH | `/sessions/{id}/` | Update a session | Admin only |
| DELETE | `/sessions/{id}/` | Delete a session | Admin only |
| GET | `/my-schedule/` | Get user's weekly schedule | All users |

### Attendance
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/attendance/` | List attendance records | Role-filtered |
| POST | `/attendance/mark/` | Mark bulk attendance | Teachers/Admin |
| GET | `/sessions/{id}/students/` | Get students for a session | Teachers/Admin |
| GET | `/my-absences/` | Get student's absences summary | Students only |

### Group Membership
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/memberships/` | List all memberships | Admin only |
| POST | `/memberships/` | Add student to group | Admin only |
| GET | `/memberships/{id}/` | Get membership details | Admin only |
| DELETE | `/memberships/{id}/` | Remove student from group | Admin only |
| GET | `/my-group/` | Get student's groups | Students only |

---

## Data Models

### StudentGroup
```json
{
  "id": 1,
  "name": "2INFO-A",
  "description": "Classe 2ème année Informatique groupe A",
  "level": "L2",
  "specialty": "Informatique",
  "members_count": 25,
  "created_at": "2024-12-01T10:00:00Z"
}
```

### Subject
```json
{
  "id": 1,
  "name": "Programmation Avancée",
  "code": "INF201",
  "description": "Cours de programmation orientée objet",
  "coefficient": 3.0,
  "hours_cours": 21,
  "hours_td": 21,
  "hours_tp": 21,
  "created_at": "2024-12-01T10:00:00Z"
}
```

### Session
```json
{
  "id": 1,
  "subject_name": "Programmation Avancée",
  "subject_code": "INF201",
  "teacher_name": "Dr. Ahmed Ben Ali",
  "group_name": "2INFO-A",
  "session_type": "COURS",
  "session_type_display": "Cours Magistral",
  "day_of_week": 1,
  "day_of_week_display": "Lundi",
  "start_time": "08:30:00",
  "end_time": "10:00:00",
  "room": "Amphi A",
  "is_active": true
}
```

### Session Types
- `COURS` - Cours Magistral
- `TD` - Travaux Dirigés
- `TP` - Travaux Pratiques
- `EXAMEN` - Examen
- `RATTRAPAGE` - Rattrapage

### Day of Week
- `1` - Lundi
- `2` - Mardi
- `3` - Mercredi
- `4` - Jeudi
- `5` - Vendredi
- `6` - Samedi
- `0` - Dimanche

### Attendance
```json
{
  "id": 1,
  "session": { ... },
  "student": { ... },
  "date": "2024-12-12",
  "status": "PRESENT",
  "status_display": "Présent",
  "is_justified": false,
  "justification": null,
  "marked_by_name": "Dr. Ahmed Ben Ali",
  "marked_at": "2024-12-12T10:30:00Z"
}
```

### Attendance Status
- `PRESENT` - Présent
- `ABSENT` - Absent
- `LATE` - En retard
- `EXCUSED` - Excusé

---

## Usage Examples

### Get Student's Weekly Schedule
```bash
GET /api/schedule/my-schedule/
Authorization: Bearer <student_token>
```

Response:
```json
{
  "1": [  // Monday
    {
      "id": 1,
      "subject_name": "Mathématiques",
      "session_type": "COURS",
      "start_time": "08:30:00",
      "end_time": "10:00:00",
      "room": "Salle A1",
      "teacher_name": "Dr. Ahmed"
    }
  ],
  "2": [ ... ],
  ...
}
```

### Mark Attendance (Teacher)
```bash
POST /api/schedule/attendance/mark/
Authorization: Bearer <teacher_token>
Content-Type: application/json

{
  "session_id": 1,
  "date": "2024-12-12",
  "attendances": [
    { "student_id": "5", "status": "PRESENT" },
    { "student_id": "6", "status": "ABSENT" },
    { "student_id": "7", "status": "LATE" }
  ]
}
```

### Get Student's Absences
```bash
GET /api/schedule/my-absences/
Authorization: Bearer <student_token>
```

Response:
```json
{
  "total_sessions": 50,
  "total_absences": 3,
  "justified_absences": 1,
  "unjustified_absences": 2,
  "presence_rate": 94.00,
  "absences": [ ... ]
}
```

### Create Session (Admin)
```bash
POST /api/schedule/sessions/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "subject_id": 1,
  "teacher_id": 3,
  "group_id": 1,
  "session_type": "TD",
  "day_of_week": 2,
  "start_time": "10:15:00",
  "end_time": "11:45:00",
  "room": "Salle TD1",
  "semester": "S1",
  "academic_year": "2024-2025"
}
```
