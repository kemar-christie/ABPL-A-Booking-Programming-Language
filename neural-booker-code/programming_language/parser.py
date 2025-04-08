# Copyright (c) 2025 Kemar Christie, Roberto James, Dwayne Gibbs, Tyoni Davis, Danielle Jones
# Authors: Kemar Christie, Roberto James, Dwayne Gibbs, Tyoni Davis, Danielle Jones

from ply.yacc import yacc
from lexer import tokens  # Import the token list from lexer.py

#semanrtic validation functions
def valid_date_format(date_str):
    import datetime
    try:
        datetime.datetime.strptime(date_str, "%b %d, %Y")  # '%b' matches abbreviated month names
        return True
    except ValueError:
        print(f"Error: Invalid date format '{date_str}'. Expected format: 'Jan 18, 2025'.")
        return False


def valid_time_format(time_str):
        import re

        # Regular expression to validate the time format
        time_regex = r"^(1[0-2]|0?[1-9]):[0-5][0-9] ?[APap][Mm]$|^(2[0-3]|1[0-9]|0?[0-9]):[0-5][0-9]$"
        time_str=time_str.strip()  # Remove leading/trailing whitespace
        if re.match(time_regex, time_str):
            return True
        else:
            print(f"Error: Invalid time '{time_str}'. Expected formats: '10:30 AM' or '19:30'.")
            return False


def validate_date_order(start_date, end_date):
    from datetime import datetime

    try:
        # Parse the dates into datetime objects
        start = datetime.strptime(start_date, "%b %d, %Y")
        end = datetime.strptime(end_date, "%b %d, %Y")

        # Check if the start date is earlier than the end date
        if start >= end:
            print(f"Error: Start date '{start_date}' must be earlier than end date '{end_date}'.")
            return False
        else:
            return True
    except ValueError as e:
        print(f"Invalid date format: {e}")
        return False    
# Parser rules with unique names to avoid conflicts with token names

def p_command(p):
    '''COMMAND : booking_command
               | list_command
               | payment_command
               | inquiry_command
               | rent_command
               | confirm_command'''

    # Recursive function for semantic validation
    def validate(node):
        # Helper variables to store start and end dates
        start_date = None
        end_date = None

        if isinstance(node, tuple):  # If the node is a tuple, traverse it
            for element in node:  # Iterate through tokens
                # Identify if a token is a start or end date
                if isinstance(element, tuple) and element[0] == "START_DATE":
                    start_date = element[1]  # Extract the start date string
                    if not valid_date_format(start_date):  # Validate the date format
                        return False
                if isinstance(element, tuple) and element[0] == "END_DATE":
                    end_date = element[1]  # Extract the end date string
                    if not valid_date_format(end_date):  # Validate the date format
                        return False
                if isinstance(element, tuple) and element[0] == "TIME":  # Validate time tokens
                    time_str = element[1]
                    if not valid_time_format(time_str):
                        return False
                elif isinstance(element, tuple):  # Recur for nested tuples
                    if not validate(element):
                        return False

            # Call validate_date_order if both start_date and end_date are available
            if start_date and end_date:
                if not validate_date_order(start_date, end_date):
                    return False

        return True  # All validations passed

    
    
    # Perform semantic validation on the parsed structure
    if not validate(p[1]):  # Validate nested structures
        return  # Stop further processing on validation failure

    # If all validations pass, set the parsed result
    p[0] = ('COMMAND', p[1])


