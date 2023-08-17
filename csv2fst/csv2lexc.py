import pandas as pd
import math
import click
import re
import os
from collections import defaultdict

"""
This script is a mess and needs to be refactored.
"""

SET_NO_PREFIX_FLAG = "@P.Prefix.NONE@"
CHECK_NO_PREFIX_FLAG = "@R.Prefix.NONE@"

# Used when formatting comments
PAD = "   "
CPREF = "!!"
CSUFF = "!!"

CLASSDICT={"vai":"VAI_V", }
def escape(sym):
    """ Escape special characters in lexc formalism """
    return re.sub("(?<!%)([<>0/])",r"%\1",sym)

def isnan(x):
    """ Return True if x represents an empty entry in the CSV file """
    try:
        return math.isnan(x)
    except:
        return False
    
def print_multichar_symbols(multichar_symbols,f):
    """ 
        Print the Multichar_Symbols section in the LEXC file. 
    """
    print("Multichar_Symbols", file=f)
    escaped = [escape(sym) for sym in multichar_symbols]
    print(" ".join(escaped), file=f)
    print("", file=f)
    
def print_rootlex(entries, f):
    """ 
        Print the root lexicon which currently contains just one entry 
        for a single verb subclass but which will in the future contain
        one entry for each verb subclass.  
    """
    print("LEXICON Root", file=f)
    entries = list(entries)
    entries.sort()
    for entry in entries:
        print(f"{entry} ;", file=f)
    print("", file=f)
    
def print_sublex(name, entries, f):
    """ 
        Print a sublexicon with a given name and entries. Each entry is 
        a 2- or 3-tuple containing an underlying analysi, a surface 
        realization and a potential constinuation lexicon name.
    """
    entries = list(entries)
    entries.sort(key = lambda x:(x[1], x[0])) # Sort lexicon entries
                                              # according to lemma. 
    print(f"LEXICON {name}", file=f)
    for entry in entries:
        surf, under, cont, *_ = list(entry) + ["#"]
        if under == surf:
            print(f"{under} {cont} ;", file=f)
        else:
            print(f"{under}:{surf} {cont} ;", file=f)
    print("", file=f)

def print_subclass_comment(subclass,stem_type, f):
    """ 
        Print a comment before endings for specific subclass and 
        stem-type
    """
    comment = f"Endings: Verb Class = {subclass}, Stem Type = {stem_type}"
    sepline = "!" * (2 * len(CPREF) + 2 * len(PAD) + len(comment))
    print(sepline, file=f)
    print(f"{CPREF}{PAD}{' '*len(comment)}{PAD}{CSUFF}", file=f)
    print(f"{CPREF}{PAD}{        comment }{PAD}{CSUFF}", file=f)
    print(f"{CPREF}{PAD}{' '*len(comment)}{PAD}{CSUFF}", file=f)
    print(sepline, file=f)
    print("",file=f)

def print_lexc(lexc_file, pos, multichar_symbols, prefix_lexicon,
               lemma_lexicon, subclass_lexicons, flag_lexicons,
               prefix_wb_lexicon,suffix_wb_lexicons, suffix_lexicons):
    lexc_f = open(lexc_file,"w")
    print_multichar_symbols(multichar_symbols,lexc_f)
    print_rootlex([f"{pos}_Prefix"], lexc_f)
    print_sublex(f"{pos}_Prefix", prefix_lexicon, lexc_f)
    print_sublex(f"{pos}_Prefix_WB",prefix_wb_lexicon, lexc_f)
    print_sublex(f"{pos}_Stems",lemma_lexicon, lexc_f)              

    for stem_type in flag_lexicons:
        print_subclass_comment(pos,stem_type, lexc_f)
        print_sublex(f"{pos}_{stem_type}_Subclass",subclass_lexicons[stem_type], lexc_f)
        print_sublex(f"{pos}_{stem_type}_Flags",flag_lexicons[stem_type], lexc_f)
        for rflag, _, _ in flag_lexicons[stem_type]:
            print_sublex(f"{pos}_{stem_type}_{get_val(rflag)}_WB",suffix_wb_lexicons[(stem_type,rflag)], lexc_f)
            print_sublex(f"{pos}_{stem_type}_{get_val(rflag)}_Endings",suffix_lexicons[(stem_type,rflag)], lexc_f)
    
