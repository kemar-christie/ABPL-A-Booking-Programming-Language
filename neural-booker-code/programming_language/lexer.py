# Copyright (c) 2025 Kemar Christie, Roberto james, Dwayne Gibbs, Tyoni Davis, Danielle Jones
# Authors: Kemar Christie, Roberto James, Dwayne Gibbs, Tyoni Davis, Danielle Jones

import re
from ply.lex import lex

# --- Tokenizer

tokens = ('ACTION_KEYWORD','LIST_KEYWORD', 'CONTEXT_KEYWORD', 'LOCATION_MARKER', 'CONNECTIVE_WORD', 
          'DATE', 'START_DATE', 'END_DATE', 'NUMBER', 'SYMBOL', 'MONEY', 'RESOURCE', 
          'CONDITIONS', 'TIME', 'USERNAME', 'DEPARTURE', 'ARRIVAL', 'LOCATION', 
          'SERVICE', 'ARTICLE_CONJUNCTION','PAYMENT_TYPE')

# Define action keywords - commands that initiate an action
action_keywords = [ 'Book a', 'Confirm a', 'Pay', 'Cancel a', 
                   'Reserve a', 'How many', 'Duration of']

# Define context keywords - words that provide context to actions
context_keywords = ['on', 'For', 'Schedule', 'are there', 'Returning', 
                    'cost']

all_keywords = action_keywords + context_keywords

# Define location markers separately - they help identify departure/arrival/location
location_markers = ['in', 'at', 'from', 'to']

# Define connective words - words that connect clauses or phrases
connective_words = ['that']

t_LIST_KEYWORD=r'List'

# Generate regex patterns for each category
t_ACTION_KEYWORD = r'\b(?:' + r'|'.join(action_keywords) + r')\b'

t_CONTEXT_KEYWORD = r'\b(?:' + r'|'.join(context_keywords) + r')\b'

t_LOCATION_MARKER = r'\b(?:' + r'|'.join(location_markers) + r')\b'

t_CONNECTIVE_WORD = r'\b(?:' + r'|'.join(connective_words) + r')\b'

t_START_DATE = r'(?<=\bfrom\b\s).+?(?=\s\bto\b)|(?<=\bon\b\s).+?(?=\s\bat\b)'

t_END_DATE = r'(?<=\breturning on\s).+?(?=\s(?:at)\b)|' \
             r'(?<=\bto\s).+?(?=\s(?:for)\b)|' \
             r'(?<=\bto\s).+?(?=\.)'

t_DATE = r'(?<=\bon\s)((?!\b(?:in|at|from|to)\b).)+?(?=\s\bto\b|\.)'

t_NUMBER = r'\b\d+\b'

t_SYMBOL = r'\.+(?=[ \t]*$)|,|:'

# The backslash escapes the $ to avoid it being interpreted as a special character.
t_MONEY = r'\$\d+(\.\d+)?'

t_RESOURCE = r'Reservations|Reservation|Tickets|Ticket|tickets|Flights|Flight|Rooms|Room|Hotels|Hotel'

t_CONDITIONS = r'\b(?:less than|more than|equal to|greater than|if|then)\b'

t_TIME = r'\b(?:([0-9])?[0-9]):[0-9][0-9]\s*(?:AM|PM)\b'

t_USERNAME = r'(?<=\bfor\b\s)[A-Za-z0-9_]+'

# Starting Point
t_DEPARTURE = r'(?<=\bfrom\b\s)([a-zA-Z\s]+?)(?=\s\band\b)|(?<=\bFrom\b\s)([a-zA-Z\s]+)(?=\s\bTo\b)|(?<=\bFrom\b\s)([a-zA-Z\s]+)(?=\s\bThat\b)|(?<=\bFrom\b\s)([a-zA-Z\s]+)(?=\s*\.)|(?<=\bFrom\b\s)([a-zA-Z\s]+)(?=\s\b(?:' + r'|'.join(all_keywords) + r')\b)'

# Destination
t_ARRIVAL = r'(?<=\bTo\b\s)([a-zA-Z\s]+?)(?=\s\bFrom\b)|' \
            r'(?<=\bTo\b\s)([a-zA-Z\s]+?)(?=\s*\.)|' \
            r'(?<=\bTo\b\s)([a-zA-Z\s]+?)(?=\s\b(?:' + r'|'.join(all_keywords) + r')\b)'

t_LOCATION = r'(?<=\bin\b\s)([a-zA-Z\s]+?)(?=\s\b(?:' + r'|'.join(all_keywords) + r')\b)|' \
             r'(?<=\bin\b\s)([a-zA-Z\s]+?)(?=\s*\.)'

t_SERVICE = r'(?<=\ba\s)(?!(?:' + r'|'.join(all_keywords) + r')\b)([A-Za-z]+(?:\s[A-Za-z]+)?)(?=\s(?:' + t_RESOURCE + r')\b)|' \
            r'(?<=\bList\s)([A-Za-z]+(?:\s[A-Za-z]+)?)(?=\s\bSchedule\b)|' \
            r'(?<=\bfor\s)([A-Za-z]+(?:\s[A-Za-z]+)?)(?=\s\bfor\b)|' \
            r'(?<=\bat\s)([A-Za-z]+(?:\s[A-Za-z]+)?)(?=\s(?:From|from)\b)'

t_ARTICLE_CONJUNCTION = r'\b(a|and)\b'

t_PAYMENT_TYPE = r'\b(credit card|debit card|bank transfer)\b'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Ignored white spaces and tab
t_ignore = ' \t'


def t_error(t):
    column = t.lexpos - t.lexer.lexdata.rfind('\n', 0, t.lexpos)
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}, column {column} ")
    t.lexer.skip(1)  # Skip the invalid character


# Build the lexer object
lexer = lex(reflags=re.IGNORECASE)

# Test the lexer (optional, for testing the lexer in isolation)
if __name__ == '__main__':
    data = "Bank transfer."
    lexer.input(data)

    print("\nTokenized Output:\n")
    while True:
        tok = lexer.token()  # Extract the next token
        if not tok:
            break # Stop when no more tokens are available
        print(tok)


