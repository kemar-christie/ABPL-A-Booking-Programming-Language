# Copyright (c) 2025 Kemar Christie, Roberto James, Dwayne Gibbs, Tyoni Davis, Danielle Jones
# Authors: Kemar Christie, Roberto James, Dwayne Gibbs, Tyoni Davis, Danielle Jones

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import json
import database_connection
import mysql.connector

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
PROMPT_FILE = "copilot_prompt.txt"
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



def addUserInfoToDatabase(username, total_price, amount_paid, booking_type):

    # Get the database connection
    dbConn = database_connection.getDatabaseConnection()

    try:
        # Create a cursor object
        cursor = dbConn.cursor()

        # Call the stored procedure
        cursor.callproc('InsertBookingAndPayment', (booking_type, total_price, amount_paid, username))

        # Fetch the result of the stored procedure (booking_id)
        for result in cursor.stored_results():
            booking_id = result.fetchone()[0]  # Assuming booking_id is the first column in the result

        # Commit the transaction
        dbConn.commit()

        # Return the booking_id
        return booking_id

    except Exception as e:
        # Handle any exceptions (e.g., database errors)
        print(f"An error occurred: {e}")
        dbConn.rollback()  # Rollback the transaction in case of an error
        return None

    finally:
        # Close the cursor and connection
        cursor.close()
        dbConn.close()



def save_data_for_json(json_string):
    import os
    import json

    # Parse the JSON string into a dictionary
    try:
        data_dict = json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return

    # Define the attributes to extract and check
    attributes_to_check = ['username', 'total_price', 'amount_paid', 'booking_type']
    identified_attributes = {attr: data_dict.get(attr, None) for attr in attributes_to_check}

    print("Identified attributes in JSON:")
    for attr, value in identified_attributes.items():
        if value is None:
            print(f"{attr}: Not found")

    # Call the function to add customer info to the database
    bookingID = addUserInfoToDatabase( identified_attributes['username'],identified_attributes['total_price'],identified_attributes['amount_paid'],identified_attributes['booking_type'])

    # Reorganize the dictionary with booking_id as the first key
    reordered_data_dict = {'booking_id': bookingID}
    reordered_data_dict.update(data_dict)  # Add all other key-value pairs

    # Check if the file exists and load the current content if it does
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
    existing_data.append(reordered_data_dict)

    # Save the updated content back to the JSON file
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure the directory exists
    with open(file_path, "w") as file:
        json.dump(existing_data, file, indent=4)
        print("Data appended successfully to booking_data.json")
    
    return bookingID


def cancel_and_remove_booking(booking_id):

    try:
        # Establish a database connection
        db_conn = database_connection.getDatabaseConnection()
        
        # Create a cursor object
        cursor = db_conn.cursor()

        # Call the stored procedure
        cursor.callproc('CancelBooking', [booking_id])

        # Fetch the result from the stored procedure
        for result in cursor.stored_results():
            message = result.fetchone()[0]  # Get the first column of the first row (result message)

        # Commit the transaction
        db_conn.commit()

        return message

    except mysql.connector.Error as e:
        # Handle database errors
        print(f"Database error: {e}")
        return "An error occurred while processing the request."

    except Exception as e:
        # Handle other potential errors
        print(f"Error: {e}")
        return "An unexpected error occurred."

    finally:
        # Ensure the connection is closed
        if db_conn.is_connected():
            cursor.close()
            db_conn.close()


import mysql.connector

