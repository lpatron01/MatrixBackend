import os
from datetime import datetime
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .chatbot import UniversityChatbot
from .serializers import (
    ChatbotRequestSerializer,
    ChatbotResponseSerializer,
    ChatbotMessageSerializer
)


class ChatbotView(APIView):
    """Main chatbot API endpoint"""
    permission_classes = [permissions.AllowAny]  # Allow public access for chatbot

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._chatbot_instance = None

    @property
    def chatbot(self):
        """Lazy loading of chatbot instance"""
        if self._chatbot_instance is None:
            # Get the data directory path relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(current_dir, 'data')
            self._chatbot_instance = UniversityChatbot(data_dir)
        return self._chatbot_instance

    def post(self, request):
        """Handle chatbot conversation"""
        try:
            # Validate input
            serializer = ChatbotRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            user_message = serializer.validated_data['message']
            language = serializer.validated_data.get('language', 'fr')

            # Generate chatbot response
            bot_response = self.chatbot.generate_response(user_message)

            # Prepare response data
            response_data = {
                'response': bot_response,
                'timestamp': datetime.now(),
                'language': language
            }

            # Serialize and return response
            response_serializer = ChatbotResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected errors
            error_response = {
                'error': 'Une erreur s\'est produite lors du traitement de votre message.',
                'details': str(e) if request.user.is_staff else None,  # Show details only to staff
                'timestamp': datetime.now()
            }
            return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatbotHealthView(APIView):
    """Health check endpoint for chatbot"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Check if chatbot is operational"""
        try:
            # Get the data directory path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(current_dir, 'data')

            # Check if data directory exists
            if not os.path.exists(data_dir):
                return Response({
                    'status': 'error',
                    'message': 'Data directory not found'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            # Check if required data files exist
            required_files = ['absence.json', 'demarche.json']
            missing_files = []
            for file in required_files:
                if not os.path.exists(os.path.join(data_dir, file)):
                    missing_files.append(file)

            if missing_files:
                return Response({
                    'status': 'warning',
                    'message': f'Some data files missing: {", ".join(missing_files)}'
                }, status=status.HTTP_206_PARTIAL_CONTENT)

            # Try to initialize chatbot
            try:
                chatbot = UniversityChatbot(data_dir)
            except Exception as e:
                return Response({
                    'status': 'error',
                    'message': f'Failed to initialize chatbot: {str(e)}'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            return Response({
                'status': 'healthy',
                'message': 'Chatbot is operational',
                'response_type': 'keyword-based',
                'ai_available': False,
                'timestamp': datetime.now()
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Health check failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatbotInfoView(APIView):
    """Information about chatbot capabilities"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Return information about chatbot capabilities"""
        info = {
            'name': 'Chatbot Universitaire',
            'version': '1.0.0',
            'description': 'Assistant virtuel pour les étudiants de l\'université',
            'capabilities': [
                'Informations sur les programmes de licence et master',
                'Règles d\'absence et justifications',
                'Démarches administratives (attestations, relevés de notes, etc.)',
                'Informations sur les semestres et matières',
                'Coefficients des matières'
            ],
            'supported_languages': ['fr', 'en', 'ar'],
            'response_type': 'keyword-based',
            'ai_available': False,
            'features': 'Système basé sur les mots-clés pour des réponses structurées et précises'
        }
        return Response(info, status=status.HTTP_200_OK)
