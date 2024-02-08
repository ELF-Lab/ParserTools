import argparse
import pandas as pd
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '../csv2yaml'))
from create_yaml import create_output_directory

POS_TO_KEEP = ["vai + o", "vta", "vai", "vii", "vti", "vti2", "vti3", "vti4"]
POS_WITH_CLASS_IN_FILE_NAME = ["VAI", "VTA", "VII", "VTI"]
vowels = ["i", "e", "o", "a"]
forms_with_missing_info = []
PARTICIPANT_TAG_CONVERSIONS = {
    "0" : "?",
    "0'" : "?",
    "0's" : "0SgObv",
    "0p" : "0PlProx",
    "0s" : "0SgProx",
    "1" : "?",
    "1s" : "1Sg",
    "1p" : "Excl",
    "2" : "?",
    "2s" : "2Sg",
    "2p" : "2Pl",
    "21p" : "Incl",
    "3" : "?",
    "3'" : "?",
    "3's" : "3SgObv",
    "3'p" : "3PlObv",
    "3s" : "3SgProx",
    "3p" : "3PlProx",
    "X" : "X"
}
POSSIBLE_PARTICIPANTS = PARTICIPANT_TAG_CONVERSIONS.keys()

def process_csv(file_name):
    df = pd.read_csv(file_name, keep_default_na = False)

    forms_with_info = []

    df = df.truncate(after = 10000)
    for index, row in df.iterrows():
        row = row.to_dict()
        # Grab only the verbs!
        if row["POS"] in POS_TO_KEEP:
            row = tidy_entry(row)
            if missing_info_check(row):
                row = format_entry(row)
                forms_with_info.append(row)
            else:
                forms_with_missing_info.append(row)

    return forms_with_info

# Takes one row at a time
# Returns a bool, True = keep it in, False = remove it
def missing_info_check(form_with_info):
    POSSIBLE_ORDERS = ["ind", "ch-conj", "conj", "imp", "part", "ic"]
    has_an_order = False
    for order in POSSIBLE_ORDERS:
        if order in form_with_info["Abbreviated Gloss"]:
            has_an_order = True

    # Check for missing stem OR an erroenous stem we noticed
    has_a_stem = (form_with_info["Stem"] != "" and form_with_info["Stem"] != "akwaakwak")

    has_a_subj = False
    glosses = form_with_info["Abbreviated Gloss"].split()
    if len(glosses) > 0:
        potential_subj = glosses[0]
        if potential_subj in POSSIBLE_PARTICIPANTS:
            has_a_subj = True

    return has_an_order and has_a_stem and has_a_subj

def tidy_entry(form_with_info):
    form_with_info["Abbreviated Gloss"] = form_with_info["Abbreviated Gloss"].strip()
    form_with_info["Stem"] = (form_with_info["Stem"].replace("/", "")).replace("-", "")

    if form_with_info["POS"] == "vai + o":
        form_with_info["POS"] = "vaio"
    form_with_info["POS"] = form_with_info["POS"].upper()

    return form_with_info

# Manages the adding of fields we need for our new CSV
def format_entry(form_with_info):
    form_with_info = add_order(form_with_info)

    # Dictionary uses VTI/VTI2/VTI3/VTI4 as POS, but we want to convert all of those to just VTI
    # However, this info lets us easily determine class
    # So we will assign class *first* before we lose those labels, then lose them!
    form_with_info = add_class(form_with_info)
    if "VTI" in form_with_info["POS"]:
        form_with_info["POS"] = "VTI"

    form_with_info = add_person_and_number(form_with_info)

    form_with_info = add_mode(form_with_info)

    form_with_info = add_negation(form_with_info)

    return form_with_info

# Ind, Cnj, Imp -- what about changed conjunct? No default
def add_order(form_with_info):
    short_gloss = form_with_info["Abbreviated Gloss"]

    if "ind" in short_gloss:
        order = "Ind"
    elif "ch-conj" in short_gloss:
        order = "?"
    elif "conj" in short_gloss:
        order = "Cnj"
    elif "imp" in short_gloss:
        order = "Imp"
    elif "ic" in short_gloss:
        order = "?"
    elif "part" in short_gloss:
        order = "Particip"
    else:
        print(f"\nERROR: Form {form_with_info['Inflectional Form']} does not have an expected order value.  Please investigate this form in the spreadsheet and update the code accordingly.  Exiting...")
        sys.exit()

    form_with_info["Order"] = order
    return form_with_info

