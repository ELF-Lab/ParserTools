#!/bin/env python3

import argparse
from json import load
import os
import pandas as pd
import shutil

# Run just `python3 create_yaml.py` to view help.
# Assume that there are maximally five parallel forms on any given CSV row
MAX_FORMS=5
EMPTY_FIELD_MARKER = "NONE"
HEADER = """Config:
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

def remove_empty(value):
    has_a_value = True
    if value == "" or value == EMPTY_FIELD_MARKER:
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

    # For each word class in the dictionary, create its own YAML file.
    for klass, analysis_and_forms_list in yaml_dict.items():
        regular_output_file_name = os.path.join(output_directory,f"{klass}.yaml")
        core_output_file_name = os.path.join(output_directory,f"{klass}-core.yaml")
        regular_yaml_line_count, core_yaml_line_count = write_to_file(analysis_and_forms_list, regular_output_file_name, regular_yaml_line_count, core_output_file_name, core_yaml_line_count, non_core_tags)

    return regular_yaml_line_count, core_yaml_line_count


def write_to_file(analysis_and_forms_list, regular_output_file_name, total_regular_yaml_line_count, core_output_file_name, total_core_yaml_line_count, non_core_tags):
    current_regular_yaml_line_count = 0
    current_core_yaml_line_count = 0

    # If the file doesn't exist, initialize it
    if not os.path.isfile(regular_output_file_name):
        with open(regular_output_file_name, "w+") as yaml_file:
            print(HEADER, file = yaml_file)
        # Don't bother with the "core" files if there's no tags given
        if non_core_tags:
            with open(core_output_file_name, "w+") as core_yaml_file:
                print(HEADER, file = core_yaml_file)
    # Write the forms
    for analysis, forms in analysis_and_forms_list:
        with open(regular_output_file_name, "a") as yaml_file:
            yaml_file.write(f"{analysis}: {forms}\n")
            current_regular_yaml_line_count += 1
            # Don't bother with the "core" files if there's no tags given
            # If there are, check if we should write to the core file now
            if non_core_tags and len(non_core_tags.intersection(analysis.split("+"))) == 0:
                with open(core_output_file_name, "a") as core_yaml_file:
                    core_yaml_file.write(f"{analysis}: {forms}\n")
                    current_core_yaml_line_count += 1

    print(f"Wrote {current_regular_yaml_line_count} lines to {regular_output_file_name}")
    if non_core_tags:
        print(f"Wrote {current_core_yaml_line_count} lines to {core_output_file_name}")

    total_regular_yaml_line_count += current_regular_yaml_line_count
    total_core_yaml_line_count += current_core_yaml_line_count

    return total_regular_yaml_line_count, total_core_yaml_line_count

def generate_analysis(json_file):
    config = load(open(json_file))
    tags = ["Lemma"]
    tags.extend(config["morph_features"])

    # Using filter with remove_NA to make sure "not applicable" values do not end up in the analysis
    analysis = lambda row: "+".join(list(filter(remove_empty,[row[x] for x in tags])))
    return analysis

if __name__ == '__main__':
    # Sets up argparse.
    parser = argparse.ArgumentParser(prog="create_yaml")
    parser.add_argument("csv_directory", type=str, help="Path to the directory containing the spreadsheet(s).")
    parser.add_argument("morphological_tag_file", type=str, help="Path to the JSON file containing \"morph_features\", specifying the order of tags for this POS.")
    parser.add_argument("output_parent_directory", type=str, help="Path to the folder where the yaml files will be saved (inside their own subdirectory).")
    parser.add_argument("--non-core-tags", dest="non_core_tags", action="store",default="",help="If one of these tags occurs in the analysis, the form will not be included in core yaml tests. Example: \"Prt,Dub,PrtDub\".  If no non-core-tags are specified, no core files are written, as they would be identical to the regular YAML files.")
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
