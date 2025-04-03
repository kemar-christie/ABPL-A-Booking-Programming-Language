# Copyright (c) 2025 Kemar Christie, Roberto james, Dwayne Gibbs, Tyoni Davis, Danielle Jones
# Authors: Kemar Christie, Roberto James, Dwayne Gibbs, Tyoni Davis, Danielle Jones

import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

# Load environment variables from .env file
load_dotenv()

# Retrieve the Gemini API key from the environment variables
gemini_api = os.environ.get('GEMINI_API')
# Configure the Gemini API with the loaded API key
genai.configure(api_key=gemini_api)

# Initialize the Gemini Generative Model
model = genai.GenerativeModel("gemini-2.0-flash")

# Define the file name to store the conversation history
HISTORY_FILE = "chat_history.txt"

# Initialize an empty list to store the conversation history in the current session
conversation_history = []

# Load history from file if it exists when the script starts
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        # Iterate through each line in the history file
        for line in f:
            try:
                # Try to parse each line as a JSON object representing a turn in the conversation
                turn = json.loads(line.strip())
                conversation_history.append(turn)
            except json.JSONDecodeError:
                # If JSON parsing fails, attempt to parse based on simple "You:" and "Gemini:" prefixes
                # This provides backward compatibility for older history file formats
                if line.startswith("You: "):
                    conversation_history.append({"role": "user", "content": line[5:].strip()})
                elif line.startswith("Gemini: "):
                    conversation_history.append({"role": "model", "content": line[8:].strip()})

def generate_with_context(prompt, history):
    """
    Generates content using the Gemini model, incorporating the conversation history.

    Args:
        prompt (str): The current user input.
        history (list): A list of dictionaries, where each dictionary represents a turn
                        in the conversation with 'role' and 'content' keys.

    Returns:
        str: The generated response from the Gemini model.
    """
    # Prepare the 'contents' for the Gemini API, including the conversation history
    contents = []
    for turn in history:
        contents.append({"role": turn["role"], "parts": [turn["content"]]})

    # Add the current user prompt to the 'contents'
    contents.append({"role": "user", "parts": [prompt]})

    try:
        # Generate content using the Gemini model with the provided context
        response = model.generate_content(contents=contents)
        return response.text
    except Exception as e:
        return f"Error generating response: {e}"

# Print a welcome message to the user
print("Welcome to the interactive chat with Gemini!")
print("Type 'exit' to end the conversation.")

# Start the main loop for the interactive chat
while True:
    # Get user input
    user_input = input("You(type exit to end convo): ")
    # Check if the user wants to exit the chat
    if user_input.lower() == 'exit':
        break

    # Generate a response from Gemini, considering the conversation history
    response_text = generate_with_context(user_input, conversation_history)
    # Print Gemini's response
    print(f"Gemini: {response_text}")

    # Add the current user input to the conversation history list
    conversation_history.append({"role": "user", "content": user_input})
    # Add Gemini's response to the conversation history list
    conversation_history.append({"role": "model", "content": response_text})

    # Append the current turn (user input and Gemini's response) to the history file
    with open(HISTORY_FILE, "a") as f:  # Open the file in append mode ("a")
        # Write the user's turn as a JSON object to the file, followed by a newline
        f.write(json.dumps({"role": "user", "content": user_input}) + "\n")
        # Write Gemini's turn as a JSON object to the file, followed by a newline
        f.write(json.dumps({"role": "model", "content": response_text}) + "\n")

# Print a thank you message when the chat ends
print("Thank you for chatting!")