def split(form):
    """ 
        Split segmented form like gi<<niimi>>siiminaaban into a prefix
        stem and suffix. Either the prefix or suffix or both may be 
        missing.
    """
    if not ">>" in form:
        print(f'Note: Appending suffix boundary at the end of "{form}".')
        form += ">>"
    if not "<<" in form:
        print(f'Note: Appending prefix boundary at the start of "{form}".')
        form = "<<" + form
    return re.split("<<|>>",form)

def get_val(flag):
    # @R.NAME.VAL@ => VAL
    return re.findall("[.][^.]*@",flag)[0][1:-1]

def is_alternant(stem, lemma, stem_type):
    """
        This function aims to figure out whether stem is the result of
        phonological alternation, which are handled using rules, or
        whether it is a genuine lexicalized variant of lemma, which have to
        be separately stored in the lexicon. 
    """
    lemma = lemma[:-len(stem_type)]
    stem = stem[:len(lemma)]
    return lemma == stem

def add_prefix_entry(prefix, pos, prefix_lexicon, multichar_symbols):
    pflag = SET_NO_PREFIX_FLAG if prefix == "" else f"@P.Prefix.{prefix}@"
    rflag = CHECK_NO_PREFIX_FLAG if prefix == "" else f"@R.Prefix.{prefix}@"
    multichar_symbols.add(pflag)
    multichar_symbols.add(rflag)                
    prefix_lexicon.add((f"{pflag}{prefix}",f"{pflag}",f"{pos}_Prefix_WB"))
    return pflag, rflag

def add_stem_entry(stem, lemma, stem_type, pos, rflag, lemma_lexicon,
                   suffix_lexicons, flag_lexicons, suffix_wb_lexicons,
                   subclass_lexicons):
    if is_alternant(stem, lemma, stem_type):
        stem = lemma 

    lemma_lexicon.add((stem, f"{lemma}", f"{pos}_{stem_type}_Subclass"))
    if not (stem_type,rflag) in suffix_lexicons:
        suffix_lexicons[(stem_type,rflag)] = set()
        suffix_wb_lexicons[(stem_type,rflag)] = set([("%>%>","0",f"{pos}_{stem_type}_{get_val(rflag)}_Endings")])
    if not stem_type in flag_lexicons:
        flag_lexicons[stem_type] = set()
        subclass_lexicons[stem_type] = set()            

def strip_order(tag):
    if "_" in tag:
        return tag[:tag.find("_")]
    return tag

def add_ending_entry(stem_type, rflag, row, suffix, flag_lexicons, subclass_lexicons, suffix_lexicons,
                     multichar_symbols, pos):
    flag_lexicons[stem_type].add((rflag,rflag,f"{pos}_{stem_type}_{get_val(rflag)}_WB"))
    subclass_lexicons[stem_type].add(("0",f"+{strip_order(pos)}",f"{pos}_{stem_type}_Flags"))

    if "Object" in row and not isnan(row["Object"]):
        suffix_tags = f"+{row['Order']}+{row['Negation']}+{row['Mode']}+{row['Subject']}+{row['Object']}"
    else:
        suffix_tags = f"+{row['Order']}+{row['Negation']}+{row['Mode']}+{row['Subject']}"
    suffix_tags = escape(suffix_tags)
    
    suffix_lexicons[(stem_type,rflag)].add((f"{suffix}", suffix_tags))
    for tag in suffix_tags.split("+") + [pos]:
        if tag != "" and tag[0] != "@":
            multichar_symbols.add(f"+{tag}")

def longest_match(line, stem_types):
    match = [(line.endswith(st), len(st), st) for st in stem_types]
    match.sort(reverse=True)
    ismatch, length, st = match[0]
    if ismatch:
        return st
    return None

def read_lexical_database(pos, stem_types, lemma_lexicon):
    database_fn = os.path.join("data",f"{pos}_stems.lexc")
    if not os.path.isfile(database_fn):
        print(f"Lexical database {database_fn} not found. No additional stems will be added")
        return
    
    for line in open(database_fn):
        line = line.strip()
        if line.endswith(f"{pos}_StemEndings ;"):
            lemma = line[:line.find(" ")]
            stem_type = longest_match(lemma, stem_types)
            if stem_type == None:
                print(f"Skip lexical entry: {lemma}. Can't identify stem type")
            else:
                lemma_lexicon.add((lemma, f"{lemma}", f"{pos}_{stem_type}_Subclass"))

