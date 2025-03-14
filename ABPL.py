# Copyright (c) 2025 Kemar Christie, Roberto james, Dwayne Gibbs, Tyoni Davis, Danielle Jones
# All rights reserved. Unauthorised use, copying, or distribution is prohibited.
# Contact kemar.christie@yahoo.com, robertojames91@gmail.com, dwaynelgibbs@gmail.com, davistyo384@gmail.com & Jonesdanielle236@yahoo.com for licensing inquiries.
# Authors: Kemar Christie, Roberto James, Dwayne Gibbs, Tyoni Davis, Danielle Jones


import sys,re
sys.path.insert(0, "ply-master/ply-master/src")


# Example of Strings that can be tokenized:

# List all flights from Jamaica to USA.
# Book a ticket to USA from Jamaica that cost less than $2000.
# Book a ticket to USA from Jamaica.
# How many tickets are there from USA to Jamaica.
# Book a ticket to USA from Jamaica and a Reservation from Mar 10, 2025 To Mar 10, 2025.


from ply.lex import lex
from ply.yacc import yacc

# --- Tokenizer

tokens = ('KEYWORD','DATE','NUMBER','SYMBOL','LOCATION','MONEY','REQUEST','CONDITIONS','ARTICLE','TIME')


# Define keywords as a Python list
keywords = ['List', 'Book', 'Confirm', 'Pay', 'From', 'To', 'On', 'For', 'Schedule', 
            'Cancel', 'Cost', 'Duration', 'That', 'Knutsford Express', 'How many', 
            'There', 'Are', 'All', 'At']

# Generate the t_KEYWORD regex dynamically
t_KEYWORD = r'\b(?:' + r'|'.join(keywords) + r')\b'

t_CONDITIONS = r'\b(?:less than|more than|equal to|greater than|if|then)\b'

t_REQUEST = r'Reservations|Reservation|Tickets|Ticket|Flights|Flight'

# Regex for dates (abbreviated and full month names only)
t_DATE = r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{1,2},\s*\d{4}\b|' \
         r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2},\s*\d{4}\b)'

t_ARTICLE = r'\b(a|an|the)\b'

t_NUMBER = r'\b\d+\b'

# The backslash escapes the $ to avoid it being interpreted as a special character.
t_MONEY = r'\$\d+(\.\d+)?'

t_SYMBOL = r'\.+(?=[ \t]*$)|,|:'

# Ignored white spaces and tab
t_ignore = ' \t'

# Use the same keywords in t_LOCATION
t_LOCATION = r'(?<=\bTo\b\s)([a-zA-Z\s]+)(?=\s\bFrom\b)|' \
             r'(?<=\bFrom\b\s)([a-zA-Z\s]+)(?=\s\bTo\b)|' \
             r'(?<=\bTo\b\s)([a-zA-Z\s]+)(?=\s*\.)|' \
             r'(?<=\bFrom\b\s)([a-zA-Z\s]+)(?=\s\bThat\b)|' \
             r'(?<=\bFrom\b\s)([a-zA-Z\s]+)(?=\s*\.)|' \
             r'(?<=\bTo\b\s)([a-zA-Z\s]+)(?=\s\b(?:' + r'|'.join(keywords) + r')\b)'

t_TIME = r'\b(?:([0-9])?[0-9]):[0-9][0-9]\s*(?:AM|PM)\b'


def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)


# Build the lexer object
lexer = lex(reflags=re.IGNORECASE)


# Provide the input data
data = "boOk Knutsford Express from Montego Bay to Kingston on February 17, 2025 at 08:39AM for Joy Reynolds."

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
# user must  end line with a period.
# ensure the lexer ignore new line
# need to ensure that the time can only go to 12 hours max(so 14:00 PM is invalid), t_TIME = r'\b(?:0?[1-9]|1[0-2]):[0-5][0-9]\s*(?:AM|PM)\b'
# Ensure to split up the  the location KEYWORD so we have a starting location and a destination.