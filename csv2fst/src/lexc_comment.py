"""Functions for transforming sublexicon names like
   `VAIO_PrefixBoundary` into lexc comment blocks:

   ```
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !                                                                              !
   !         Paradigm: VAIO                                                       !
   !         Morpheme boundary between prefix and stem                            !
   !                                                                              !
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   ```
"""

import re

SEP="<<<SEP>>>"
COMMENT_BLOCK_WIDTH=80
INITIAL_SPACE=10

PATTERNS = [
    (r"(.*)_Prefix", (r"Paradigm: \1",
                      r"Prefixes")),
    (r"(.*)_PrefixBoundary", (r"Paradigm: \1",
                              r"Morpheme boundary between prefix and stem")),
    (r"(.*)_PreElement", (r"Paradigm: \1",
                          r"Pre-verbs/nouns")),
    (r"(.*)_Stems", (r"Paradigm: \1",
                     r"Stems")),
    (r"(.*)_Class=(.*)_Boundary", (r"Paradigm: \1, Class: \2",
                                   r"Morpheme boundary between stem and suffix")),
    (r"(.*)_Class=(.*)_Flags", (r"Paradigm: \1, Class: \2",
                                r"Flag diacritic governing combinations between",
                                r"prefix and ending")),
    (r"(.*)_Class=(.*)_Prefix=(.*)_Order=(.*)", (r"Paradigm: \1, Class: \2, Prefix: \3, Order: \4",)),
    (r"(.*)_Class=(.*)_Prefix=(.*)_Order=(.*)_Endings", (r"Paradigm: \1, Class: \2, Prefix: \3, Order: \4",
                                                         r"Endings")),
]
"""Patterns and substitutions which can be used to translate lexc
   sublexicon names to comments using re.sub().

"""

def comment_str(lex_name:str) -> str:
    """Transform lexc sublexicon name into a comment string for the lexc
       file.

    """
    comment = None
    for pattern, subst in PATTERNS:
        if re.match(pattern, lex_name):
            comment = re.sub(pattern, SEP.join(subst), lex_name)
            comment = comment.split(SEP)
    if comment == None:
        raise ValueError(
            f"Lexicon name {lex_name} does not match any comment patterns")
    return comment

def print_to_index(substring:str, string:str, i:int) -> str:
    """Replace the content starting at i in string and spanning for
       len(substring) symbols by substring."""
    string = [c for c in string]
    string[i:i+len(substring)] = substring
    return "".join(string)
    
def comment_block(lex_name:str) -> str:
    """Return a lexc comment block corresponding to sublexicon name
       lex_name"""
    border = "!" * COMMENT_BLOCK_WIDTH
    comment_template = "!" + " " * (COMMENT_BLOCK_WIDTH - 2) + "!"
    comment_lines = comment_str(lex_name)
    block = ([border,
              comment_template] +
             [print_to_index(l,
                             comment_template,
                             INITIAL_SPACE)
              for l in comment_lines] +
             [comment_template,
              border])

    return "\n".join(block)