# Add an entry to the dict that indicates the class of the stem (e.g. n, am, etc.)
# For some POS, like VAIO, we don't want the class in the file name at all
def add_class(form_with_info):
    pos = form_with_info["POS"]
    stem = form_with_info["Stem"]

    verb_class = ""
    if pos == "VTA":
        if stem.endswith("aw"):
            verb_class = "aw"
        elif stem.endswith("w") and not stem[-2] in vowels:
            verb_class = "Cw"
        elif stem.endswith("N"):
            verb_class = "n"
        # This condition is needlessly explicit, just to be clear about the categories
        elif not stem[-1] in vowels and not stem[-1] == "s" and not stem[-1] == "N":
            verb_class = "C"
        # Remaining classes: s, irr
    elif pos == "VAI":
        print(stem)
        if stem.endswith("n"):
            verb_class = "n"
        elif stem.endswith("m") and stem[-2] != "a":
            verb_class = "m"
        elif stem.endswith("m") and stem[-2] == "a":
            verb_class = "am"
        elif stem [-1] in vowels and stem[-2] in vowels:
            verb_class = "VV"
        elif stem[-1] in vowels:
            verb_class = "V"
        # Remaining classes: rcp, rfx
    elif pos == "VII":
        if stem.endswith("d"):
            verb_class = "d"
        elif stem.endswith("n"):
            verb_class = "n"
        elif stem [-1] in vowels and stem[-2] in vowels:
            verb_class = "VV"
        elif stem [-1] in vowels:
            verb_class = "V"
        # Remaining classes: none!
    if "VTI" in pos:
        if pos == "VTI":
            verb_class = "am"
        elif pos == "VTI2":
            verb_class = "oo"
        # Remaining classes: aa, i

    # Make sure we assigned a class where needed
    if verb_class:
        form_with_info["Class"] = verb_class
    elif pos in POS_WITH_CLASS_IN_FILE_NAME:
        print(f"\nERROR: You need to assign a class (e.g. info about the final characters in the stem) to a form with this stem: {form_with_info['Stem']}. (POS: {pos})  Exiting...")
        sys.exit()
    return form_with_info

# Add 1SG, 3PLObv, etc.
# Transitive verbs (VTA, VTI) will have two participants
# Intransitive verbs (VAI, VII) will have one participant
# Seems like VAIO can go either way
def add_person_and_number(form_with_info):
    short_gloss = form_with_info["Abbreviated Gloss"].split()
    if "-" in short_gloss:
        short_gloss.remove("-")

    # Add info for the first participant
    subject_participant = short_gloss[0]
    form_with_info["Subject"] = PARTICIPANT_TAG_CONVERSIONS[subject_participant]
    # If there's a second participant (i.e. it's transitive), add their info too
    if len(short_gloss) > 1 and short_gloss[1] in POSSIBLE_PARTICIPANTS:
        object_participant = short_gloss[1]
        form_with_info["Object"] = PARTICIPANT_TAG_CONVERSIONS[object_participant]
    else:
        form_with_info["Object"] = "NA"

    return form_with_info

# Neu, Prt, Dub, DubPrt, with Neu being the default
def add_mode(form_with_info):
    short_gloss = form_with_info["Abbreviated Gloss"]

    if "pret" in short_gloss and "dub" in short_gloss:
        mode = "DubPrt"
    elif "pret" in short_gloss:
        mode = "Prt"
    elif "dub" in short_gloss:
        mode = "Dub"
    else:
        mode = "Neu"

    form_with_info["Mode"] = mode

    return form_with_info

# Neg, Pos, with Pos being the default
def add_negation(form_with_info):
    short_gloss = form_with_info["Abbreviated Gloss"]

    if "neg" in short_gloss:
        negation = "Neg"
    else:
        negation = "Pos"

    form_with_info["Negation"] = negation
    return form_with_info

# Reminder: forms_with_info is a list of dicts
def write_new_csv(forms_with_info, output_dir):
    CSV_HEADER = "Paradigm,Order,Class,Lemma,Stem,Subject,Object,Mode,Negation,Form1Surface,Form1Split,Form1Source"

    with open(output_dir + 'inflectional_forms_for_yaml.csv', "w+") as csv:
        csv.write(CSV_HEADER + "\n")
        for form_with_info in forms_with_info:
            print(form_with_info)
            csv.write(form_with_info["POS"] + ",") # Paradigm
            csv.write(form_with_info["Order"] + ",") # Order
            if "Class" in form_with_info.keys(): # Class
                csv.write(form_with_info["POS"] + "_" + form_with_info["Class"] + ",")
            else:
                csv.write(form_with_info["POS"] + ",")
            csv.write(form_with_info["Lemma"] + ",") # Lemma
            csv.write(form_with_info["Stem"] + ",") # Stem
            csv.write(form_with_info["Subject"] + ",") # Subject
            csv.write(form_with_info["Object"] + ",") # Object
            csv.write(form_with_info["Mode"] + ",") # Mode
            csv.write(form_with_info["Negation"] + ",") # Negation
            csv.write(form_with_info["Inflectional Form"] + ",") # Form1Surface
            csv.write("\n") # for the new line

def main():
    # Sets up argparse.
    parser = argparse.ArgumentParser(prog="create_if_yaml")
    parser.add_argument("if_csv_path", type=str, help="Path to the spreadsheet.")
    parser.add_argument("output_parent_directory", type=str, help="Path to the folder where the yaml files will be saved (inside their own subdirectory).")
    args = parser.parse_args()

    output_directory = create_output_directory(args.output_parent_directory)

    forms_with_info = process_csv(args.if_csv_path)

    write_new_csv(forms_with_info, output_directory)

    print(args.if_csv_path, output_directory)

if __name__ == '__main__':
    main()
