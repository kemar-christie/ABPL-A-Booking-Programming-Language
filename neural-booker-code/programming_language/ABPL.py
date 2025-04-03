# Copyright (c) 2025 Kemar Christie, Roberto james, Dwayne Gibbs, Tyoni Davis, Danielle Jones
# Authors: Kemar Christie, Roberto James, Dwayne Gibbs, Tyoni Davis, Danielle Jones

import re

from ply.lex import lex
from ply.yacc import yacc


# --- Tokenizer

tokens = ('ACTION_KEYWORD', 'CONTEXT_KEYWORD', 'LOCATION_MARKER', 'CONNECTIVE_WORD', 
          'DATE', 'START_DATE', 'END_DATE', 'NUMBER', 'SYMBOL', 'MONEY', 'RESOURCE', 
          'CONDITIONS', 'TIME', 'USERNAME', 'DEPARTURE', 'ARRIVAL', 'LOCATION', 
          'SERVICE', 'ARTICLE_CONJUNCTION')

# Define action keywords - commands that initiate an action
action_keywords = ['List', 'Book a', 'Confirm a', 'Pay', 'Cancel a', 
                   'Reserve a', 'How many', 'Duration of']

# Define context keywords - words that provide context to actions
context_keywords = ['on', 'For', 'Schedule', 'are there', 'Returning', 
                    'cost']

all_keywords = action_keywords + context_keywords

# Define location markers separately - they help identify departure/arrival/location
location_markers = ['in', 'at', 'from', 'to']

# Define connective words - words that connect clauses or phrases
connective_words = ['that']

# Generate regex patterns for each category
t_ACTION_KEYWORD = r'\b(?:' + r'|'.join(action_keywords) + r')\b'

t_CONTEXT_KEYWORD = r'\b(?:' + r'|'.join(context_keywords) + r')\b'

t_LOCATION_MARKER = r'\b(?:' + r'|'.join(location_markers) + r')\b'

t_CONNECTIVE_WORD = r'\b(?:' + r'|'.join(connective_words) + r')\b'

t_START_DATE = r'(?<=\bfrom\b\s).+?(?=\s\bto\b)|(?<=\bon\b\s).+?(?=\s\bat\b)'

t_END_DATE = r'(?<=\breturning on\s).+?(?=\s(?:at)\b)|' \
             r'(?<=\bto\s).+?(?=\s(?:for)\b)|' \
             r'(?<=\bto\s).+?(?=\.)'

t_DATE = r'(?<=\bon\s)((?!\b(?:in|at|from|to)\b).)+?(?=\.)'

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
t_ARRIVAL = r'(?<=\bTo\b\s)([a-zA-Z\s]+?)(?=\s\bFrom\b)|'\
            r'(?<=\bTo\b\s)([a-zA-Z\s]+?)(?=\s*\.)|'\
            r'(?<=\bTo\b\s)([a-zA-Z\s]+?)(?=\s\b(?:' + r'|'.join(all_keywords) + r')\b)'

t_LOCATION = r'(?<=\bin\b\s)([a-zA-Z\s]+?)(?=\s\b(?:' + r'|'.join(all_keywords) + r')\b)|'\
             r'(?<=\bin\b\s)([a-zA-Z\s]+?)(?=\s*\.)'

t_SERVICE = r'(?<=\ba\s)(?!(?:' + r'|'.join(all_keywords) + r')\b)([A-Za-z]+(?:\s[A-Za-z]+)?)(?=\s(?:' + t_RESOURCE + r')\b)|'\
            r'(?<=\bList\s)([A-Za-z]+(?:\s[A-Za-z]+)?)(?=\s\bSchedule\b)|'\
            r'(?<=\bfor\s)([A-Za-z]+(?:\s[A-Za-z]+)?)(?=\s\bfor\b)|'\
            r'(?<=\bat\s)([A-Za-z]+(?:\s[A-Za-z]+)?)(?=\s(?:From|from)\b)'

t_ARTICLE_CONJUNCTION = r'\b(a|and)\b'


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

# Provide the input data
data = "How many tickets are there from USA to Jamaica."

# Feed the input data to the lexer
lexer.input(data)

# Tokenize and print the output
print("\nTokenized Output:\n")
while True:
    tok = lexer.token()  # Extract the next token
    if not tok:
        break # Stop when no more tokens are available
    print(tok)



# --- Parser
# Define the grammar rules for your parser
# Parser rules with unique names to avoid conflicts with token names


def p_command(p):
    '''COMMAND : booking_command
               | list_command
               | payment_command
               | inquiry_command'''
    p[0] = ('COMMAND', p[1])


