# Copyright (c) 2025 Kemar Christie & Roberto James
# Authors: Kemar Christie & Roberto James

from lexer import lexer  # Import the lexer object from lexer.py
from parser import parser
import gemini


def run_lexer(input_string):
    """Runs the lexer and prints the tokens."""
    lexer.input(input_string),
    print("----------------------------------------\nTokens:")
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)
    print("----------------------------------------\n")

def run_parser(input_string):
    """Runs the parser and validates the parse result."""
    result = parser.parse(input_string) 

    if result:
        print("\nParse Result:")
        print(result)
    return result  # Return the valid result if available

def run_complete_project(input_string):
    """Runs the lexer, parser, and the complete project (semantic analysis, etc.)."""
    print("\n--- Running Lexer ---")
    run_lexer(input_string)

    print("\n--- Running Parser ---")
    result = run_parser(input_string)


    if result:
        gemini.promptAI("single input",input_string)


def main():
    while True:
        print("\n--- Select an Option ---")
        print("1. Run Lexer")
        print("2. Run Parser")
        print("3. Run Complete Project")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            input_string = input("\nEnter the input string for the lexer: ")
            run_lexer(input_string)
        elif choice == '2':
            input_string = input("\nEnter the input string for the parser: ")
            run_parser(input_string)
        elif choice == '3':
            
            while True:
                input_string = input("\nEnter the input string for the complete project\n(enter exit to quit)\n: ")
                
                if "exit" in input_string.lower():
                    print("Exiting...")
                    break
                else:
                    run_complete_project(input_string)

        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    main()