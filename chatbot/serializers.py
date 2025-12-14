from rest_framework import serializers


class ChatbotRequestSerializer(serializers.Serializer):
    """Serializer for chatbot API requests"""
    message = serializers.CharField(
        max_length=1000,
        required=True,
        help_text="The user's message to send to the chatbot"
    )
    language = serializers.ChoiceField(
        choices=['fr', 'en', 'ar'],
        default='fr',
        required=False,
        help_text="Language preference for the response"
    )


class ChatbotResponseSerializer(serializers.Serializer):
    """Serializer for chatbot API responses"""
    response = serializers.CharField(
        help_text="The chatbot's response message"
    )
    timestamp = serializers.DateTimeField(
        help_text="When the response was generated"
    )
    language = serializers.CharField(
        help_text="Language of the response",
        default="fr"
    )


class ChatbotMessageSerializer(serializers.Serializer):
    """Serializer for complete chatbot conversation messages"""
    user_message = serializers.CharField(
        help_text="The user's input message"
    )
    bot_response = serializers.CharField(
        help_text="The chatbot's response"
    )
    timestamp = serializers.DateTimeField(
        help_text="When the conversation occurred"
    )
    language = serializers.CharField(
        help_text="Language used in the conversation",
        default="fr"
    )