def p_list_command(p):
    '''list_command : ACTION_KEYWORD RESOURCE LOCATION_MARKER DEPARTURE LOCATION_MARKER ARRIVAL SYMBOL
                    | ACTION_KEYWORD SERVICE CONTEXT_KEYWORD SYMBOL'''
    if len(p) == 8:  # Handling the first variant
        p[0] = ('LIST_COMMAND', ('ACTION_KEYWORD', p[1]), ('RESOURCE', p[2]), ('LOCATION_MARKER', p[3]),
                ('DEPARTURE', p[4]), ('LOCATION_MARKER', p[5]), ('ARRIVAL', p[6]), ('SYMBOL', p[7]))
    elif len(p) == 5:  # Handling the second variant
        p[0] = ('LIST_COMMAND', ('ACTION_KEYWORD', p[1]), ('SERVICE', p[2]), ('CONTEXT_KEYWORD', p[3]),
                ('SYMBOL', p[4]))


def p_booking_command(p):
    '''booking_command : ACTION_KEYWORD RESOURCE LOCATION_MARKER ARRIVAL LOCATION_MARKER DEPARTURE SYMBOL
                       | ACTION_KEYWORD RESOURCE LOCATION_MARKER ARRIVAL LOCATION_MARKER DEPARTURE CONNECTIVE_WORD CONTEXT_KEYWORD CONDITIONS MONEY SYMBOL
                       | ACTION_KEYWORD RESOURCE LOCATION_MARKER ARRIVAL LOCATION_MARKER DEPARTURE ARTICLE_CONJUNCTION ARTICLE_CONJUNCTION RESOURCE LOCATION_MARKER START_DATE LOCATION_MARKER END_DATE SYMBOL
                       | ACTION_KEYWORD SERVICE RESOURCE LOCATION_MARKER DEPARTURE LOCATION_MARKER ARRIVAL CONTEXT_KEYWORD START_DATE LOCATION_MARKER TIME CONTEXT_KEYWORD USERNAME SYMBOL
                       | ACTION_KEYWORD RESOURCE LOCATION_MARKER DEPARTURE LOCATION_MARKER ARRIVAL CONTEXT_KEYWORD START_DATE LOCATION_MARKER TIME CONTEXT_KEYWORD CONTEXT_KEYWORD END_DATE LOCATION_MARKER TIME SYMBOL
                       | ACTION_KEYWORD RESOURCE LOCATION_MARKER SERVICE LOCATION_MARKER START_DATE LOCATION_MARKER END_DATE CONTEXT_KEYWORD USERNAME SYMBOL'''
    
    if len(p) == 8:  # Variant 1: Booking with ARRIVAL, DEPARTURE, and SYMBOL
        p[0] = ('BOOKING_COMMAND', ('ACTION_KEYWORD', p[1]), ('RESOURCE', p[2]), ('LOCATION_MARKER', p[3]),
                ('ARRIVAL', p[4]), ('LOCATION_MARKER', p[5]), ('DEPARTURE', p[6]), ('SYMBOL', p[7]))
    elif len(p) == 12:  # Variant 2: Booking with CONNECTIVE_WORD, CONTEXT_KEYWORD, CONDITIONS, and MONEY
        p[0] = ('BOOKING_COMMAND', ('ACTION_KEYWORD', p[1]), ('RESOURCE', p[2]), ('LOCATION_MARKER', p[3]),
                ('ARRIVAL', p[4]), ('LOCATION_MARKER', p[5]), ('DEPARTURE', p[6]), ('CONNECTIVE_WORD', p[7]),
                ('CONTEXT_KEYWORD', p[8]), ('CONDITIONS', p[9]), ('MONEY', p[10]), ('SYMBOL', p[11]))
    elif len(p) == 15:  # Variant 3: Booking with ARTICLE_CONJUNCTION and DATE elements
        p[0] = ('BOOKING_COMMAND', ('ACTION_KEYWORD', p[1]), ('RESOURCE', p[2]), ('LOCATION_MARKER', p[3]),
                ('ARRIVAL', p[4]), ('LOCATION_MARKER', p[5]), ('DEPARTURE', p[6]), ('ARTICLE_CONJUNCTION', p[7]),
                ('ARTICLE_CONJUNCTION', p[8]), ('RESOURCE', p[9]), ('LOCATION_MARKER', p[10]),
                ('START_DATE', p[11]), ('LOCATION_MARKER', p[12]), ('END_DATE', p[13]), ('SYMBOL', p[14]))
    elif len(p) == 14:  # Variant 4: Booking with SERVICE, DATE, TIME, and USERNAME elements
        p[0] = ('BOOKING_COMMAND', ('ACTION_KEYWORD', p[1]), ('SERVICE', p[2]), ('RESOURCE', p[3]),
                ('LOCATION_MARKER', p[4]), ('DEPARTURE', p[5]), ('LOCATION_MARKER', p[6]), ('ARRIVAL', p[7]),
                ('CONTEXT_KEYWORD', p[8]), ('START_DATE', p[9]), ('LOCATION_MARKER', p[10]), ('TIME', p[11]),
                ('CONTEXT_KEYWORD', p[12]), ('USERNAME', p[13]), ('SYMBOL', p[14]))
    elif len(p) == 17:  # Variant 5: Booking with DEPARTURE, ARRIVAL, DATES, and TIMES
        p[0] = ('BOOKING_COMMAND', ('ACTION_KEYWORD', p[1]), ('RESOURCE', p[2]), ('LOCATION_MARKER', p[3]),
                ('DEPARTURE', p[4]), ('LOCATION_MARKER', p[5]), ('ARRIVAL', p[6]), ('CONTEXT_KEYWORD', p[7]),
                ('START_DATE', p[8]), ('LOCATION_MARKER', p[9]), ('TIME', p[10]), ('CONTEXT_KEYWORD', p[11]),
                ('CONTEXT_KEYWORD', p[12]), ('END_DATE', p[13]), ('LOCATION_MARKER', p[14]), ('TIME', p[15]),
                ('SYMBOL', p[16]))
    elif len(p) == 11:  # Variant 6: Booking a Room with START_DATE, END_DATE, and USERNAME
        p[0] = ('BOOKING_COMMAND', ('ACTION_KEYWORD', p[1]), ('RESOURCE', p[2]), ('LOCATION_MARKER', p[3]),
                ('SERVICE', p[4]), ('LOCATION_MARKER', p[5]), ('START_DATE', p[6]), ('LOCATION_MARKER', p[7]),
                ('END_DATE', p[8]), ('CONTEXT_KEYWORD', p[9]), ('USERNAME', p[10]), ('SYMBOL', p[11]))

