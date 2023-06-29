# The purpose of this script is to convert Ojibwe verb paradigm spreadsheets to yaml files to test an Ojibwe morphological parser
# Final script created by Scott Parkill (CultureFoundry) and Christopher Hammerly (University of British Columbia)
# Initial script that served as inspiration created by Miikka Silfverberg (University of British Columbia) and Hammerly 
# Original Version: January 30, 2023

#!/bin/env python3

import argparse
import os
import pandas as pd

# To use this file, as an example do `python3 create_yaml.py /home/user/Documents/vii.xlsx --vii`.
# Run just `python3 create_yaml.py` to view help.

## READ ME ##
# To maintain this file, add a new analysis for each type (e.g. VTA).
# Then, add another entry to the `group` variable below (like that on approx. line 68).
# Lastly, add another `if` check that for that verb type (like than on approx. line 74).



VII_analysis = lambda row: "+".join([row["Lemma"], row["Paradigm"], row["Order"], row["Negation"], row["Mode"], row["Subject"].replace(" ","")])
VAI_analysis = lambda row: "+".join([row["Lemma"], row["Paradigm"], row["Order"], row["Negation"], row["Mode"], row["Subject"].replace(" ","")])
VTI_analysis = lambda row: "+".join([row["Lemma"], row["Paradigm"], row["Order"], row["Negation"], row["Mode"], row["Subject"], row["Object"].replace(" ","")])
VTA_analysis = lambda row: "+".join([row["Lemma"], row["Paradigm"], row["Order"], row["Negation"], row["Mode"], row["Subject"], row["Object"].replace(" ","")])


def make_yaml(file_name:str, analysis:callable) -> None:
    '''Create a yaml file for the given spreadsheet under the given analysis function.'''

    output_path = f'{os.path.dirname(file_name)}/yaml_output/'

    # Create the directory for the yaml output if it doesn't exist already.
    try:
        os.mkdir(f'{output_path}')
    except FileExistsError:
        pass

    # Read the entire spreadsheet in order to get all the sheets in that spreadsheet.
    xls = pd.ExcelFile(file_name)

    # Loop over each sheet.
    for sheet in xls.sheet_names:
        df = pd.read_excel(file_name, sheet_name=sheet)

        # This dictionary will have keys that are stems and values that are lists of tuples of (tag, form).
        # Example: 'aa': [(tag1, form1), (tag2, form2)].
        yaml_dict = {}

        for _, row in df.iterrows():
            row = row.to_dict()

            # This will skip empty lines, which are read as floats and not strings by pandas.
            if type(row["Form1"]) is float:
                continue

            # If the given stem is not in our dictionary yet, add it.
            if row["Class"] not in yaml_dict:
                yaml_dict[row["Class"]] = []

            # Check if there is a second form. If there is, create the form in the expected format.
            if type(row["Form2"]) is not float:
                forms = f"[{row['Form1']},{row['Form2']}]"
            else:
                forms = f"{row['Form1']}"

            # Add this row to the dictionary appropriately.
            yaml_dict[row["Class"]].append(("     "+analysis(row), forms))

        # For each stem in the dictionary, write it to its own yaml file.
        for key, value in yaml_dict.items():
            with open(f"{output_path}{sheet}_{key}.yaml", "w+") as yaml_file:
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

    print('Successfully generated yaml files.')

if __name__ == '__main__':
    # Sets up argparse.
    parser = argparse.ArgumentParser(prog="create_yaml")
    parser.add_argument("xlsx_path", type=str, help="Path to the spreadsheet.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--vii', action='store_true', help="Do analysis for VII verbs.")
    group.add_argument('--vai', action='store_true', help="Do analysis for VAI verbs.")
    group.add_argument('--vti', action='store_true', help="Do analysis for VTI verbs.")
    group.add_argument('--vta', action='store_true', help="Do analysis for VTA verbs.")
    # Example to add VTA:
    #group.add_argument('--vta', action='store_true', help='Do analysis for VTA verbs.')

    args = parser.parse_args()

    if args.vii:
        analysis = VII_analysis
    elif args.vai:
        analysis = VAI_analysis
    elif args.vti:
        analysis = VTI_analysis
    elif args.vta:
        analysis = VTA_analysis

    make_yaml(args.xlsx_path, analysis)
