# parser.py
from ply.yacc import yacc
from lexer import tokens  # Import the token list from lexer.py

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

# Test the parser (optional, for testing the parser in isolation)
if __name__ == '__main__':
    data = "How many tickets are there from USA to Jamaica."
    result = parser.parse(data)

    print("\nParsed Result:")
    print(result)