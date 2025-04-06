# Copyright (c) 2025 Kemar Christie, Roberto James, Dwayne Gibbs, Tyoni Davis, Danielle Jones
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

# Define file paths
HISTORY_FILE = "chat_history.txt"
PROMPT_FILE = "Copilot_prompt.txt"
conversation_history = []

def get_initial_prompt():
    """
    Reads the initial prompt from the Copilot_prompt.txt file.
    Returns:
        str: The initial prompt text, or None if the file cannot be read.
    """
    try:
        with open(PROMPT_FILE, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: {PROMPT_FILE} not found.")
        return None
    except IOError:
        print(f"Error: Could not read {PROMPT_FILE}.")
        return None


if not os.path.exists(HISTORY_FILE) or os.path.getsize(HISTORY_FILE) == 0:
    initial_prompt = get_initial_prompt()
    if initial_prompt:
        # Add the initial prompt to the conversation history
        conversation_history.append({"role": "user", "content": initial_prompt})
        try:
            response = model.generate_content(contents=[{"role": "user", "parts": [initial_prompt]}])
            conversation_history.append({"role": "model", "content": response.text})
            # Write the initial prompt and response to the history file
            with open(HISTORY_FILE, "a") as f:
                f.write(json.dumps({"role": "user", "content": initial_prompt}) + "\n")
                f.write(json.dumps({"role": "model", "content": response.text}) + "\n")
        except Exception as e:
            print(f"Error priming Gemini with initial prompt: {e}")
    else:
        print("Warning: Initial prompt could not be loaded.")


# Load history from file if it exists when the script starts
elif os.path.exists(HISTORY_FILE) and os.path.getsize(HISTORY_FILE) > 0:
    # Read the conversation history from the file
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



def save_data_for_json(json_string):
    # Parse the JSON string into a dictionary
    try:
        data_dict = json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return

    # Check if the file exists, and load the current content if it does
    file_path = "neural-booker-output/json/booking_data.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                print("Warning: Existing file contains invalid JSON. Starting fresh.")
                existing_data = []
    else:
        existing_data = []

    # Append the new data to the existing content
    existing_data.append(data_dict)

    # Save the updated content back to the JSON file
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure the directory exists
    with open(file_path, "w") as file:
        json.dump(existing_data, file, indent=4)
        print("Data appended successfully to booking_data.json")


def trainAI():
    # Print a welcome message to the user
    print("\n______________________________________________________________\nWelcome to the interactive chat with Gemini!")
    print("Type 'exit' to end the conversation.")

    # Start the main loop for the interactive chat
    while True:
        # Get user input
        user_input = input("\nYou(type exit to end convo): ")
        # Check if the user wants to exit the chat
        if user_input.lower() == 'exit' or user_input.lower() == 'exit.':
            break

        response_text = generate_with_context(user_input, conversation_history)
        # Remove escape characters before searching for the trigger word

        response_text = response_text.replace("\\", "")  # Remove all backslashes

        if "getKnutsfordDetails()" in response_text:
            print(f"\n-----Gemini:\n {response_text}") # Print Gemini's response
            import get_data_for_AI
            knutsford_data = get_data_for_AI.getKnutsfordDetails()
            
            data_prompt = f"Here is the Knutsford Express data from the code: {knutsford_data} use it to {user_input} "
            conversation_history.append({"role": "user", "content": data_prompt})

            # Append the current turn (user input and Gemini's response) to the history file
            with open(HISTORY_FILE, "a") as f:  # Open the file in append mode ("a")
                # Write Gemini's turn as a JSON object to the file, followed by a newline
                f.write(json.dumps({"role": "model", "content": response_text}) + "\n")
                # Write the user's turn as a JSON object to the file, followed by a newline
                f.write(json.dumps({"role": "user", "content": data_prompt}) + "\n")


            response_text = generate_with_context(data_prompt, conversation_history)  # Get Gemini's formatted response


            print(f"\n-----Gemini:\n{response_text}") # Print Gemini's response
        # Check if the AI response contains the trigger word "saveDataforJSON"
        elif "save_data_for_json(" in response_text:
            print("\n--------------processed!!!\n\n")
            print(f"\n-----Gemini:\n{response_text}")  # Print Gemini's response

            #Initialize start_index properly
            start_index = response_text.find("save_data_for_json(")
            if start_index == -1:
                print("Error: Trigger word 'save_data_for_json(' not found in response_text.")
                return  # Exit the function if the trigger word is missing

            start_index += len("save_data_for_json(")  # Adjust start_index to the position after the trigger word
            end_index = response_text.rfind(")")


            if end_index == -1:
                print("Error: Closing parenthesis ')' not found after 'saveDataforJSON('.")
                return  
            data_string = response_text[start_index:end_index]

            data_string = data_string.strip()  # Remove leading/trailing whitespace
            data_string = data_string.replace("\n", "")  # Remove any newlines
            data_string = data_string.strip("'")  # Remove the enclosing single quotes

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
            
            print(f"Extracted Data String: {data_string}")

            # Call the JSON saving function from the imported module
            save_data_for_json(data_string)


        else:
            print(f"\n-----Gemini:\n{response_text}")
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




def send_prompt_to_gemini(user_input):
    # Print a welcome message to the user
    print("\n______________________________________________________________\nWelcome to the interactive chat with Gemini!")
    print("Type 'exit' to end the conversation.")

    # Start the main loop for the interactive chat
    #while True:
        # Get user input
        #user_input = input("\nYou(type exit to end convo): ")
        # Check if the user wants to exit the chat
    #if user_input.lower() == 'exit' or user_input.lower() == 'exit.':
    #    break

    response_text = generate_with_context(user_input, conversation_history)

    if "getKnutsfordDetails()" in response_text:
        print(f"\n-----Gemini:\n {response_text}") # Print Gemini's response
        import get_data_for_AI
        knutsford_data = get_data_for_AI.getKnutsfordDetails()
        
        data_prompt = f"Here is the Knutsford Express data from the code: {knutsford_data} use it to {user_input} "
        conversation_history.append({"role": "user", "content": data_prompt})

        # Append the current turn (user input and Gemini's response) to the history file
        with open(HISTORY_FILE, "a") as f:  # Open the file in append mode ("a")
            # Write Gemini's turn as a JSON object to the file, followed by a newline
            f.write(json.dumps({"role": "model", "content": response_text}) + "\n")
            # Write the user's turn as a JSON object to the file, followed by a newline
            f.write(json.dumps({"role": "user", "content": data_prompt}) + "\n")


        response_text = generate_with_context(data_prompt, conversation_history)  # Get Gemini's formatted response


        print(f"\n-----Gemini:\n{response_text}") # Print Gemini's response
    # Check if the AI response contains the trigger word "saveDataforJSON"
    elif "save_data_for_json(" in response_text:
        print("\n--------------processed!!!\n\n")
        print(f"\n-----Gemini:\n{response_text}")  # Print Gemini's response

        # Extract the data string within saveDataforJSON(...)
        start_index = response_text.find("saveDataforJSON(") + len("saveDataforJSON(")
        end_index = response_text.find(")", start_index)
        data_string = response_text[start_index:end_index]
        
 
        # Call the JSON saving function from the imported module
        save_data_for_json(data_string)

        # Append the current turn (user input and Gemini's response) to the history file
        with open(HISTORY_FILE, "a") as f:  # Open the file in append mode ("a")
            # Write Gemini's turn as a JSON object to the file, followed by a newline
            f.write(json.dumps({"role": "model", "content": response_text}) + "\n")
            # Write the user's turn as a JSON object to the file, followed by a newline
            f.write(json.dumps({"role": "user", "content": data_prompt}) + "\n")

    else:
        print(f"\n-----Gemini:\n{response_text}")
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

#send_prompt_to_gemini("List all Knutsford Express ")
trainAI()
#save_data_for_json('{"username": "rob_jam1", "route": "Montego Bay to Kingston", "date": "February 21 2025", "departure_time": "10:00 AM", "arrival_time": "2:00 PM", "ticket_type": "Adult", "total_cost": 55.44, "amount_paid": 55.44, "booking_type": "Knutsford Express"}')
