# Clubs API Documentation

## Base URL
`/api/clubs/`

## Authentication
All endpoints require JWT Bearer token authentication.

---

## Clubs

### List/Create Clubs
`GET /api/clubs/` - List all clubs (filtered by role)  
`POST /api/clubs/` - Create a new club

**Query Parameters:**
- `status` - Filter by status (pending, active, inactive, rejected)
- `search` - Search by name/description

**Create Request Body:**
```json
{
    "name": "Club Informatique",
    "description": "Club dédié à l'informatique",
    "logo": "<file upload>"
}
```

### Get/Update/Delete Club
`GET /api/clubs/<uuid:public_id>/` - Get club details  
`PATCH /api/clubs/<uuid:public_id>/` - Update club  
`DELETE /api/clubs/<uuid:public_id>/` - Delete club

**Update Request Body:**
```json
{
    "name": "Nouveau nom",
    "description": "Nouvelle description",
    "logo": "<file upload>",
    "status": "active",
    "members_count": 50
}
```

---

## Club Events

### List/Create Events
`GET /api/clubs/events/` - List all events  
`POST /api/clubs/events/` - Create a new event

**Query Parameters:**
- `status` - Filter by status
- `club` - Filter by club ID

**Create Request Body:**
```json
{
    "club": 1,
    "title": "Hackathon 2025",
    "description": "Événement annuel",
    "date": "2025-01-15",
    "start_time": "09:00",
    "end_time": "18:00",
    "location": "Amphi A",
    "expected_attendees": 100
}
```

### Get/Update/Delete Event
`GET /api/clubs/events/<uuid:public_id>/`  
`PATCH /api/clubs/events/<uuid:public_id>/`  
`DELETE /api/clubs/events/<uuid:public_id>/`

**Event Statuses:**
- `draft` - Brouillon
- `pending` - En attente d'approbation
- `approved` - Approuvé
- `rejected` - Rejeté
- `completed` - Terminé
- `cancelled` - Annulé

---

## Club Reports

### List/Create Reports
`GET /api/clubs/reports/` - List all semester reports  
`POST /api/clubs/reports/` - Create a new report

**Query Parameters:**
- `semester` - Filter by semester (s1, s2)
- `academic_year` - Filter by year (e.g., 2024-2025)
- `club` - Filter by club ID

**Create Request Body:**
```json
{
    "club": 1,
    "semester": "s1",
    "academic_year": "2024-2025",
    "title": "Rapport S1 2024-2025",
    "content": "Description détaillée...",
    "events_organized": 5,
    "total_attendees": 250,
    "budget_used": 1500.00,
    "achievements": "Réalisations...",
    "challenges": "Défis rencontrés...",
    "next_semester_plans": "Plans futurs..."
}
```

### Get/Update/Delete Report
`GET /api/clubs/reports/<uuid:public_id>/`  
`PATCH /api/clubs/reports/<uuid:public_id>/`  
`DELETE /api/clubs/reports/<uuid:public_id>/`

---

## Club Announcements

### List/Create Announcements
`GET /api/clubs/announcements/` - List active announcements  
`POST /api/clubs/announcements/` - Create (admin only)

**Create Request Body:**
```json
{
    "title": "Réunion obligatoire",
    "content": "Tous les présidents...",
    "priority": "high",
    "target_clubs": [1, 2],
    "is_global": false,
    "expires_at": "2025-02-01T00:00:00Z"
}
```

**Priority Levels:**
- `low` - Basse
- `medium` - Moyenne
- `high` - Haute
- `urgent` - Urgente

### Get/Update/Delete Announcement
`GET /api/clubs/announcements/<uuid:public_id>/`  
`PATCH /api/clubs/announcements/<uuid:public_id>/`  
`DELETE /api/clubs/announcements/<uuid:public_id>/`

---

## Statistics

### Get Club Manager Stats
`GET /api/clubs/stats/`

**Response:**
```json
{
    "clubs_count": 2,
    "total_events": 10,
    "upcoming_events": 3,
    "completed_events": 5,
    "reports_count": 4,
    "total_members": 120
}
```

---

## Models

### Club
| Field | Type | Description |
|-------|------|-------------|
| public_id | UUID | Unique identifier |
| name | String | Club name |
| description | Text | Club description |
| logo | Image | Club logo |
| president | FK User | Club manager |
| status | Choice | pending/active/inactive/rejected |
| members_count | Integer | Number of members |
| created_at | DateTime | Creation date |

### ClubEvent
| Field | Type | Description |
|-------|------|-------------|
| public_id | UUID | Unique identifier |
| club | FK Club | Associated club |
| title | String | Event title |
| description | Text | Event details |
| date | Date | Event date |
| start_time | Time | Start time |
| end_time | Time | End time |
| location | String | Event location |
| status | Choice | Event status |
| expected_attendees | Integer | Expected participants |
| actual_attendees | Integer | Actual participants |

### ClubReport
| Field | Type | Description |
|-------|------|-------------|
| public_id | UUID | Unique identifier |
| club | FK Club | Associated club |
| semester | Choice | s1/s2 |
| academic_year | String | e.g., 2024-2025 |
| title | String | Report title |
| content | Text | Detailed content |
| events_organized | Integer | Number of events |
| total_attendees | Integer | Total participants |
| budget_used | Decimal | Budget spent |

### ClubAnnouncement
| Field | Type | Description |
|-------|------|-------------|
| public_id | UUID | Unique identifier |
| title | String | Announcement title |
| content | Text | Content |
| priority | Choice | low/medium/high/urgent |
| target_clubs | M2M Club | Target clubs |
| is_global | Boolean | Visible to all clubs |
| is_active | Boolean | Active status |
| expires_at | DateTime | Expiration date |
