import argparse
import pandas as pd
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '../csv2yaml'))
from create_yaml import create_output_directory

pos_to_keep = ["vai + o"]
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

def process_csv(file_name):
    df = pd.read_csv(file_name)#, na_filter = False)

    rows_of_strings = []

    df = df.truncate(before=505, after=506)
    print("")
    for index, row in df.iterrows():
        row = row.to_dict()
        if row["POS"] in pos_to_keep:
            lexical_info = format_entry(row)
            # print(row)
            # print(lexical_info)
            # print("")

            rows_of_strings.append(lexical_info)

    return rows_of_strings

# Convert each row to a string formatted as Stem+Class+Imp/Ind+Pos/Neg/N/A+Neu/Prt+Person
# e.g. zaaga'am+VAI+Imp+Del+2Sg
def format_entry(entry_as_dict):
    lexical_info = (entry_as_dict["Stem"].replace("/", "")).replace("-", "")
    
    if entry_as_dict["POS"] == "vai + o":
        entry_as_dict["POS"] = "vaio"
    lexical_info += "+" + entry_as_dict["POS"].upper()

    lexical_info += "+" + "Ind"

    lexical_info += "+" + "Pos"
    
    lexical_info += ": "

    lexical_info += entry_as_dict["Inflectional Form"]

    return lexical_info

def write_yaml(rows, output_directory):
    # Every time we run the code, any existing YAML files will be deleted.
    # So we must be creating the files anew every run.
    # But then we are printing the forms out of order, so we need to
    # create each file once, and after that (i.e. once the file exists)
    # we just want to add new rows to it.

    # For each stem in the dictionary, write it to its own yaml file.
    for row in rows:
        output_file_name = f"{output_directory}/VAIO.yaml"
        # If the file doesn't exist, initialize it and write the forms
        if not os.path.isfile(output_file_name):
            with open(output_file_name, "w+") as yaml_file:
                print(YAML_HEADER, file = yaml_file)
                yaml_file.write(YAML_INDENT + f"{row}\n")
        # If the file already exists, just append these new forms
        else:
            with open(output_file_name, "a") as yaml_file:
                print(row)
                yaml_file.write(YAML_INDENT + f"{row}\n")

def main():
    # Sets up argparse.
    parser = argparse.ArgumentParser(prog="create_if_yaml")
    parser.add_argument("if_csv_path", type=str, help="Path to the spreadsheet.")
    parser.add_argument("output_parent_directory", type=str, help="Path to the folder where the yaml files will be saved (inside their own subdirectory).")
    args = parser.parse_args()

    rows = process_csv(args.if_csv_path)

    output_dir = create_output_directory(args.output_parent_directory)
    write_yaml(rows, output_dir)

    print(args.if_csv_path, args.output_parent_directory)

if __name__ == '__main__':
    main()