# Chatbot API Documentation

## Overview

The Chatbot API provides an intelligent conversational assistant for university students. It leverages local AI models to answer questions about academic programs, administrative procedures, absence policies, and general university information. The chatbot uses structured data from JSON files and can provide responses in multiple languages.

## Base URL

```
http://localhost:8000/api/chatbot/
```

## Technology Stack

- **Framework**: Django 5.0+ with Django REST Framework 3.15+
- **Response System**: Keyword-based pattern matching and structured responses
- **Data Storage**: JSON files for university data (programs, procedures, policies)
- **Languages**: Multi-language support (French, English, Arabic)
- **Algorithm**: Rule-based keyword triggering for accurate responses

## Authentication

The Chatbot API is publicly accessible and does not require authentication. This allows students to access university information without needing to create accounts.

```
Authentication: Not required
```

## Features

### Keyword-Based Responses
- **Pattern Matching**: Advanced keyword detection and context analysis
- **Structured Responses**: Pre-formatted responses based on query patterns
- **Context Awareness**: Maintains conversation context for program-specific discussions

### Knowledge Base
- **Academic Programs**: Information about license and master programs, subjects, coefficients
- **Administrative Procedures**: Document requests, certificates, attestations
- **Absence Policies**: Rules, justifications, procedures
- **University Information**: General information and procedures

### Multi-language Support
- **Primary Language**: French (default)
- **Supported Languages**: French (`fr`), English (`en`), Arabic (`ar`)

## API Endpoints

All chatbot endpoints are prefixed with `/api/chatbot/`.

### 1. Chat Conversation

**Endpoint:** `POST /api/chatbot/chat/`

**Authentication:** Not required

**Description:** Send a message to the chatbot and receive an intelligent response. The chatbot can answer questions about university programs, administrative procedures, absence policies, and general information.

**Request Body:**

```json
{
  "message": "Quelles sont les matières du semestre 1 en licence informatique?",
  "language": "fr"
}
```

**Fields:**

- `message` (required, string): The user's question or message (max 1000 characters)
- `language` (optional, string): Language preference - choices: `fr`, `en`, `ar` (default: `fr`)

**Response:** `200 OK`

```json
{
  "response": "Pour le programme de Licence en Informatique, les matières enseignées au premier semestre sont :\n\n1. Algorithmique et Structures de Données\n2. Mathématiques Discrètes\n3. Architecture des Ordinateurs\n4. Programmation Orientée Objet\n5. Bases de Données\n6. Anglais Technique",
  "timestamp": "2025-12-14T10:30:00Z",
  "language": "fr"
}
```

**Example Queries:**
- "Quels sont les programmes disponibles?"
- "Quelles sont les règles d'absence?"
- "Comment demander une attestation de présence?"
- "Quelles sont les matières du semestre 1 en licence informatique?"
- "Quel est le coefficient de la matière Algorithmique?"

### 2. Health Check

**Endpoint:** `GET /api/chatbot/health/`

**Authentication:** Not required

**Description:** Check if the chatbot service is operational and verify data availability.

**Request Body:** None

**Response:** `200 OK` (Healthy)

```json
{
  "status": "healthy",
  "message": "Chatbot is operational",
  "response_type": "keyword-based",
  "ai_available": false,
  "timestamp": "2025-12-14T10:30:00Z"
}
```

**Response:** `503 Service Unavailable` (Issues detected)

```json
{
  "status": "error",
  "message": "Data directory not found"
}
```

**Response:** `206 Partial Content` (Some issues)

```json
{
  "status": "warning",
  "message": "Some data files missing: absence.json"
}
```

### 3. Chatbot Information

**Endpoint:** `GET /api/chatbot/info/`

**Authentication:** Not required

**Description:** Get detailed information about the chatbot's capabilities, supported features, and available data.

**Request Body:** None

**Response:** `200 OK`

```json
{
  "name": "Chatbot Universitaire",
  "version": "1.0.0",
  "description": "Assistant virtuel pour les étudiants de l'université",
  "capabilities": [
    "Informations sur les programmes de licence et master",
    "Règles d'absence et justifications",
    "Démarches administratives (attestations, relevés de notes, etc.)",
    "Informations sur les semestres et matières",
    "Coefficients des matières"
  ],
  "supported_languages": ["fr", "en", "ar"],
  "response_type": "keyword-based",
  "ai_available": false,
  "features": "Système basé sur les mots-clés pour des réponses structurées et précises"
}
```

## Error Responses

### 400 Bad Request

```json
{
  "message": "The message field is required.",
  "timestamp": "2025-12-14T10:30:00Z"
}
```

### 500 Internal Server Error

```json
{
  "error": "Une erreur s'est produite lors du traitement de votre message.",
  "details": "Detailed error message (only shown to staff users)",
  "timestamp": "2025-12-14T10:30:00Z"
}
```

## Data Structure

The chatbot uses structured JSON data files:

### Academic Programs
- **License Programs**: Information about bachelor's degree programs
- **Master Programs**: Information about master's degree programs
- **Subjects**: Course names, coefficients, semesters
- **Structure**: Organized by semesters with UE (Unités d'Enseignement) and ECUE (Éléments Constitutifs d'Unités d'Enseignement)

### Administrative Procedures
- **Document Requests**: Certificates, transcripts, diplomas
- **Absence Policies**: Rules, justifications, procedures
- **General Information**: Contact details, office hours

## Response Types

### Program Information
The chatbot can provide detailed information about:
- Available programs (license and master)
- Program structure and semesters
- Course subjects and coefficients
- Credit requirements

### Administrative Guidance
- Document request procedures
- Absence justification rules
- Contact information
- Deadlines and requirements

### Conversational Responses
- Natural language processing for complex queries
- Context-aware follow-up responses
- Multi-turn conversation support

## Rate Limiting

Currently, no rate limiting is implemented. The chatbot can handle multiple concurrent requests.

## Monitoring

The health check endpoint (`/api/chatbot/health/`) provides real-time status information including:
- Service availability
- AI model status
- Data file integrity
- System health indicators

## Example Usage

### JavaScript (fetch API)

```javascript
// Send a message to the chatbot
const response = await fetch('/api/chatbot/chat/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: "Quelles sont les programmes disponibles?",
    language: "fr"
  })
});

const data = await response.json();
console.log(data.response);
```

### Python (requests)

```python
import requests

# Send a message to the chatbot
response = requests.post('/api/chatbot/chat/', json={
    'message': 'Quelles sont les règles d\'absence?',
    'language': 'fr'
})

data = response.json()
print(data['response'])
```

### cURL

```bash
# Chat with the bot
curl -X POST http://localhost:8000/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Comment demander une attestation de présence?",
    "language": "fr"
  }'

# Health check
curl http://localhost:8000/api/chatbot/health/

# Get chatbot info
curl http://localhost:8000/api/chatbot/info/
```

## Future Enhancements

- User conversation history persistence
- Advanced natural language understanding
- Integration with user profiles
- Multilingual model fine-tuning
- Voice input/output support
- Real-time notifications integration

## Support

For technical support or questions about the chatbot functionality, please contact the development team.
