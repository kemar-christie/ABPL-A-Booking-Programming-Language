# Copyright (c) 2025 Kemar Christie, Roberto james, Dwayne Gibbs, Tyoni Davis, Danielle Jones
# All rights reserved. Unauthorised use, copying, or distribution is prohibited.
# Contact kemar.christie@yahoo.com, robertojames91@gmail.com, dwaynelgibbs@gmail.com, davistyo384@gmail.com & Jonesdanielle236@yahoo.com for licensing inquiries.
# Authors: Kemar Christie, Roberto James, Dwayne Gibbs, Tyoni Davis, Danielle Jones


import re


# Example of Strings that can be tokenized:

# Working:

# List flights from Jamaica to USA. - Working
# Book a ticket to USA from Jamaica that cost less than $2000. - Working
# Book a ticket to USA from Jamaica. - Working
# How many tickets are there from USA to Jamaica. - Working
# Book a ticket to USA from Jamaica and a Reservation from Mar 10, 2025 To Mar 10, 2025. - Working
# Book a Knutsford Express Ticket from Montego Bay to Kingston on February 17, 2025 at 8:30 AM for Joy_Reynolds. - Working
# Book a Ticket from Montego Bay to Miami on February 17, 2025 at 8:30 AM returning on March 17, 2025 at 8:30 AM. - Working
# Book a Room at AC Hotel from March 10, 2025 to March 15, 2025 for Joy_Reynolds. - Working
# Reserve a Room at AC Hotel from March 10, 2025 to March 15, 2025 for Joy_Reynolds. - Working
# Confirm a Room at AC Hotel from March 10, 2025 to March 15, 2025 for Joy_Reynolds. - Working
# Cancel a Room at AC Hotel from March 10, 2025 to March 15, 2025 for Joy_Reynolds. - Working
# List Knutsford Express schedule. - Working
# Pay reservation for Knutsford Express for Joy_Reynolds. - Working
# Book a Hotel in Miami on March 19, 2025. - Working



from ply.lex import lex
from ply.yacc import yacc

# --- Tokenizer

tokens = ('KEYWORD', 'DATE', 'START_DATE', 'END_DATE', 'NUMBER', 'SYMBOL', 'MONEY', 'RESOURCE', 'CONDITIONS', 'TIME', 'USERNAME', 'DEPARTURE', 'ARRIVAL', 'LOCATION', 'SERVICE', 'OTHER_WORDS')


# Define keywords as a Python list
keywords = ['List', 'Book a', 'Confirm', 'Pay', 'From', 'To', 'On', 'For', 'Schedule', 
            'Cancel', 'Cost', 'Duration of', 'That', 'How many', 'are there', 
            'At', 'Returning', 'in','Reserve a']




# Generate the t_KEYWORD regex dynamically
t_KEYWORD = r'\b(?:' + r'|'.join(keywords) + r')\b'

t_CONDITIONS = r'\b(?:less than|more than|equal to|greater than|if|then)\b'

t_RESOURCE = r'Reservations|Reservation|Tickets|Ticket|tickets|Flights|Flight|Rooms|Room|Hotels|Hotel'

# Regex for dates (abbreviated and full month names only)
t_DATE = r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{1,2},\s*\d{4}\b|' \
         r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2},\s*\d{4}\b)'

t_START_DATE = r'(?<=\bfor\s)' + t_DATE + r'(?=\s(?:at|to)\b)|' \
               r'(?<=\bon\s)' + t_DATE + r'(?=\s(?:at|to|returning)\b)'

t_END_DATE = r'(?<=\bto\s)' + t_DATE + r'(?=\s(?:for|at|\.|\b))'

t_NUMBER = r'\b\d+\b'

t_OTHER_WORDS = r'\b(a|and)\b'

# The backslash escapes the $ to avoid it being interpreted as a special character.
t_MONEY = r'\$\d+(\.\d+)?'

