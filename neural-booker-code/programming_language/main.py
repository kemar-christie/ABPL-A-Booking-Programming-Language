# Copyright (c) 2025 Kemar Christie, Roberto James, Dwayne Gibbs, Tyoni Davis, Danielle Jones
# Authors: Kemar Christie, Roberto James, Dwayne Gibbs, Tyoni Davis, Danielle Jones

import ply.lex as lex
import ply.yacc as yacc
from lexer import lexer  # Import the lexer object from lexer.py
from parser import parser  # Import the parser object from parser.py
import gemini


def run_lexer(input_string):
    """Runs the lexer and prints the tokens."""
    lexer.input(input_string)
    print("----------------------------------------\nTokens:")
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)
    print("----------------------------------------\n")

def run_parser(input_string):
    """Runs the parser and prints the parse result."""
    result = parser.parse(input_string)
    print("\nParse Result:")
    print(result)
    return result  # Return the result for the complete project

def run_complete_project(input_string):
    """Runs the lexer, parser, and the complete project (semantic analysis, etc.)."""
    print("--- Running Lexer ---")
    run_lexer(input_string)

    print("\n--- Running Parser ---")
    parse_result = run_parser(input_string)

    # --- Semantic Analysis, LLM Integration, and Simulation ---
    #  This is where you would add the code to perform the remaining
    #  parts of your assignment. The 'parse_result' variable contains the
    #  parse tree, which you can now traverse and analyze.
    #  You would also make calls to the LLM and simulate the
    #  booking process here.

    gemini.send_prompt_to_gemini(input_string)


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
            input_string = input("\nEnter the input string for the complete project: ")
            run_complete_project(input_string)
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    main()