def p_payment_command(p):
    '''payment_command : ACTION_KEYWORD RESOURCE CONTEXT_KEYWORD SERVICE CONTEXT_KEYWORD USERNAME SYMBOL'''
    p[0] = ('PAYMENT_COMMAND', ('ACTION_KEYWORD', p[1]), ('RESOURCE', p[2]), ('CONTEXT_KEYWORD', p[3]),
            ('SERVICE', p[4]), ('CONTEXT_KEYWORD', p[5]), ('USERNAME', p[6]), ('SYMBOL', p[7]))

def p_inquiry_command(p):
    '''inquiry_command : ACTION_KEYWORD RESOURCE CONTEXT_KEYWORD LOCATION_MARKER DEPARTURE LOCATION_MARKER ARRIVAL SYMBOL'''
    p[0] = ('INQUIRY_COMMAND', ('ACTION_KEYWORD', p[1]), ('RESOURCE', p[2]), ('CONTEXT_KEYWORD', p[3]),
            ('LOCATION_MARKER', p[4]), ('DEPARTURE', p[5]), ('LOCATION_MARKER', p[6]), ('ARRIVAL', p[7]), ('SYMBOL', p[8]))

def p_departure(p):
    '''departure : DEPARTURE'''
    p[0] = ('DEPARTURE', p[1])

def p_arrival(p):
    '''arrival : ARRIVAL'''
    p[0] = ('ARRIVAL', p[1])

def p_action_keyword_rule(p):
    '''action_keyword_rule : ACTION_KEYWORD'''
    p[0] = ('ACTION_KEYWORD', p[1])

def p_resource_rule(p):
    '''resource_rule : RESOURCE'''
    p[0] = ('RESOURCE', p[1])

def p_service_rule(p):
    '''service_rule : SERVICE'''
    p[0] = ('SERVICE', p[1])

def p_location_marker_rule(p):
    '''location_marker_rule : LOCATION_MARKER'''
    p[0] = ('LOCATION_MARKER', p[1])

def p_context_keyword_rule(p):
    '''context_keyword_rule : CONTEXT_KEYWORD'''
    p[0] = ('CONTEXT_KEYWORD', p[1])

def p_start_date_rule(p):
    '''start_date_rule : START_DATE'''
    p[0] = ('START_DATE', p[1])

def p_time_rule(p):
    '''time_rule : TIME'''
    p[0] = ('TIME', p[1])

def p_username_rule(p):
    '''username_rule : USERNAME'''
    p[0] = ('USERNAME', p[1])

def p_symbol_rule(p):
    '''symbol_rule : SYMBOL'''
    p[0] = ('SYMBOL', p[1])

# Error handling
def p_error(p):
    if p:
        print(f"Syntax error at token '{p.value}', line {p.lineno}")
    else:
        print("Syntax error at end of input")



# Build the parser
parser = yacc()

# Test the parser with an input string
input_data = data
result = parser.parse(input_data)

print("\nParsed Result:")
print(result)



# Stuff to look out for (Parser):

# When reserving a ticket the customer must make a down payment of 60 % of the total cost
# When ever the keyword confirm is used, we take the full amount from the customer
# When Booking a plane ticket we have three option: The customer can Pay for the ticket then they have to confirm the ticket and also they have the option of cancelling the ticket.
# When Booking a reservation for the hotel we have four option: The customer can reserve the room, confirm the room, cancel the room and pay for the room.



# Example of Strings that can be tokenized:

# Working:

# List Knutsford Express Schedule - Working
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



# issues to tell Kemar:
# the 6th rule for booking command is exactly the same as reservtion command