# Destination
t_ARRIVAL = r'(?<=\bTo\b\s)([a-zA-Z\s]+?)(?=\s\bFrom\b)|'\
            r'(?<=\bTo\b\s)([a-zA-Z\s]+?)(?=\s*\.)|'\
            r'(?<=\bTo\b\s)([a-zA-Z\s]+?)(?=\s\b(?:' + r'|'.join(keywords) + r')\b)'

# Starting Point
t_DEPARTURE = r'(?<=\bfrom\b\s)([a-zA-Z\s]+?)(?=\s\band\b)|(?<=\bFrom\b\s)([a-zA-Z\s]+)(?=\s\bTo\b)|(?<=\bFrom\b\s)([a-zA-Z\s]+)(?=\s\bThat\b)|(?<=\bFrom\b\s)([a-zA-Z\s]+)(?=\s*\.)|(?<=\bFrom\b\s)([a-zA-Z\s]+)(?=\s\b(?:' + r'|'.join(keywords) + r')\b)'

t_LOCATION = r'(?<=\bin\b\s)([a-zA-Z\s]+?)(?=\s\b(?:' + r'|'.join(keywords) + r')\b)|'\
             r'(?<=\bin\b\s)([a-zA-Z\s]+?)(?=\s*\.)'

t_TIME = r'\b(?:([0-9])?[0-9]):[0-9][0-9]\s*(?:AM|PM)\b'

t_USERNAME = r'(?<=\bfor\b\s)[A-Za-z0-9_]+'

#t_SERVICE = r'(?<=\bat\s)([A-Za-z\s]+?)(?=\sfrom\b)|(?<=\bList\s)([A-Za-z\s]+?)(?=\s\bSchedule\b)|(?<=\bfor\s)([A-Za-z\s]+?)(?=\s\bfor\b)|(?<=\ba\s)([A-Za-z\s]+?)(?=\s(?:' + t_RESOURCE + r')\b)(?!.*\b(?:' + t_RESOURCE + r')\b)'

t_SERVICE = r'(?<=\ba\s)(?!(?:' + r'|'.join(keywords) + r')\b)([A-Za-z]+(?:\s[A-Za-z]+)?)(?=\s(?:' + t_RESOURCE + r')\b)|'\
            r'(?<=\bList\s)([A-Za-z]+(?:\s[A-Za-z]+)?)(?=\s\bSchedule\b)|'\
            r'(?<=\bfor\s)([A-Za-z]+(?:\s[A-Za-z]+)?)(?=\s\bfor\b)|'\
            r'(?<=\bat\s)([A-Za-z]+(?:\s[A-Za-z]+)?)(?=\s(?:From|from)\b)'

t_SYMBOL = r'\.+(?=[ \t]*$)|,|:'

# Ignored white spaces and tab
t_ignore = ' \t\n'


def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)


# Build the lexer object
lexer = lex(reflags=re.IGNORECASE)


# Provide the input data
data = "Book a flight from miami to New to York for March 20, 2025 at 10:00 PM to April 7, 2025 for jam_smi2."

# Feed the input data to the lexer
lexer.input(data)

# Tokenize and print the output
print("Tokenized Output:")
while True:
    tok = lexer.token()  # Extract the next token
    if not tok:
        break  # Stop when no more tokens are available
    print(tok)



# Note Error to look out for:

# user must end line with a period
# need to ensure that the time can only go to 12 hours max(so 14:00 PM is invalid), t_TIME = r'\b(?:0?[1-9]|1[0-2]):[0-5][0-9]\s*(?:AM|PM)\b' 
# When reserving a ticket the customer must make a down payment of 60 % of the total cost
# When ever the keyword confirm is used, we take the full amount from the customer
# When Booking a plane ticket we have three option: The customer can Pay for the ticket then they have to confirm the ticket and also they have the option of cancelling the ticket.
# When Booking a reservation for the hotel we have four option: The customer can reserve the room, confirm the room, cancel the room and pay for the room.
# If the customer enters "Reserve a Reservation" an error should be displayed.