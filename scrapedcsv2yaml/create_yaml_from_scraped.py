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

def process_csv(file_name):
    df = pd.read_csv(file_name, keep_default_na = False)

    forms_with_info = []

    df = df.truncate(after = 1000)
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

    POSSIBLE_SUBJECTS = ["0s", "1s", "1p", "2s", "2p", "21p", "3s", "3'", "3p", "X"]
    has_a_subj = False
    for subj in POSSIBLE_SUBJECTS:
        if subj in form_with_info["Abbreviated Gloss"]:
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
# The "Gloss" field contains this info in a list (+ info about ind vs. conj etc.)
# So a verb with only one participant will have len(Gloss) = 2 e.g. ['First person singular subject', 'independent ']
# Whereas a verb with two participants will have len(Gloss) = 3 e.g. ['First person singular subject', 'Third person singular object', 'independent ']
def add_person_and_number(form_with_info):
    # Gloss is a list, but it initially gets read as a string and must be converted to a lsit
    gloss = form_with_info["Gloss"].strip('][').replace("'","").split(', ')
    gloss_subj_dict = {
        "First person singular subject" : "1Sg",
        "First person inclusive plural subject" : "Incl",
        "First person exclusive plural subject" : "Excl",
        "Second person singular subject" : "2Sg",
        "Second person plural subject" : "2Pl",
        "Third person singular subject" : "3Sg",
        "Third person obviative subject" : "3SgObv",
        "Third person obviative subject; number not shown" : "3Obv", # ???
        "Third person plural subject" : "3Pl",
        "Singular inanimate subject" : "0Sg",
        'Indefinite subject/actor (often translated as an unspecified <i>they</i>)': "X"
    }
    gloss_obj_dict = {
        "First person singular object" : "1Sg",
        "First person object; number not shown" : "1",
        "Second person singular object" : "2Sg",
        "Third person singular object" : "3Sg",
        "Third person obviative object" : "3SgObv",
        "Third person object: number not shown" : "3",
        "Singular inanimate object" : "0Sg",
        "Inanimate object; number not shown" : "0",
        "Inanimate obviative object; number not shown" : "0"
    }

    # Add info for the first participant
    participant = gloss[0]
    if participant in gloss_subj_dict.keys():
        form_with_info["Subject"] = gloss_subj_dict[participant]
    else:
        form_with_info["Subject"] = "?" # So we take note of info we can't currently handle
    # If there's a second participant (i.e. it's transitive), add their info too
    if len(gloss) == 3 and (not gloss[1] == "augmented") and (not gloss[1] == "independent"):
        participant = gloss[1]
        if participant in gloss_obj_dict.keys():
            form_with_info["Object"] = gloss_obj_dict[participant]
        else:
            form_with_info["Object"] =  "?"
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
