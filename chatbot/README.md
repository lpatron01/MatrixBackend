# University Chatbot API

A keyword-based conversational assistant for university students built with Django REST Framework and structured data matching.

## Features

- 🔍 **Keyword-Based Responses**: Advanced pattern matching and keyword detection
- 📚 **University Knowledge**: Comprehensive information about academic programs, procedures, and policies
- 🌍 **Multi-language Support**: French (primary), English, and Arabic
- 💬 **Context Awareness**: Maintains conversation context for program-specific discussions
- 📖 **Structured Data**: Uses JSON knowledge base for accurate information

## Quick Start

### Prerequisites
- Python 3.10+
- Django 5.0+
- No external AI models required

### Installation

The chatbot is already integrated into the main Django project.

### Running the Chatbot

1. Start the Django development server:
```bash
cd backend
python manage.py runserver
```

2. The chatbot API will be available at:
- **Chat**: `POST /api/chatbot/chat/`
- **Health Check**: `GET /api/chatbot/health/`
- **Info**: `GET /api/chatbot/info/`

## API Usage

### Basic Chat

```bash
curl -X POST http://localhost:8000/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Quelles sont les programmes disponibles?", "language": "fr"}'
```

### Health Check

```bash
curl http://localhost:8000/api/chatbot/health/
```

## Knowledge Base

The chatbot uses structured JSON data files located in the `data/` directory:

- `absence.json` - University absence policies and procedures
- `demarche.json` - Administrative procedures and document requests
- `license/` - Bachelor's degree program information (5 programs)
- `mastere/` - Master's degree program information (5 programs)

## Capabilities

### Academic Information
- Available programs (license and master degrees)
- Course subjects and coefficients
- Semester structure and credits
- Program-specific details

### Administrative Procedures
- Document requests (certificates, transcripts, diplomas)
- Absence justifications and policies
- Contact information and deadlines

### Keyword Matching
- Advanced keyword detection for query classification
- Structured response generation based on detected patterns
- Multi-turn conversation support with context retention

## Architecture

### Components

1. **Chatbot Class** (`chatbot.py`): Core keyword matching and response generation
2. **Django Views** (`views.py`): REST API endpoints
3. **Serializers** (`serializers.py`): Request/response handling
4. **URLs** (`urls.py`): Route configuration

### Response Pipeline

1. **Input Processing**: User message validation and language detection
2. **Keyword Analysis**: Pattern matching against predefined keyword sets
3. **Context Retrieval**: Extract relevant data from knowledge base
4. **Response Generation**: Format structured responses based on detected patterns
5. **Context Management**: Maintain conversation history and program context

## Configuration

### Environment Variables

No additional configuration required. The chatbot operates entirely with keyword-based responses.

### Data Updates

To update the knowledge base:
1. Modify JSON files in the `data/` directory
2. Restart the Django server
3. The chatbot will automatically reload the updated data

## Development

### Adding New Knowledge

1. Create or update JSON files in `data/` directory
2. Follow existing data structure patterns
3. Test with the health check endpoint

### Extending Capabilities

The chatbot can be extended by:
- Adding new JSON data files
- Modifying keyword patterns in the matching logic
- Adding new response templates
- Extending language support

## Troubleshooting

### Common Issues

**Data Files Missing**
- Check `data/` directory exists and contains required JSON files
- Use health check endpoint to verify data integrity

**No Response Generated**
- Verify the query contains recognizable keywords
- Check if the question matches expected patterns
- Ensure JSON data files are properly formatted

**Wrong Program Context**
- Clear conversation context by asking about a different program
- Use specific program names in queries

## API Reference

For detailed API documentation, see: `../API-Documentation/Chatbot_API.md`

## Performance

- **No External Dependencies**: Operates without AI models or external APIs
- **Fast Response Times**: Keyword matching is instantaneous
- **Lightweight**: Minimal memory footprint
- **Reliable**: Deterministic responses based on structured data

## Support

For technical support or questions about the chatbot functionality, please contact the development team.
