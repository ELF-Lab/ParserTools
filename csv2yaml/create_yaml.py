# The purpose of this script is to convert Ojibwe verb paradigm spreadsheets to yaml files to test an Ojibwe morphological parser
# Final script created by Scott Parkill (CultureFoundry) and Christopher Hammerly (University of British Columbia)
# Initial script that served as inspiration created by Miikka Silfverberg (University of British Columbia) and Hammerly 
# Original Version: January 30, 2023

#!/bin/env python3

import argparse
import os
import pandas as pd
import shutil

# Run just `python3 create_yaml.py` to view help.

# Using filter with remove_NA to make sure "not applicable" values do not end up in the analysis
analysis = lambda row: "+".join(list(filter(remove_NA, [row["Lemma"], row["Paradigm"], row["Order"], row["Negation"], row["Mode"], row["Subject"], row["Object"]])))

def remove_NA(value):
    has_a_value = True
    if value == "NA":
        has_a_value = False

    return has_a_value

def create_output_directory(parent_directory:str) -> str:
    output_directory = f'{parent_directory}yaml_output/'
    # Clear any existing yaml output files
    if os.path.isdir(output_directory):
        shutil.rmtree(output_directory)

    # Create the directory for the yaml output if it doesn't exist already.
    try:
        os.mkdir(f'{output_directory}')
    except FileExistsError:
        pass

    return output_directory

def make_yaml(file_name:str, output_directory:str, analysis:callable) -> None:
    '''Create a yaml file for the given spreadsheet under the given analysis function.'''

    # na_filter prevents the reading of "NA" values (= not applicable) as NaN
    df = pd.read_csv(file_name, na_filter = False)

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

        if 'Form1Surface' in row.keys():
            forms = f"{row['Form1Surface']}"
        else:
            forms = f"{row['Form1']}"

        # Check if there is a second form, and add it to the form list if so
        if 'Form2Surface' in row.keys() and (row["Form2Surface"]):
            forms = f"[{forms},{row['Form2Surface']}]"

        # Add this row to the dictionary appropriately.
        yaml_dict[row["Class"]].append(("     "+analysis(row), forms))

    # For each stem in the dictionary, write it to its own yaml file.
    for key, value in yaml_dict.items():
        output_file_name = f"{output_directory}{key}.yaml"
        # If the file doesn't exist, initialize it and write the forms
        if not os.path.isfile(output_file_name):
            with open(output_file_name, "w+") as yaml_file:
                print("""Config:
  hfst:
    Gen: ../../../src/generator-gt-norm.hfst
    Morph: ../../../src/analyser-gt-norm.hfst
  xerox:
    Gen: ../../../src/generator-gt-norm.xfst
    Morph: ../../../src/analyser-gt-norm.xfst
    App: lookup
     
Tests:

  Lemma - ALL :
""", file = yaml_file)
                for tag, forms in value:
                    yaml_file.write(f"{tag}: {forms}\n")
        # If the file already exists, just append these new forms
        else:
            with open(output_file_name, "a") as yaml_file:
                for tag, forms in value:
                    yaml_file.write(f"{tag}: {forms}\n")


if __name__ == '__main__':
    # Sets up argparse.
    parser = argparse.ArgumentParser(prog="create_yaml")
    parser.add_argument("csv_directory", type=str, help="Path to the spreadsheet.")
    parser.add_argument("output_parent_directory", type=str, help="Path to the folder where the yaml files will be saved (inside their own subdirectory).")

    args = parser.parse_args()

    output_directory = create_output_directory(args.output_parent_directory)

    files_generated = False

    for file_name in os.listdir(args.csv_directory):
        full_name = args.csv_directory + file_name
        if full_name.endswith(".csv"):
            make_yaml(full_name, output_directory, analysis)
            files_generated = True # At least one, anyways

    if files_generated:
        print('Successfully generated yaml files.')
