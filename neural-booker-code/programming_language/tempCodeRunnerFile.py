
def p_command(p):
    '''COMMAND : list_command
               | booking_command'''
    p[0] = ('COMMAND', p[1])

def p_list_command(p):
    '''list_command : ACTION_KEYWORD RESOURCE LOCATION_MARKER DEPARTURE LOCATION_MARKER ARRIVAL SYMBOL
                    | ACTION_KEYWORD SERVICE CONTEXT_KEYWORD SYMBOL'''
    if len(p) == 8:  # First variant: List Command with RESOURCE
        p[0] = ('LIST_COMMAND', ('ACTION_KEYWORD', p[1]), ('RESOURCE', p[2]), ('LOCATION_MARKER', p[3]),
                ('DEPARTURE', p[4]), ('LOCATION_MARKER', p[5]), ('ARRIVAL', p[6]), ('SYMBOL', p[7]))
    elif len(p) == 5:  # Second variant: List Command with SERVICE
        p[0] = ('LIST_COMMAND', ('ACTION_KEYWORD', p[1]), ('SERVICE', p[2]), ('CONTEXT_KEYWORD', p[3]),
                ('SYMBOL', p[4]))

def p_booking_command(p):
    '''booking_command : ACTION_KEYWORD RESOURCE LOCATION_MARKER ARRIVAL LOCATION_MARKER DEPARTURE CONNECTIVE_WORD CONTEXT_KEYWORD CONDITIONS MONEY SYMBOL
                       | ACTION_KEYWORD RESOURCE LOCATION_MARKER ARRIVAL LOCATION_MARKER DEPARTURE SYMBOL'''
    if len(p) == 12:  # First variant: Booking Command with CONNECTIVE_WORD, CONTEXT_KEYWORD, CONDITIONS, MONEY
        p[0] = ('BOOKING_COMMAND', ('ACTION_KEYWORD', p[1]), ('RESOURCE', p[2]), ('LOCATION_MARKER', p[3]),
                ('ARRIVAL', p[4]), ('LOCATION_MARKER', p[5]), ('DEPARTURE', p[6]), ('CONNECTIVE_WORD', p[7]),
                ('CONTEXT_KEYWORD', p[8]), ('CONDITIONS', p[9]), ('MONEY', p[10]), ('SYMBOL', p[11]))
    elif len(p) == 8:  # Second variant: Booking Command without CONNECTIVE_WORD
        p[0] = ('BOOKING_COMMAND', ('ACTION_KEYWORD', p[1]), ('RESOURCE', p[2]), ('LOCATION_MARKER', p[3]),
                ('ARRIVAL', p[4]), ('LOCATION_MARKER', p[5]), ('DEPARTURE', p[6]), ('SYMBOL', p[7]))

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

def p_location_marker_rule(p):
    '''location_marker_rule : LOCATION_MARKER'''
    p[0] = ('LOCATION_MARKER', p[1])

def p_context_keyword_rule(p):
    '''context_keyword_rule : CONTEXT_KEYWORD'''
    p[0] = ('CONTEXT_KEYWORD', p[1])

def p_connective_word_rule(p):
    '''connective_word_rule : CONNECTIVE_WORD'''
    p[0] = ('CONNECTIVE_WORD', p[1])

def p_conditions_rule(p):
    '''conditions_rule : CONDITIONS'''
    p[0] = ('CONDITIONS', p[1])

def p_money_rule(p):
    '''money_rule : MONEY'''
    p[0] = ('MONEY', p[1])

def p_symbol_rule(p):
    '''symbol_rule : SYMBOL'''
    p[0] = ('SYMBOL', p[1])

# Error handling
def p_error(p):
    if p:
        print(f"Syntax error at token '{p.value}', line {p.lineno}")
    else:
        print("Syntax error at end of input")

