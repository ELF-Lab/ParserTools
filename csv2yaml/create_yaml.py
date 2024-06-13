# The purpose of this script is to convert Ojibwe verb paradigm spreadsheets to yaml files to test an Ojibwe morphological parser
# Final script created by Scott Parkill (CultureFoundry) and Christopher Hammerly (University of British Columbia)
# Initial script that served as inspiration created by Miikka Silfverberg (University of British Columbia) and Hammerly 
# Original Version: January 30, 2023

#!/bin/env python3

import argparse
from json import load
import os
import pandas as pd
import shutil

# Assume that there are maximally five parallel forms on any given CSV
# row
MAX_FORMS=10

# Run just `python3 create_yaml.py` to view help.

def remove_NA_or_empty(value):
    has_a_value = True
    if value == "" or value == "NONE" or value == "NA":
        has_a_value = False

    return has_a_value

def create_output_directory(output_directory:str) -> str:
    # Clear any existing yaml output files
    if os.path.isdir(output_directory):
        shutil.rmtree(output_directory)

    # Create the directory for the yaml output if it doesn't exist already.
    try:
        os.mkdir(f'{output_directory}')
    except FileExistsError:
        pass

    return output_directory

def make_yaml(file_name:str, output_directory:str, analysis:callable, non_core_tags:str, regular_yaml_line_count:int, core_yaml_line_count:int) -> None:
    '''Create a yaml file for the given spreadsheet under the given analysis function.'''

    output_line_count = 0
    # na_filter prevents the reading of "NA" values (= not applicable) as NaN
    df = pd.read_csv(file_name, keep_default_na=False)

    # This dictionary will have keys that are stems and values that are lists of tuples of (tag, form).
    # Example: 'aa': [(tag1, form1), (tag2, form2)].
    yaml_dict = {}

    for _, row in df.iterrows():
        row = row.to_dict()

        # This will skip empty lines, which are read as floats and not strings by pandas.
        if type(row["Form1Split"]) is float:
            continue

        # If the given stem is not in our dictionary yet, add it.
        if row["Class"] not in yaml_dict:
            yaml_dict[row["Class"]] = []

        # An analysis can have 0, 1, or multiple forms, because some forms are missing
        # We want to output
        #   - "[]" for 0 forms
        #   - "form" for 1 form
        #   - "[form1, form2, ...]" for multiple forms

        # Get all forms
        forms = []
        for i in range(1, MAX_FORMS + 1):
            if f'Form{i}Surface' in row.keys() and row[f'Form{i}Surface']:
                forms.append(row[f'Form{i}Surface'])
            elif i == 1 and 'Form1' in row.keys():
                forms.append(row['Form1'])
            else:
                break

        # Remove missing forms
        if "MISSING" in forms:
            forms.remove("MISSING")

        # Determine how to print the forms
        if len(forms) == 0:
            forms_output = "[]"
        elif len(forms) == 1:
            forms_output = forms[0]
        else:
            forms_output = "[" + ",".join(forms) + "]"

        # Add this row to the dictionary appropriately.
        yaml_dict[row["Class"]].append(("     " + analysis(row), forms_output))

    # Convert tag1,tag2,... -> {tag1, tag2, ...}
    non_core_tags = set(non_core_tags.split(",")) if non_core_tags != "" else set()

    # For each stem in the dictionary, write it to its own yaml file.
    for key, value in yaml_dict.items():
        output_file_name = os.path.join(output_directory,f"{key}.yaml")
        core_output_file_name = os.path.join(output_directory,f"{key}-core.yaml")
        # If the file doesn't exist, initialize it and write the forms
        header = """Config:
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
        if not os.path.isfile(output_file_name):
            with open(output_file_name, "w+") as yaml_file, \
                 open(core_output_file_name, "w+") as core_yaml_file:
                print(header, file = yaml_file)
                print(header, file = core_yaml_file)
        with open(output_file_name, "a") as yaml_file, \
             open(core_output_file_name, "a") as core_yaml_file:
            for tag, forms in value:
                yaml_file.write(f"{tag}: {forms}\n")
                output_line_count += 1
                regular_yaml_line_count += 1
                if len(non_core_tags.intersection(tag.split("+"))) != 0:
                    continue
                core_yaml_file.write(f"{tag}: {forms}\n")
                core_yaml_line_count += 1

        print(f"Wrote {output_line_count} lines to {output_file_name}")
        output_line_count = 0

    return regular_yaml_line_count, core_yaml_line_count

def generate_analysis(json_file):
    config = load(open(json_file))
    tags = ["Lemma"]
    tags.extend(config["morph_features"])

    # Using filter with remove_NA to make sure "not applicable" values do not end up in the analysis
    analysis = lambda row: "+".join(list(filter(remove_NA_or_empty,[row[x] for x in tags])))
    return analysis

if __name__ == '__main__':
    # Sets up argparse.
    parser = argparse.ArgumentParser(prog="create_yaml")
    parser.add_argument("csv_directory", type=str, help="Path to the directory containing the spreadsheet(s).")
    parser.add_argument("morphological_tag_file", type=str, help="Path to the JSON file containing \"morph_features\", specifying the order of tags for this POS.")
    parser.add_argument("output_parent_directory", type=str, help="Path to the folder where the yaml files will be saved (inside their own subdirectory).")
    parser.add_argument("--non-core-tags", dest="non_core_tags", action="store",default="",help="If one of these tags occurs in the analysis, the form will not be included in core yaml tests. Example: \"Prt,Dub,PrtDub\"")
    parser.add_argument("--pos", dest="pos", action="store", default="verb", help="Which POS are we generating tests for (noun or verb).")
    args = parser.parse_args()
    output_directory = create_output_directory(args.output_parent_directory + "yaml_output/")

    files_generated = False

    analysis = generate_analysis(args.morphological_tag_file)

    regular_yaml_line_count = 0
    core_yaml_line_count = 0
    for file_name in os.listdir(args.csv_directory):
        full_name = os.path.join(args.csv_directory, file_name)
        if full_name.endswith(".csv") and args.pos == "verb":
            regular_yaml_line_count, core_yaml_line_count = make_yaml(full_name, output_directory, analysis, args.non_core_tags, regular_yaml_line_count, core_yaml_line_count)
            files_generated = True # At least one, anyways
        if full_name.endswith(".csv") and args.pos == "noun":
            regular_yaml_line_count, core_yaml_line_count = make_yaml(full_name, output_directory, analysis, args.non_core_tags, regular_yaml_line_count, core_yaml_line_count)
            files_generated = True # At least one, anyways

    if files_generated:
        print("\nSuccessfully generated yaml files.")
        print("Total lines printed to normal yaml files: ", regular_yaml_line_count)
        print("Total lines printed to core yaml files:", core_yaml_line_count)
