import re

SEP="<<<SEP>>>"
COMMENT_BLOCK_WIDTH=80
INITIAL_SPACE=10

# Patterns and substitutions which can be used to translate lexc
# sublexicon names to comments using re.sub().
patterns = [
    (r"(.*):Prefix", (r"Paradigm: \1",
                      r"Prefixes")),
    (r"(.*):PrefixBoundary", (r"Paradigm: \1",
                              r"Morpheme boundary between prefix and stem")),
    (r"(.*):PreElement", (r"Paradigm: \1",
                          r"Pre-verbs/nouns")),
    (r"(.*):Stems", (r"Paradigm: \1",
                     r"Stems")),
    (r"(.*):Class=(.*):Boundary", (r"Paradigm: \1, Class: \2",
                                   r"Morpheme boundary between stem and suffix")),
    (r"(.*):Class=(.*):Flags", (r"Paradigm: \1, Class: \2",
                                r"Flag diacritic governing combinations between",
                                r"prefix and ending")),
    (r"(.*):Class=(.*):Prefix=(.*):Order=(.*)", (r"Paradigm: \1, Class: \2, Prefix: \3, Order: \4",)),
    (r"(.*):Class=(.*):Prefix=(.*):Order=(.*):Endings", (r"Paradigm: \1, Class: \2, Prefix: \3, Order: \4",
                                                         r"Endings")),
]

def comment_str(lex_name):
    comment = None
    for pattern, subst in patterns:
        if re.match(pattern, lex_name):
            comment = re.sub(pattern, SEP.join(subst), lex_name)
            comment = comment.split(SEP)
    if comment == None:
        raise ValueError(
            f"Lexicon name {lex_name} does not match any comment patterns")
    return comment

def print_to_index(substring, string, i):
    string = [c for c in string]
    string[i:i+len(substring)] = substring
    return "".join(string)
    
def comment_block(lex_name):
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

