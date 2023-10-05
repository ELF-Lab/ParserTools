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

def print_lexc(lexc_file, pos_mode, multichar_symbols, prefix_lexicon,
               lemma_lexicon, subclass_lexicons, flag_lexicons,
               prefix_wb_lexicon,suffix_wb_lexicons, suffix_lexicons):
    lexc_f = open(lexc_file,"w")
    print_multichar_symbols(multichar_symbols,lexc_f)
    print_rootlex([f"{pos_mode}_Prefix"], lexc_f)
    print_sublex(f"{pos_mode}_Prefix", prefix_lexicon, lexc_f)
    print_sublex(f"{pos_mode}_Prefix_WB",prefix_wb_lexicon, lexc_f)
    print_sublex(f"{pos_mode}_Stems",lemma_lexicon, lexc_f)              

    for stem_type in flag_lexicons:
        print_subclass_comment(pos_mode,stem_type, lexc_f)
        print_sublex(f"{pos_mode}_{stem_type}_Subclass",subclass_lexicons[stem_type], lexc_f)
        print_sublex(f"{pos_mode}_{stem_type}_Flags",flag_lexicons[stem_type], lexc_f)
        for rflag, _, _ in flag_lexicons[stem_type]:
            print_sublex(f"{pos_mode}_{stem_type}_{get_val(rflag)}_WB",suffix_wb_lexicons[(stem_type,rflag)], lexc_f)
            print_sublex(f"{pos_mode}_{stem_type}_{get_val(rflag)}_Endings",suffix_lexicons[(stem_type,rflag)], lexc_f)
    
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

def add_prefix_entry(prefix, pos_mode, prefix_lexicon, multichar_symbols):
    pflag = SET_NO_PREFIX_FLAG if prefix == "" else f"@P.Prefix.{prefix}@"
    rflag = CHECK_NO_PREFIX_FLAG if prefix == "" else f"@R.Prefix.{prefix}@"
    multichar_symbols.add(pflag)
    multichar_symbols.add(rflag)                
    prefix_lexicon.add((f"{pflag}{prefix}",f"{pflag}",f"{pos_mode}_Prefix_WB"))
    return pflag, rflag

def add_stem_entry(stem, lemma, stem_type, pos_mode, rflag, lemma_lexicon,
                   suffix_lexicons, flag_lexicons, suffix_wb_lexicons,
                   subclass_lexicons):

    lemma_lexicon.add((stem, f"{lemma}", f"{pos_mode}_{stem_type}_Subclass"))
    if not (stem_type,rflag) in suffix_lexicons:
        suffix_lexicons[(stem_type,rflag)] = set()
        suffix_wb_lexicons[(stem_type,rflag)] = set([("%>%>","0",f"{pos_mode}_{stem_type}_{get_val(rflag)}_Endings")])
    if not stem_type in flag_lexicons:
        flag_lexicons[stem_type] = set()
        subclass_lexicons[stem_type] = set()            

def strip_order(tag):
    if "_" in tag:
        return tag[:tag.find("_")]
    return tag

def add_ending_entry(stem_type, rflag, row, suffix, flag_lexicons, subclass_lexicons, suffix_lexicons,
                     multichar_symbols, pos_mode):
    flag_lexicons[stem_type].add((rflag,rflag,f"{pos_mode}_{stem_type}_{get_val(rflag)}_WB"))
    subclass_lexicons[stem_type].add(("0",f"+{strip_order(pos_mode)}",f"{pos_mode}_{stem_type}_Flags"))

    if "Object" in row and not isnan(row["Object"]):
        suffix_tags = f"+{row['Order']}+{row['Negation']}+{row['Mode']}+{row['Subject']}+{row['Object']}"
    else:
        suffix_tags = f"+{row['Order']}+{row['Negation']}+{row['Mode']}+{row['Subject']}"
    suffix_tags = escape(suffix_tags)
    
    suffix_lexicons[(stem_type,rflag)].add((f"{suffix}", suffix_tags))
    for tag in suffix_tags.split("+") + [pos_mode]:
        if tag != "" and tag[0] != "@":
            multichar_symbols.add(f"+{tag}")

def longest_match(line, stem_types):
    match = [(line.endswith(st), len(st), st) for st in stem_types]
    match.sort(reverse=True)
    ismatch, length, st = match[0]
    if ismatch:
        return st
    return None

def get_row_pos(tag):
    if tag == "vai+o":
        return "VAIO"
    if tag[:3] in ["vai", "vii", "vta", "vti"]:
        return tag[:3].upper()
    raise ValueError