def p_booking_command(p):
    '''booking_command : ACTION_KEYWORD RESOURCE LOCATION_MARKER DEPARTURE LOCATION_MARKER ARRIVAL SYMBOL
                       | ACTION_KEYWORD RESOURCE LOCATION_MARKER ARRIVAL LOCATION_MARKER DEPARTURE SYMBOL
                       | ACTION_KEYWORD RESOURCE LOCATION_MARKER ARRIVAL LOCATION_MARKER DEPARTURE CONNECTIVE_WORD CONTEXT_KEYWORD CONDITIONS MONEY SYMBOL
                       | ACTION_KEYWORD RESOURCE LOCATION_MARKER ARRIVAL LOCATION_MARKER DEPARTURE ARTICLE_CONJUNCTION ARTICLE_CONJUNCTION RESOURCE LOCATION_MARKER START_DATE LOCATION_MARKER END_DATE SYMBOL
                       | ACTION_KEYWORD SERVICE RESOURCE LOCATION_MARKER DEPARTURE LOCATION_MARKER ARRIVAL CONTEXT_KEYWORD START_DATE LOCATION_MARKER TIME CONTEXT_KEYWORD USERNAME SYMBOL
                       | ACTION_KEYWORD RESOURCE LOCATION_MARKER DEPARTURE LOCATION_MARKER ARRIVAL CONTEXT_KEYWORD START_DATE LOCATION_MARKER TIME CONTEXT_KEYWORD CONTEXT_KEYWORD END_DATE LOCATION_MARKER TIME SYMBOL
                       | ACTION_KEYWORD RESOURCE LOCATION_MARKER SERVICE LOCATION_MARKER START_DATE LOCATION_MARKER END_DATE CONTEXT_KEYWORD USERNAME SYMBOL
                       | ACTION_KEYWORD RESOURCE LOCATION_MARKER DEPARTURE CONTEXT_KEYWORD DATE ARRIVAL CONTEXT_KEYWORD DATE SYMBOL
                       | ACTION_KEYWORD RESOURCE LOCATION_MARKER LOCATION LOCATION_MARKER START_DATE LOCATION_MARKER END_DATE CONTEXT_KEYWORD USERNAME SYMBOL
                       | ACTION_KEYWORD SERVICE RESOURCE LOCATION_MARKER DEPARTURE LOCATION_MARKER ARRIVAL CONTEXT_KEYWORD START_DATE LOCATION_MARKER TIME CONTEXT_KEYWORD NUMBER PASSENGER_TYPE SYMBOL
                       | ACTION_KEYWORD NUMBER RESOURCE CONTEXT_KEYWORD RESOURCE CONTEXT_KEYWORD DATE SYMBOL
                       | ACTION_KEYWORD NUMBER TICKET_TYPE RESOURCE CONTEXT_KEYWORD RESOURCE CONTEXT_KEYWORD DATE SYMBOL'''

    if len(p)==8: # Variant 1.1:
        p[0] = ('BOOKING_COMMAND', ('ACTION_KEYWORD', p[1]), ('RESOURCE', p[2]), ('LOCATION_MARKER', p[3]),
        ('DEPARTURE', p[4]), ('LOCATION_MARKER', p[5]), ('ARRIVAL', p[6]), ('SYMBOL', p[7]))
    elif len(p) == 8:  # Variant 1: Booking with ARRIVAL, DEPARTURE, and SYMBOL
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
    elif len(p) == 10: # New Variant
        p[0] = ('BOOKING_COMMAND', ('ACTION_KEYWORD', p[1]), ('RESOURCE', p[2]), ('LOCATION_MARKER', p[3]),
                ('DEPARTURE', p[4]), ('CONTEXT_KEYWORD', p[5]), ('DATE', p[6]), ('ARRIVAL', p[7]),
                ('CONTEXT_KEYWORD', p[8]), ('DATE', p[9]), ('SYMBOL', p[10]))
    elif len(p) == 12:
        p[0] = ('BOOKING_COMMAND', ('ACTION_KEYWORD', p[1]), ('RESOURCE', p[2]), ('LOCATION_MARKER', p[3]),
                ('LOCATION', p[4]), ('LOCATION_MARKER', p[5]), ('START_DATE', p[6]), ('LOCATION_MARKER', p[7]),
                ('END_DATE', p[8]), ('CONTEXT_KEYWORD', p[9]), ('USERNAME', p[10]), ('SYMBOL', p[11]))
    elif len(p) == 16:
        p[0]= ('BOOKING_COMMAND', ('ACTION_KEYWORD', p[1]), ('SERVICE', p[2]), ('RESOURCE', p[3]),
               ('LOCATION_MARKER', p[4]), ('DEPARTURE', p[5]), ('LOCATION_MARKER', p[6]), ('ARRIVAL', p[7]),
                ('CONTEXT_KEYWORD', p[8]), ('START_DATE', p[9]), ('LOCATION_MARKER', p[10]), ('TIME', p[11]),
                ('CONTEXT_KEYWORD', p[12]), ('NUMBER', p[13]), ('PASSENGER_TYPE', p[14]), ('SYMBOL', p[15]))
    elif len(p) == 9:  
        p[0] = ('BOOKING_COMMAND', ('ACTION_KEYWORD', p[1]), ('NUMBER', p[2]), ('RESOURCE', p[3]),
                ('CONTEXT_KEYWORD', p[4]), ('RESOURCE', p[5]), ('CONTEXT_KEYWORD', p[6]), ('DATE', p[7]), ('SYMBOL', p[8]))
    elif len(p) == 10:
        p[0] = ('BOOKING_COMMAND', ('ACTION_KEYWORD', p[1]), ('NUMBER', p[2]), ('TICKET_TYPE', p[3]), ('RESOURCE', p[4]),
                ('CONTEXT_KEYWORD', p[5]), ('RESOURCE', p[6]), ('CONTEXT_KEYWORD', p[7]), ('DATE', p[8]), ('SYMBOL', p[9]))


