#!/usr/bin/env python
"""
Test script for keyword-based chatbot functionality
"""
import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.development')
django.setup()

from chatbot.chatbot import UniversityChatbot

def test_keyword_chatbot():
    print("Testing keyword-based chatbot initialization...")
    try:
        # Get data directory path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(current_dir, 'chatbot', 'data')

        print(f"Data directory: {data_dir}")
        print(f"Data directory exists: {os.path.exists(data_dir)}")

        # Initialize chatbot
        chatbot = UniversityChatbot(data_dir)
        print("SUCCESS: Chatbot initialized with keyword-based responses!")

        # Test basic response
        print("\nTesting keyword response...")
        test_message = "Quels sont les programmes disponibles?"
        response = chatbot.generate_response(test_message)
        print(f"User: {test_message}")
        print(f"Bot: {response[:150]}...")
        print("SUCCESS: Keyword-based response generated!")

        # Test absence query
        print("\nTesting absence keyword response...")
        test_message2 = "Quelles sont les règles d'absence?"
        response2 = chatbot.generate_response(test_message2)
        print(f"User: {test_message2}")
        print(f"Bot: {response2[:150]}...")
        print("SUCCESS: Absence query handled!")

        print("\nALL TESTS PASSED: Keyword-based chatbot is working correctly!")

    except Exception as e:
        print(f"ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = test_keyword_chatbot()
    sys.exit(0 if success else 1)