def get_row_pos(tag):
    if tag == "vai+o":
        return "VAIO"
    if tag[:3] in ["vai", "vii", "vta", "vti"]:
        return tag[:3].upper()
    raise ValueError

def read_lexical_database(pos, stem_types, lemma_lexicon, database_file):
    table = pd.read_csv(database_file)
    for _, row in table.iterrows():
        row_pos = get_row_pos(row["part_of_speech_id"])
        if row_pos == pos:
            stem_class = find_stem_class(row["lemma"])
        
@click.command()
@click.option("--csv_file",required=True)
@click.option("--lexc_file",required=True)
@click.option("--database_file", required=True)
def main(csv_file, lexc_file, database_file):
    # We need several continuation lexicons under the Root lexicon:
    # Empty prefix, ni- and gi-prefix + P-flags
    prefix_lexicon = set() 

    # The "<<" prefix-stem boundary symbol which can trigger rules
    prefix_wb_lexicon = set()
    
    # Lemmas like zanagad
    lemma_lexicon = set()

    # The +POS symbol which indicates verb subclass (e.g. +VII)
    subclass_lexicons = {}

    # R-flags which govern combinations of prefixes and suffixes.
    flag_lexicons = {}

    # The ">>" stem-suffix boundary symbol which can trigger rules
    suffix_wb_lexicons = {}

    # Verb endings like +Ind+Neg+Neu+1Sg:siin which are specific to
    # each prefix ("", ni- or gi-) and stem-type (e.g. magad).
    suffix_lexicons = {}

    # We collect multichar symbols into this set. Boundary symbols and P-flags
    # for the empty prefix are always added.
    multichar_symbols = set(["<<",">>",SET_NO_PREFIX_FLAG,CHECK_NO_PREFIX_FLAG])

    # Collect all stem types
    stem_types = set()

    table = pd.read_csv(csv_file)
    # Each row in the spreadsheet becomes a lexicon entry.
    for _, row in table.iterrows():
        row["Subject"] = escape(row["Subject"])

        pos = f'{row["Paradigm"]}_{row["Order"]}'
        # Make sure the paradigm and order tags are defined.
        multichar_symbols.add(f"+{row['Paradigm']}")
        multichar_symbols.add(f"+{row['Order']}")
        
        #prefix_wb_lexicon.add((escape("<<"),"0",f"{pos}_Stems"))
        prefix_wb_lexicon.add((escape("<<"),escape("<<"),f"{pos}_Stems"))
        # Empty prefix is always possible so we'll add a flag sublexicon entry.
        #prefix_lexicon.add((SET_NO_PREFIX_FLAG, SET_NO_PREFIX_FLAG,f"{pos}_Stems"))
        # There may be up to 4 forms on the same row
        for form in [row[f"Form{n}Split"] for n in range(1,5) if f"Form{n}Split" in row]:
            # Skip non-existent forms
            if not type(form) == type('') or form == "":
                continue
            lemma = row["Lemma"]
            stem_type = row["Class"]
            stem_types.add(stem_type)
#            stem_type_endings[lemma[-1:]].add(stem_type)
#            stem_type_endings[lemma[-2:]].add(stem_type)
            prefix, stem, suffix = split(form)
            
            # Skip empty entries
            #if stem == "":
            #    continue
            pflag, rflag = add_prefix_entry(prefix,
                                            pos,
                                            prefix_lexicon,
                                            multichar_symbols)
            
            # Stem
            add_stem_entry(stem, lemma, stem_type, pos, rflag,
                           lemma_lexicon, suffix_lexicons, flag_lexicons,
                           suffix_wb_lexicons, subclass_lexicons)
            
            # Ending
            add_ending_entry(stem_type, rflag, row, suffix, flag_lexicons, subclass_lexicons, suffix_lexicons,
                             multichar_symbols, pos)

#    read_lexical_database(pos, stem_types, lemma_lexicon, database_file)
    
    print_lexc(lexc_file, pos, multichar_symbols, prefix_lexicon,
               lemma_lexicon, subclass_lexicons, flag_lexicons,
               prefix_wb_lexicon,suffix_wb_lexicons, suffix_lexicons)
if __name__=="__main__":
    main()