def p_list_command(p):
    '''list_command : LIST_KEYWORD RESOURCE LOCATION_MARKER DEPARTURE LOCATION_MARKER ARRIVAL SYMBOL
                    | LIST_KEYWORD CONTEXT_KEYWORD RENT_KEYWORD RESOURCE LOCATION_MARKER LOCATION SYMBOL
                    | LIST_KEYWORD SERVICE CONTEXT_KEYWORD SYMBOL
                    | LIST_KEYWORD SERVICE CONTEXT_KEYWORD LOCATION_MARKER DEPARTURE LOCATION_MARKER ARRIVAL SYMBOL
                    | LIST_KEYWORD CONTEXT_KEYWORD USERNAME SYMBOL'''

    if len(p) == 8:  # Handling the first variant
        p[0] = ('LIST_COMMAND', ('LIST_KEYWORD', p[1]), ('RESOURCE', p[2]), ('LOCATION_MARKER', p[3]),
                ('DEPARTURE', p[4]), ('LOCATION_MARKER', p[5]), ('ARRIVAL', p[6]), ('SYMBOL', p[7]))
    elif len(p) == 8:
        p[0] = ('LIST_COMMAND', ('LIST_KEYWORD', p[1]), ('CONTEXT_KEYWORD', p[2]),('RENT_KEYWORD', p[3]),
                ('RESOURCE',p[4]), ('LOCATION_MARKER', p[5]), ('LOCATION', p[6]), ('SYMBOL', p[7]))
    elif len(p) == 5:  # Handling the second variant
        p[0] = ('LIST_COMMAND', ('LIST_KEYWORD', p[1]), ('SERVICE', p[2]), ('CONTEXT_KEYWORD', p[3]),
                ('SYMBOL', p[4]))
    elif len(p) == 9:  #Handle third variant
        p[0] = ('LIST_COMMAND', ('LIST_KEYWORD', p[1]), ('SERVICE', p[2]), ('CONTEXT_KEYWORD', p[3]),
                ('LOCATION_MARKER', p[4]), ('DEPARTURE', p[5]), ('LOCATION_MARKER', p[6]), ('ARRIVAL', p[7]), 
                ('SYMBOL', p[8]))
    elif len(p) == 6:
        p[0] = ('LIST_COMMAND', ('LIST_KEYWORD', p[1]), ('CONTEXT_KEYWORD', p[2]), ('USERNAME', p[3]),
                ('SYMBOL', p[4]))
        


