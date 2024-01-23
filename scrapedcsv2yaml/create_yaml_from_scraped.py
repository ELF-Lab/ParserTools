import argparse
import pandas as pd
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '../csv2yaml'))
from create_yaml import create_output_directory

POS_TO_KEEP = ["vai + o", "vta", "vai", "vii", "vti", "vti2", "vti3", "vti4"]
POS_WITH_CLASS_IN_FILE_NAME = ["VAI", "VTA", "VII", "VTI"]
YAML_HEADER = """Config:
  hfst:
    Gen: ../../../src/generator-gt-norm.hfst
    Morph: ../../../src/analyser-gt-norm.hfst
  xerox:
    Gen: ../../../src/generator-gt-norm.xfst
    Morph: ../../../src/analyser-gt-norm.xfst
    App: lookup
     
Tests:

  Lemma - ALL :
"""
YAML_INDENT = "     "
vowels = ["i", "e", "o", "a"]

def process_csv(file_name):
    df = pd.read_csv(file_name)#, na_filter = False)

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
        print(form_with_info)
        assert "Class" in form_with_info.keys(), f"\nYou need to assign a class (e.g. info about the final characters in the stem) to a form with this stem: {form_with_info['Stem']}. (POS: {pos})"

    return form_with_info

def write_yaml(forms_with_info, output_directory):
    # Every time we run the code, any existing YAML files will be deleted.
    # So we must be creating the files anew every run.
    # But then we are printing the forms out of order, so we need to
    # create each file once, and after that (i.e. once the file exists)
    # we just want to add new rows to it.

    # For each stem in the dictionary, write it to its own yaml file.
    for form_with_info in forms_with_info:
        print("")
        print(form_with_info)
        output_file_name = f"{output_directory}/{determine_output_file(form_with_info)}"
        # If the file doesn't exist, initialize it and write the forms
        if not os.path.isfile(output_file_name):
            with open(output_file_name, "w+") as yaml_file:
                print(YAML_HEADER, file = yaml_file)
                yaml_file.write(YAML_INDENT + f"{form_with_info['lexical_info']}\n")
        # If the file already exists, just append these new forms
        else:
            with open(output_file_name, "a") as yaml_file:
                yaml_file.write(YAML_INDENT + f"{form_with_info['lexical_info']}\n")

def determine_output_file(form_with_info):
    output_file = form_with_info["POS"]
    if form_with_info["POS"] in POS_WITH_CLASS_IN_FILE_NAME:
        assert("Class" in form_with_info.keys())
        output_file += "_" + form_with_info["Class"]
    output_file += ".yaml"

    return output_file


def main():
    # Sets up argparse.
    parser = argparse.ArgumentParser(prog="create_if_yaml")
    parser.add_argument("if_csv_path", type=str, help="Path to the spreadsheet.")
    parser.add_argument("output_parent_directory", type=str, help="Path to the folder where the yaml files will be saved (inside their own subdirectory).")
    args = parser.parse_args()

    forms_with_info = process_csv(args.if_csv_path)

    output_dir = create_output_directory(args.output_parent_directory)
    write_yaml(forms_with_info, output_dir)

    print(args.if_csv_path, args.output_parent_directory)

if __name__ == '__main__':
    main()