import os
from dotenv import load_dotenv

import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

gemini_api = os.environ.get('GEMINI_API')
genai.configure(api_key=gemini_api)

model = genai.GenerativeModel("gemini-2.0-flash")

# Initialize an empty list to store the conversation history
conversation_history = []

def generate_with_context(prompt, history):
    """Generates content with conversation history."""
    contents = []
    for turn in history:
        contents.append({"role": turn["role"], "parts": [turn["content"]]})
    contents.append({"role": "user", "parts": [prompt]})

    try:
        response = model.generate_content(contents=contents)
        return response.text
    except Exception as e:
        return f"Error generating response: {e}"

print("Welcome to the interactive chat with Gemini!")
print("Type 'exit' to end the conversation.")

while True:
    user_input = input("You: ")
    if user_input.lower() == 'exit':
        break

    response_text = generate_with_context(user_input, conversation_history)
    print(f"Gemini: {response_text}")

    # Add the current turn to the history
    conversation_history.append({"role": "user", "content": user_input})
    conversation_history.append({"role": "model", "content": response_text})

print("Thank you for chatting!")