def addPartialPay(booking_id, amount_paid):
    """
    Calls the AddPartialPayment stored procedure to add a partial payment
    for the specified booking, ensuring the customer's balance is sufficient and
    updates payment and outstanding balance.
    
    :param booking_id: The ID of the booking to which the payment applies.
    :param amount_paid: The amount of the partial payment.
    :return: A success or error message from the stored procedure.
    """
    try:
        # Establish a database connection
        db_conn = database_connection.getDatabaseConnection()
        
        # Create a cursor object
        cursor = db_conn.cursor()

        # Call the stored procedure
        cursor.callproc('AddPartialPayment', [booking_id, amount_paid])

        # Fetch the result from the stored procedure
        for result in cursor.stored_results():
            message = result.fetchone()[0]  # Get the first column of the first row (result message)

        # Commit the transaction
        db_conn.commit()

        return message

    except mysql.connector.Error as e:
        # Handle database errors
        print(f"Database error: {e}")
        return "An error occurred while processing the payment."

    except Exception as e:
        # Handle other potential errors
        print(f"Error: {e}")
        return "An unexpected error occurred."

    finally:
        # Ensure the connection is closed
        if db_conn.is_connected():
            cursor.close()
            db_conn.close()


def promptAI(mode,singlePrompt=None):

    if mode!= "train" and mode != "single input":
        raise ValueError("Invalid mode. Use 'train' or 'single input'.")

    if mode == "train":
        # Print a welcome message to the user
        print("\n______________________________________________________________\nWelcome to the interactive chat with Gemini!")
        print("Type 'exit' to end the conversation.")

    # Start the main loop for the interactive chat
    while True:

        if mode == "train":
            # Get user input
            user_input = input("\nYou(type exit to end convo): ")
            # Check if the user wants to exit the chat
            if user_input.lower() == 'exit' or user_input.lower() == 'exit.':
                break
        elif mode == "single input":
            # Use the provided single prompt for testing
            user_input = singlePrompt

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
            bookingID=save_data_for_json(data_string)
            user_input = f"User data is save and just to let you know for future context the booking ID used is: {bookingID}"
            
            print("\n-----------------------------------------------\nDatabase Returned Booking ID:", bookingID,"\n-------------------------------------------\n")
            response_text =generate_with_context(user_input, conversation_history)  # Get Gemini's formatted response

            # Add the current user input to the conversation history list
            conversation_history.append({"role": "user", "content": user_input})
            # Add Gemini's response to the conversation history list
            conversation_history.append({"role": "model", "content": response_text})
            
            print(f"\n-----Gemini:\n{response_text}")  # Print Gemini's response

            # Append the current turn (user input and Gemini's response) to the history file
            with open(HISTORY_FILE, "a") as f:  # Open the file in append mode ("a")
                # Write the user's turn as a JSON object to the file, followed by a newline
                f.write(json.dumps({"role": "user", "content": user_input}) + "\n")
                # Write Gemini's turn as a JSON object to the file, followed by a newline
                f.write(json.dumps({"role": "model", "content": response_text}) + "\n")

        #check if AI contains the trigger word "cancel_Booking"
        elif "cancel_Booking(" in response_text:
            print("\n--------------Cancelled!!!\n\n")
            print(f"\n-----Gemini:\n{response_text}")       

            start_index = response_text.find("cancel_Booking(")
            if start_index == -1:
                print("Error: Trigger word 'cancel_Booking(' not found in response_text.")
                return  # Exit the function if the trigger word is missing
            start_index += len("cancel_Booking(")  # Adjust start_index to the position after the trigger word
            end_index = response_text.rfind(")")

            if end_index == -1:
                print("Error: Closing parenthesis ')' not found after 'cancel_Booking('.")
                return
            data_string = response_text[start_index:end_index]

            data_string = data_string.strip()  # Remove leading/trailing whitespace
            data_string = data_string.replace("\n", "")  # Remove any newlines
            data_string = data_string.strip("'")  # Remove the enclosing single quotes

            #Add Current user input to the conversation history list
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

            #extract the booking ID from the string that the AI sends as cancel_Booking("Kem_Chr1",10)
            bookingID = data_string.split(",")[1].strip().strip('"')  # Extract the booking ID from the string
            db_response=cancel_and_remove_booking(bookingID)  # Call the function to cancel the booking

            user_input = generate_with_context(db_response, conversation_history)  # Get Gemini's formatted response
            # Add the current user input to the conversation history list
            conversation_history.append({"role": "user", "content": user_input})
            # Add Gemini's response to the conversation history list
            conversation_history.append({"role": "model", "content": db_response})

            print(f"\n-----Gemini:\n{user_input}")

            # Append the current turn (user input and Gemini's response) to the history file
            with open(HISTORY_FILE, "a") as f:  # Open the file in append mode ("a")
                # Write the user's turn as a JSON object to the file, followed by a newline
                f.write(json.dumps({"role": "user", "content": user_input}) + "\n")
                # Write Gemini's turn as a JSON object to the file, followed by a newline
                f.write(json.dumps({"role": "model", "content": response_text}) + "\n")

        #check if AI contains the trigger word "partialPay"
        elif "partialPay(" in response_text:
            print("\n--------------Partial Payment!!!\n\n")
            print(f"\n-----Gemini:\n{response_text}")       

            start_index = response_text.find("partialPay(")
            if start_index == -1:
                print("Error: Trigger word 'partialPay(' not found in response_text.")
                return  # Exit the function if the trigger word is missing 
            
            start_index += len("partialPay(")  # Adjust start_index to the position after the trigger word
            end_index = response_text.rfind(")")

            if end_index == -1:
                print("Error: Closing parenthesis ')' not found after 'partialPay('.")
                return
            data_string = response_text[start_index:end_index]

            data_string = data_string.strip()  # Remove leading/trailing whitespace
            data_string = data_string.replace("\n", "")  # Remove any newlines
            data_string = data_string.strip("'")  # Remove the enclosing single quotes

            #Add Current user input to the conversation history list
            conversation_history.append({"role": "user", "content": user_input})
            # Add Gemini's response to the conversation history list
            conversation_history.append({"role": "model", "content": response_text})

            # Append the current turn (user input and Gemini's response) to the history file
            with open(HISTORY_FILE, "a") as f:  # Open the file in append mode ("a")
                # Write the user's turn as a JSON object to the file, followed by a newline
                f.write(json.dumps({"role": "user", "content": user_input}) + "\n")
                # Write Gemini's turn as a JSON object to the file, followed by a newline
                f.write(json.dumps({"role": "model", "content": response_text}) + "\n")

            #extract the booking Id and amount from the string that the AI sends as partialPay(10,50) 10 is the bookind id and 50 is the amount.
            bookingID = data_string.split(",")[0].strip().strip('"')  # Extract the booking ID from the string
            amount = data_string.split(",")[1].strip().strip('"')  # Extract the amount from the string
            
            db_response = addPartialPay(bookingID, amount)  # Call the function to cancel the booking
            
            response_text = generate_with_context(db_response, conversation_history)  # Get Gemini's formatted response
            user_input = f"db_response: {db_response}"
            # Add the current user input to the conversation history list
            conversation_history.append({"role": "user", "content": user_input})
            # Add Gemini's response to the conversation history list
            conversation_history.append({"role": "model", "content": response_text})

            print(f"\n-----Gemini:\n{response_text}")

            # Append the current turn (user input and Gemini's response) to the history file
            with open(HISTORY_FILE, "a") as f:
                # Open the file in append mode ("a")
                # Write the user's turn as a JSON object to the file, followed by a newline
                f.write(json.dumps({"role": "user", "content": user_input}) + "\n")
                # Write Gemini's turn as a JSON object to the file, followed by a newline
                f.write(json.dumps({"role": "model", "content": response_text}) + "\n")            

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

        
        if mode == "single input":
            # If in single input mode, break the loop after one iteration
            break

        # Print a thank you message when the chat ends
        print("Thank you for chatting!")




#send_prompt_to_gemini("List all Knutsford Express ")
#promptAI("single input", "List all Knutsford Express bookings for rob_jam1.")
promptAI("train")
#addUserInfoToDatabase("rob_jam1", 55.44, 55.44, "Knutsford Express", "credit card")
#save_data_for_json('{"username": "rob_jam1", "route": "Montego Bay to Kingston", "date": "February 21 2025", "departure_time": "10:00 AM", "arrival_time": "2:00 PM", "ticket_type": "Adult", "total_cost": 55.44, "amount_paid": 55.44, "booking_type": "Knutsford Express"}')