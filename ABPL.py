import sys
sys.path.insert(0, "ply-master/ply-master/src")


from ply.lex import lex
from ply.yacc import yacc

# --- Tokenizer

tokens = ('KEYWORD', 'DATE')

# Case-insensitive keywords
t_KEYWORD = r'(?i)List|Book|Confirm|Pay|From|To|On|For|Schedule|Reservation|Cancel|Cost|Duration'

# Regex for dates (abbreviated and full month names only)
t_DATE = r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{1,2},\d{4}\b|' \
         r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2},\d{4}\b)'

# Ignored characters
t_ignore = ' \t'



# Build the lexer object
lexer = lex()