def find_stem_type(lemma, stem, opd_pos):
    for opos, pat, string, stype in [("vii", "^.*[aa|ii|oo|e]$",lemma,"VII_VV"),
                                     ("vii", "^.*[i|o|u]$", lemma, "VII_V"),
                                     ("vii", "^.*[n]$", lemma, "VII_n"),
                                     ("vii", "^.*[d]$", lemma, "VII_d"),
                                     ("vai", "^.*[aa|ii|oo|e]$",lemma, "VAI_VV"),
                                     ("vai", "^.*[i|o|u]$", lemma,"VAI_V"),
                                     ("vai", "^.*[n]$", lemma,"VAI_n"),
                                     ("vai", "^.*[m]$", lemma,"VAI_m"),
                                     ("vai2", "^.*am$", lemma,"VAI_am"),
                                     ("vta", "^.*aw$", lemma, "VTA_aw"),
                                     ("vta", "^.*w[bcdfghjklmnpstwz'NS]$", stem, "VTA_Cw"),
                                     ("vta", "^.*s$", stem, "VTA_s"),
                                     ("vta", "^.*n$", stem, "VTA_n"),
                                     ("vta", "^.*[bcdfghjklmnpstwz'NS]$", stem, "VTA_C"),
                                     ("vti1","^.*am$", lemma, "VTA_am"),
                                     ("vti2","^.*on$", lemma, "VTA_oo"),
                                     ("vti3","^.*in$", lemma, "VTA_i"),
                                     ("vti4","^.*an$", lemma, "VTA_aa")]:
        if opd_pos == opos and re.match(pat,string):
            return stype
    
    print(f"Warning: Can't identify class for {opd_pos} \"{lemma}\" (stem=\"{stem}\"). This lexeme won't be added to the lexc file!")
    return None
    
def read_lexical_database(pos, pos_mode, stem_types, lemma_lexicon, database_file):
    table = pd.read_csv(database_file)
    for _, row in table.iterrows():
        row_pos = get_row_pos(row["part_of_speech_id"])
        if row_pos == pos:
            # Check that the formatting is correct
            if isnan(row["lemma"]) or isnan(row["stem"]) or isnan(row["part_of_speech_id"]):
                print(f"Warning: Skipping invalid row with empty entries")
                print(row)
                continue
            lemma = row["lemma"].strip()            
            stem = row["stem"].strip()
            opd_pos = row["part_of_speech_id"].strip()
            stem_type = find_stem_type(lemma,stem,opd_pos)
            if stem_type == None:
                continue
            if stem_type in ["VTA_C","VTA_wC"]:
                stem = re.sub("N$","n",stem)
                stem = re.sub("S$","s",stem)
            lemma_lexicon.add((stem,lemma,f"{pos_mode}_{stem_type}_Subclass"))
            
@click.command()
@click.option("--csv_file",required=True)
@click.option("--lexc_file",required=True)
@click.option("--database_file", required=True)
def main(csv_file, lexc_file, database_file):
    print(f"Convert {csv_file} to {lexc_file}. Read OPD lexemes from {database_file}")
    # We need several continuation lexicons under the Root lexicon:
    # Empty prefix, ni- and gi-prefix + P-flags
    prefix_lexicon = set() 

    # The "<<" prefix-stem boundary symbol which can trigger rules
    prefix_wb_lexicon = set()
    
    # Lemmas like "zanagad"
    lemma_lexicon = set()

    # The +POS_MODE symbol which indicates verb subclass (e.g. +VII)
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

    # The paradim and mode of this CSV file like VII_Ind
    pos_mode = os.path.splitext(os.path.basename(csv_file))[0]
    pos = pos_mode.split("_")[0]
    
    table = pd.read_csv(csv_file)
    # Each row in the spreadsheet becomes a lexicon entry.
    for _, row in table.iterrows():
        row["Subject"] = escape(row["Subject"])

        # Make sure the paradigm and order tags are defined.
        multichar_symbols.add(f"+{row['Paradigm']}")
        multichar_symbols.add(f"+{row['Order']}")
        
        prefix_wb_lexicon.add((escape("<<"),escape("<<"),f"{pos_mode}_Stems"))

        # There may be up to 4 forms on the same row
        for form in [row[f"Form{n}Split"] for n in range(1,5) if f"Form{n}Split" in row]:
            # Skip non-existent forms
            if not type(form) == type('') or form == "":
                continue
            lemma = row["Lemma"]
            stem_type = row["Class"]
            stem_types.add(stem_type)
            prefix, _, suffix = split(form)
            stem = row["Stem"]
            
            pflag, rflag = add_prefix_entry(prefix,
                                            pos_mode,
                                            prefix_lexicon,
                                            multichar_symbols)
            
            # Stem
            add_stem_entry(stem, lemma, stem_type, pos_mode, rflag,
                           lemma_lexicon, suffix_lexicons, flag_lexicons,
                           suffix_wb_lexicons, subclass_lexicons)
            
            # Ending
            add_ending_entry(stem_type, rflag, row, suffix, flag_lexicons,
                             subclass_lexicons, suffix_lexicons, multichar_symbols,
                             pos_mode)

    read_lexical_database(pos, pos_mode, stem_types, lemma_lexicon, database_file)
    
    print_lexc(lexc_file, pos_mode, multichar_symbols, prefix_lexicon,
               lemma_lexicon, subclass_lexicons, flag_lexicons,
               prefix_wb_lexicon,suffix_wb_lexicons, suffix_lexicons)
    
if __name__=="__main__":
    main()
