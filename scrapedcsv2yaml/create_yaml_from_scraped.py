import argparse
import pandas as pd
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '../csv2yaml'))
from create_yaml import create_output_directory

POS_TO_KEEP = ["vai + o", "vta", "vai", "vii", "vti", "vti2", "vti3", "vti4"]
POS_WITH_CLASS_IN_FILE_NAME = ["VAI", "VTA", "VII", "VTI"]
vowels = ["i", "e", "o", "a"]

def process_csv(file_name):
    df = pd.read_csv(file_name, keep_default_na = False)

    forms_with_info = []

    df = df.truncate(after = 1000)
    for index, row in df.iterrows():
        row = row.to_dict()
        if row["POS"] in POS_TO_KEEP:
            lexical_info = format_entry(row)

            forms_with_info.append(lexical_info)

    return forms_with_info

# Add a "lexical_info" entry to each row: a string formatted as Stem+Class+Imp/Ind+Pos/Neg/N/A+Neu/Prt+Person
# e.g. zaaga'am+VAI+Imp+Del+2Sg
# Also: capitalizes the POS entry
# Also: removes the /-/ from the stem entry
def format_entry(entry_as_dict):
    entry_as_dict["Stem"] = (entry_as_dict["Stem"].replace("/", "")).replace("-", "")
    lexical_info = entry_as_dict["Stem"]

    if entry_as_dict["POS"] == "vai + o":
        entry_as_dict["POS"] = "vaio"
    entry_as_dict["POS"] = entry_as_dict["POS"].upper()
    # Dictionary uses VTI/VTI2/VTI3/VTI4 as POS, but we want to convert all of those to just VTI
    # However, this info lets us easily determine class
    # So we will assign class *first* before we lose those labels, then lose them!
    entry_as_dict = add_class(entry_as_dict)
    if "VTI" in entry_as_dict["POS"]:
        entry_as_dict["POS"] = "VTI"

    lexical_info += "+" + entry_as_dict["POS"]

    lexical_info += "+" + "Ind"

    lexical_info += "+" + "Pos"

    entry_as_dict = add_person_and_number(entry_as_dict)
    if "PersonNum" in entry_as_dict.keys():
        lexical_info += "+" + entry_as_dict["PersonNum"]

    lexical_info += ": "

    lexical_info += entry_as_dict["Inflectional Form"]

    entry_as_dict.update({"lexical_info": lexical_info})

    return entry_as_dict

# Add an entry to the dict that indicates the class of the stem (e.g. n, am, etc.)
def add_class(form_with_info):
    pos = form_with_info["POS"]
    stem = form_with_info["Stem"]
    # For some POS, like VAIO, we don't want the class in the file name at all
    if pos == "VTA":
        if stem.endswith("aw"):
            form_with_info.update({"Class": "aw"})
        elif stem.endswith("w") and not stem[-2] in vowels:
            form_with_info.update({"Class": "Cw"})
        elif stem.endswith("N"):
            form_with_info.update({"Class": "n"})
        elif not stem[-1] in vowels and not stem[-1] == "s" and not stem[-1] == "n":
            form_with_info.update({"Class": "C"})
        # Remaining classes: s, irr
    elif pos == "VAI":
        if stem.endswith("n"):
            form_with_info.update({"Class": "n"})
        elif stem [-1] in vowels and stem[-2] in vowels:
            form_with_info.update({"Class": "VV"})
        elif stem[-1] in vowels:
            form_with_info.update({"Class": "V"})
        # Remaining classes: am, m, rcp, rfx
    elif pos == "VII":
        if stem.endswith("d"):
            form_with_info.update({"Class": "d"})
        elif stem.endswith("n"):
            form_with_info.update({"Class": "n"})
        elif stem [-1] in vowels and stem[-2] in vowels:
            form_with_info.update({"Class": "VV"})
        elif stem [-1] in vowels:
            form_with_info.update({"Class": "V"})
        # Remaining classes: none!
    if "VTI" in pos:
        if pos == "VTI":
            form_with_info.update({"Class": "am"})
        elif pos == "VTI2":
            form_with_info.update({"Class": "oo"})
        # Remaining classes: aa, i

    # Make sure we assigned a class where needed
    if pos in POS_WITH_CLASS_IN_FILE_NAME:
        assert "Class" in form_with_info.keys(), f"\nYou need to assign a class (e.g. info about the final characters in the stem) to a form with this stem: {form_with_info['Stem']}. (POS: {pos})"

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
        form_with_info.update({"Subject": gloss_subj_dict[participant]})
    else:
        form_with_info.update({"Subject": "?"}) # So we take note of info we can't currently handle
    # If there's a second participant (i.e. it's transitive), add their info too
    if len(gloss) == 3 and (not gloss[1] == "augmented") and (not gloss[1] == "independent"):
        participant = gloss[1]
        if participant in gloss_obj_dict.keys():
            form_with_info.update({"Object": gloss_obj_dict[participant]})
        else:
            form_with_info.update({"Object": "?"})

    return form_with_info

# Reminder: forms_with_info is a list of dicts
def write_new_csv(forms_with_info, output_dir):
    CSV_HEADER = "Paradigm,Order,Class,Lemma,Stem,Subject,Object,Mode,Negation,Form1Surface,Form1Split,Form1Source"

    with open(output_dir + 'inflectional_forms_for_yaml.csv', "w+") as csv:
        csv.write(CSV_HEADER + "\n")
        for form_with_info in forms_with_info:
            print(form_with_info)
            csv.write(form_with_info["POS"] + ",") # Paradigm
            csv.write("Ind" + ",") # Order
            if "Class" in form_with_info.keys(): # Class
                csv.write(form_with_info["POS"] + "_" + form_with_info["Class"] + ",")
            else:
                csv.write(form_with_info["POS"] + ",")
            csv.write(form_with_info["Lemma"] + ",") # Lemma
            csv.write(form_with_info["Stem"] + ",") # Stem
            csv.write(form_with_info["Subject"] + ",") # Subject
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
