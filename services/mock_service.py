def mock_chatbot_response(prompt: str) -> str:
    simulated = {
        "hi": "Hello! How can I assist you today?",
        "bye": "Goodbye! Have a great day!",
        "who are you": "I am a conversational AI built for testing.",
        "help": "Sure! I can help you with your queries or tasks."
    }
    for key, val in simulated.items():
        if key in prompt.lower():
            return val
    return "Sorry, I didn’t quite understand that."


