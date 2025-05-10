# 🎟️ ABPL – A Booking Programming Language

<br>

## 📝 Description
ABPL (A Booking Programming Language) is a domain-specific language designed to facilitate natural-language-style ticket booking operations. Developed in Python using the PLY (Python Lex-Yacc) toolkit, ABPL interprets user-friendly source code to simulate real-world actions such as booking, confirming, paying for, and cancelling tickets for various events and transport options.

This project was created as part of the CIT4004: Analysis of Programming Languages course at the University of Technology, Jamaica (Semester 2, 2024/2025). We have decided to take it to the next level by implementing changes and updates to this program.

<br>

## 🔧 Key Features
* ✅ Lexical, Syntax & Semantic Analysis - Built using PLY to tokenize, parse, and interpret ABPL source code.
* 🔍 Natural Syntax - Accepts commands that resemble natural language, making it easy to write and understand.
* 🤖 Google Gemini Integration - Retrieves real-time event and transportation data via Gemini's API.
* 🧾 Simulated Transactions - Bookings and payments are simulated and stored via the database.
* 🧠 Demonstrates Language Design Principles - Highlights characteristics such as reliability, readability and writability.
* 🖥️ Command-Line Interface - Run ABPL programs through a straightforward interpreter shell.

<br>

## 🖥️ Technologies Used
* 🪵 PLY (Python Lex-Yacc)
* 🐍 Python
* 🤖 Google Gemini API

<br>

## 🧾 Sample Program Prompts
```text
Knutsford Booking


List all Knutsford Express Schedule.

What is the schedule for Knutsford Express from Montego Bay to Kingston on Apr 21,2025 ?

Book a Knutsford Express ticket from Montego Bay to Kingston on Apr 21, 2025 at 9:00AM for 2 adults.

Confirm the Knutsford Express booking for rob_jam1.



What The User Has Reserved

List Bookings for rob_jam1.

List my reservations.
```

<br>

## 📁 Project Components
* lexer.py - Token definitions and regular expressions.
* parser.py - Grammar rules and syntax structure, Semantic analysis and simulated execution.
* gemini.py - API communication with Google Gemini.
* main.py – Entry point for the ABPL interpreter

<br>

## ▶️ How to Run ABPL
1. Clone the Repository
   ```bash
   git clone https://github.com/kemar-christie/ABPL-A-Booking-Programming-Language
   cd ABPL-A-Booking-Programming-Language
   ```

2. Install Dependencies
   <br> Ensure you have Python 3.9+ installed. Then, install the required libraries by navigating to the folder where "requirements.txt" is located:
   ```bash
   pip install -r requirements.txt
   ```

3. Set Your Gemini API Key
   <br> Before running the program, set your Google Gemini API key as an environment variable:
   
   - **on macOS/Linux:**
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```
  
   - **or on Windows:**
   ```bash
   set GEMINI_API_KEY="your_api_key_here"
   ```
   💡 You can also store your API key in a .env file and use python-dotenv to load it automatically.

4. Run the Full Program
   ```bash
   python main.py
   ```
   This will launch the ABPL command-line interface where you can enter ABPL source code.

5. Example Usage
   <br> Paste ABPL code directly into the interpreter:
   ```text
   List events in Kingston.

   Book 1 ticket for Dancehall Concert at National Stadium on May 10, 2025 at 7:30 PM for Kem_Chr1.

   Confirm reservation for Kem_Chr1.
   ```

<br>

## ✅ Contributors' Assignments Breakdown

| Name           | Deliverables                                                                                                | Status |
|----------------|-------------------------------------------------------------------------------------------------------------|:------:|
| Kemar Christie | Creation of Lexer & Parser, Database & Documentation                                                        |   ✅   |
| Roberto James  | Creation of Lexer & Parser, Training of AI, Scraping Tools Implementation & Documentation                   |   ✅   |