def p_payment_command(p):
    '''payment_command : ACTION_KEYWORD RESOURCE CONTEXT_KEYWORD SERVICE CONTEXT_KEYWORD USERNAME SYMBOL
                       | PAYMENT_TYPE SYMBOL'''
    if len(p)== 8:
        p[0] = ('PAYMENT_COMMAND', ('ACTION_KEYWORD', p[1]), ('RESOURCE', p[2]), ('CONTEXT_KEYWORD', p[3]),
            ('SERVICE', p[4]), ('CONTEXT_KEYWORD', p[5]), ('USERNAME', p[6]), ('SYMBOL', p[7]))
    elif len(p) == 3:
        p[0] = ('PAYMENT_COMMAND',('PAYMENT_TYPE',p[1]),('SYMBOL', p[2]))



        
def p_rent_command(p):
    '''rent_command : RENT_KEYWORD RESOURCE LOCATION_MARKER LOCATION LOCATION_MARKER START_DATE LOCATION_MARKER END_DATE CONTEXT_KEYWORD USERNAME SYMBOL'''

    p[0] = ('RENT_COMMAND', ('RENT_KEYWORD', p[1]), ('RESOURCE', p[2]), ('LOCATION_MARKER', p[3]),
            ('LOCATION', p[4]), ('LOCATION_MARKER', p[5]), ('START_DATE', p[6]), ('LOCATION_MARKER', p[7]),
            ('END_DATE', p[8]), ('CONTEXT_KEYWORD', p[9]), ('USERNAME', p[10]), ('SYMBOL', p[11]))


def p_inquiry_command(p):
    '''inquiry_command : INQUIRY_KEYWORD RESOURCE CONTEXT_KEYWORD LOCATION_MARKER DEPARTURE LOCATION_MARKER ARRIVAL SYMBOL
                        | INQUIRY_KEYWORD CONTEXT_KEYWORD CONTEXT_KEYWORD SERVICE LOCATION_MARKER DEPARTURE LOCATION_MARKER ARRIVAL CONTEXT_KEYWORD DATE SYMBOL'''
    if len(p)== 9: 
        p[0] = ('INQUIRY_COMMAND', ('INQUIRY_KEYWORD', p[1]), ('RESOURCE', p[2]), ('CONTEXT_KEYWORD', p[3]),
                ('LOCATION_MARKER', p[4]), ('DEPARTURE', p[5]), ('LOCATION_MARKER', p[6]), ('ARRIVAL', p[7]), ('SYMBOL', p[8]))
    elif len(p) == 12:
        p[0]= ('INQUIRY_COMMAND', ('INQUIRY_KEYWORD', p[1]), ('CONTEXT_KEYWORD', p[2]), ('CONTEXT_KEYWORD', p[3]),
                ('SERVICE', p[4]), ('LOCATION_MARKER', p[5]), ('DEPARTURE', p[6]), ('LOCATION_MARKER', p[7]),
                ('ARRIVAL', p[8]), ('CONTEXT_KEYWORD', p[9]), ('DATE', p[10]), ('SYMBOL', p[11]))

def p_confirm_command(p):
    '''confirm_command : CONFIRM_KEYWORD SERVICE ACTION_KEYWORD CONTEXT_KEYWORD USERNAME SYMBOL'''

    if len(p) == 7:  
        p[0] = ('CONFIRM_COMMAND', ('CONFIRM_KEYWORD', p[1]), ('SERVICE', p[2]), ('ACTION_KEYWORD', p[3]),
                ('CONTEXT_KEYWORD', p[4]), ('USERNAME', p[5]), ('SYMBOL', p[6]))
        
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
parser = yacc(optimize=False)

# Test the parser (optional, for testing the parser in isolation)
if __name__ == '__main__':
    
    data = "List Bookings for rob_jam1."
    result = parser.parse(data) 

    print("\nParsed Result:")
    print(result)


#Note:
#Book a flight from Montego Bay to New York.
#Extra space throws an error
#No full stop at the end should throw an error
# lexer and parser does not identify : List Knutsford Express from Kingston to May Pen on February 17, 2025 at 8:30 AM.
# ensure these are acceptable