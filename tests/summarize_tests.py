"""A script for summarizing results of morphological analysis tests on YAML forms."""

import argparse
import os
from re import findall, search
from datetime import date
import pandas as pd

# Determined by command line args
OUTPUT_DIR = ""
OUTPUT_FILE_IDENTIFIER = ""
# Determined by the paradigm map file
TEST_SECTIONS = []
# Change these booleans as desired!
DO_PRINT_FORMS_WITH_NO_RESULTS = False
DO_PRINT_FORMS_WITH_ONLY_UNEXPECTED_RESULTS = False
# "noun" and "verb" will be added to the start of these names9/9++9
FORMS_WITH_NO_RESULTS_FILE_NAME = "forms_with_no_results.csv"
FORMS_WITH_ONLY_UNEXPECTED_RESULTS_FILE_NAME = "forms_with_only_unexpected_results.csv"

def get_test_sections_from_paradigm_map(paradigm_map_file):
    test_sections = set()
    paradigm_map = pd.read_csv(paradigm_map_file)
    for i, row in paradigm_map.iterrows():
        test_sections.add(row["Class"])

    test_sections = sorted(list(test_sections))
    return test_sections

def write_to_csv(output_line, summary_output_file_path):
    HEADER_1 = "Date,"
    HEADER_2 = ","
    summary_sections = ["Total"]
    summary_sections.extend(TEST_SECTIONS)
    for section in summary_sections:
        HEADER_1 += section + ","
        HEADER_1 += ",,,"
        HEADER_2 += "Precision,Recall,Forms,Forms Without Results,"

    if not os.path.isfile(summary_output_file_path):
            with open(summary_output_file_path, "w+") as csv_file:
                print(HEADER_1, file = csv_file)
                print(HEADER_2, file = csv_file)
    with open(summary_output_file_path, "a") as csv_file:
            csv_file.write(output_line + "\n")
    
    print("Wrote to", summary_output_file_path)

def get_prev_output_line(summary_output_file_path):
    prev_output_line = ""
    if os.path.isfile(summary_output_file_path):
        with open(summary_output_file_path, "r") as csv_file:
            lines = csv_file.readlines()
            if len(lines) >= 2: # At least one header and content line
                prev_output_line = lines[-1].strip()

    return prev_output_line

def prepare_output(results):
    output_line = ""
    total_true_pos = 0
    total_false_pos = 0
    total_false_neg = 0
    total_forms = 0
    total_forms_with_no_results = 0
    total_percent_forms_with_no_results = 0
    for test_section in TEST_SECTIONS:
        # If we don't have an expected section (maybe due to some recent reorganizing), you can just say 0/0 failures
        if not (test_section in results.keys()):
            output_line += "N/A,N/A,N/A,N/A,"
        else:
            precision = get_precision(results[test_section]["true_pos"], results[test_section]["false_pos"])
            recall = get_recall(results[test_section]["true_pos"], results[test_section]["false_neg"])
            assert(results[test_section]["number_of_forms"] > 0)
            percent_of_forms_with_no_results = round((results[test_section]["number_of_forms_with_no_results"] / results[test_section]["number_of_forms"]) * 100, 2)
            # Add the results from this test section to our output line
            output_line += str(precision) + "%,"
            output_line += str(recall) + "%,"
            output_line += str(results[test_section]["number_of_forms"]) + ","
            output_line += str(results[test_section]["number_of_forms_with_no_results"])
            output_line += " (" + str(percent_of_forms_with_no_results)+ "%),"
            # Add to our counts
            total_forms += results[test_section]["number_of_forms"]
            total_forms_with_no_results += results[test_section]["number_of_forms_with_no_results"]
            total_true_pos += results[test_section]["true_pos"]
            total_false_pos += results[test_section]["false_pos"]
            total_false_neg += results[test_section]["false_neg"]
    
    # Some summary info
    total_precision = get_precision(total_true_pos, total_false_pos)
    total_recall = get_recall(total_true_pos, total_false_neg)
    total_percent_forms_with_no_results = (round((total_forms_with_no_results / total_forms) * 100, 2) if total_forms > 0 else 0)
    # Put the summary info at the *start* of the output line
    total_output = str(total_precision) + "%," + str(total_recall) + "%," + str(total_forms) + "," + str(total_forms_with_no_results) + " (" + str(total_percent_forms_with_no_results) + "%),"
    output_line = total_output + output_line

    # First column is the date!
    output_line = str(date.today()) + ","  + output_line

    return output_line

def read_logs(input_file_name, yaml_source_csv_dir, for_nouns):
    results = {}
    forms_with_no_results = []
    forms_with_only_unexpected_results = []
    any_passes = False
    file = open(input_file_name, "r")
    lines = file.readlines()
    test_section = ""
    for index, line in enumerate(lines):
        # First, a little check so we know if --hide-passes is on
        if not(any_passes) and "[PASS]" in line:
            any_passes = True

        # Get the name of the current test section
        if line.startswith("YAML test file"):
            test_section = line.strip()
            test_section = test_section[test_section.rindex("/") + 1:]
            test_section = test_section.replace(".yaml", "")
            false_pos = 0
            false_neg = 0
            number_of_forms = 0
            number_of_forms_with_no_results = 0

        # "Missing" = an analysis in the YAML that the FST failed to produce
        elif "Missing results" in line:
            false_neg += (1 + line.count(","))

        # "Unexpected" = an analysis produced by the FST not found in the YAML
        elif search(r"Unexpected results: [A-Za-z]", line):
            false_pos += (1 + line.count(","))
            # Is this a form with NO passes?
            # If yes -> prev line will be "missing results", prev prev line will be unrelated
            # If no (has passes) -> either prev or prev prev line will be passes
            test_id = line.partition("[FAIL]")[0]
            if not (lines[index - 1].startswith(test_id) and "[PASS]" in lines[index - 1]):
                if not (lines[index - 2].startswith(test_id) and "[PASS]" in lines[index - 2]):
                        form_start = line.index("[FAIL] ") + len("[FAIL] ")
                        form_end = line.index(" =>") - 1
                        forms_with_only_unexpected_results.append({"form": line[form_start:form_end + 1].strip(), "pos": test_section})

        # Some FST analyses are "Unexpected" because they're empty!
        elif search(r"Unexpected results: \+\?", line):
            number_of_forms_with_no_results += 1
            form_start = line.index("[FAIL] ") + len("[FAIL] ")
            form_end = line.index(" =>") - 1
            forms_with_no_results.append({"form": line[form_start:form_end + 1].strip(), "pos": test_section})

        elif line.startswith("Unique"): # A final line with summary info
            number_of_forms = int(((line.partition("Unique inflected forms being tested: "))[2]).partition(",")[0])
            number_of_form_analysis_pairs = int(line.partition("Inflected form + analysis pairs being tested: ")[2])

        # The final line summarative for this section -- get the # of passes (true pos), and calculate summary stats
        elif line.startswith("Total"):
            # There's a pass for every correctly predicted analysis = true positives
            # The # of passes is the first number in this line
            true_pos = int((findall(r"[0-9]+", line))[0])

            test_section_results = {"true_pos": true_pos, "false_pos": false_pos, "false_neg": false_neg, "number_of_forms": number_of_forms, "number_of_form_analysis_pairs": number_of_form_analysis_pairs, "number_of_forms_with_no_results": number_of_forms_with_no_results}
            results.update({test_section: test_section_results})

    if DO_PRINT_FORMS_WITH_NO_RESULTS:
        if yaml_source_csv_dir:
            print_form_sublist_as_csv(forms_with_no_results, yaml_source_csv_dir, FORMS_WITH_NO_RESULTS_FILE_NAME, for_nouns)
        else:
            print("\nCannot print forms with *no results*.  No language data CSV path given, which is used to get additional information about these forms.")

    if DO_PRINT_FORMS_WITH_ONLY_UNEXPECTED_RESULTS:
        if yaml_source_csv_dir:
            if any_passes:
                print_form_sublist_as_csv(forms_with_only_unexpected_results, yaml_source_csv_dir, FORMS_WITH_ONLY_UNEXPECTED_RESULTS_FILE_NAME, for_nouns)
            else:
                print(f"\nRequested print of forms with *only unexpected results*, but the log file does not contain *passes*, which are necessary to determine these forms.  Please generate the log file again, making sure --hide-passes is NOT specified.\nHint: this probably means going into the Makefile, finding where your .log file is generated (i.e., a call to run_yaml_tests.py), and removing the --hide-passes flag.")
        else:
            print("\nCannot print forms with *only unexpected results*.  No language data CSV path given, which is used to get additional information about these forms.")

    file.close()
    assert len(results) > 0, "\nERROR: The log file didn't have any test results to read!"
    return results

# Print a subset of the reformatted scrape CSV, with only rows for certain forms
def print_form_sublist_as_csv(form_list, yaml_source_csv_dir, output_file_basic_name, for_nouns):
    # Need to remove the nouns or verbs
    updated_form_list = []
    for form in form_list:
        if (not(for_nouns) and form["pos"].startswith("V")) or (for_nouns and form["pos"].startswith("N")):
            updated_form_list.append(form)

    if len(updated_form_list) > 0:
        lexical_data = None
        forms_written = 0
        # Read in the CSV(s) of forms used to generate the YAML to get more info about this form
        for file_name in os.listdir(yaml_source_csv_dir):
            full_file_name = os.path.join(yaml_source_csv_dir, file_name)
            if full_file_name.endswith(".csv"):
                csv_data = pd.read_csv(full_file_name, keep_default_na = False)
                if type(lexical_data) == pd.core.frame.DataFrame:
                    lexical_data = pd.concat([lexical_data, csv_data])
                else:
                    lexical_data = csv_data
        # Now we have one dataframe with all the data from the CSV(s)

        lexical_data = lexical_data.sort_values(by='Class', ignore_index=True) # To accelerate the search process
        # Determine how many "surface forms" there are per row
        form_columns = [column for column in list(lexical_data) if column.endswith("Surface") ]
        paradigm_indices = {}
        new_csv = pd.DataFrame() # To print (the subset of the scrape)

        print("Number of forms to write:", len(updated_form_list))
        # Go through each of the forms we flagged as wanting to print
        for i, form in enumerate(updated_form_list):
            update_increment = 100
            if i % update_increment == 0:
                if i + update_increment < len(updated_form_list):
                    print(f"Writing forms {i + 1}-{i + update_increment}...")
                else:
                    print(f"Writing forms {i + 1}-{len(updated_form_list)}...")
            # Check if we know the starting point for this paradigm/pos yet
            if form["pos"] not in paradigm_indices.keys():
                index = lexical_data["Class"].searchsorted(form["pos"], side = 'left')
                paradigm_indices.update({form["pos"]: index})

            # Find the form we're looking for in the big spreadsheet
            inflectional_form = form["form"]
            search_starting_point = paradigm_indices[form["pos"]]
            for index, row in (lexical_data[search_starting_point:]).iterrows():
                row = row.to_dict()
                if inflectional_form in [row[form_column] for form_column in form_columns]:
                    # Add this column, so that in cases with *mulitple* surface forms,
                    # it's clear which is the form without results
                    row["FormWithoutResults"] = inflectional_form
                    new_csv = new_csv._append(row, ignore_index = True)
                    forms_written += 1
                    break # Stop looking when we've found it!

        # Print the results
        if for_nouns:
            output_file_path = OUTPUT_DIR + "/" + OUTPUT_FILE_IDENTIFIER + "_noun_" + output_file_basic_name
        else:
            output_file_path = OUTPUT_DIR + "/" + OUTPUT_FILE_IDENTIFIER + "_verb_" + output_file_basic_name
        new_csv.to_csv(output_file_path, index = False)
        print(f"\nWrote {forms_written} forms to {output_file_path}")

def get_precision(true_pos, false_pos):
    precision = 0
    if true_pos + false_pos > 0:
        precision = round((true_pos / (true_pos + false_pos)) * 100, 2)

    return precision

def get_recall(true_pos, false_neg):
    recall = 0
    if true_pos + false_neg > 0:
        recall = round((true_pos / (true_pos + false_neg)) * 100, 2)

    return recall

def print_summary_stats(results, for_nouns):
    total_form_analysis_pairs_tested = 0
    for section in results.keys():
        if section in TEST_SECTIONS:
            results_by_section = results[section]
            total_form_analysis_pairs_tested += results_by_section["number_of_form_analysis_pairs"]

    if for_nouns:
        test_label = "noun"
    else:
        test_label = "verb"
    print(f"\nThe {test_label} tests covered {total_form_analysis_pairs_tested} form-analysis pairs.")

def main():
    # Sets up argparse.
    parser = argparse.ArgumentParser(prog="summarize_tests")
    parser.add_argument("--input_file_name", type=str, help="The .log file that is being read in.")
    parser.add_argument("--yaml_source_csv_dir", type=str, help="The directory containing the .csv file(s) containing the language data which was used to generate the YAML files.  Optional; only used if you want to print out some extra information about the test data.")
    parser.add_argument("--paradigm_map_path", type=str, help="The .csv file from which the list of test sections are read (e.g., VAIPL_V, VAIPL_VV).")
    parser.add_argument("--output_dir", type=str, help="The directory where output files will be written.")
    parser.add_argument("--output_file_identifier", type=str, help="A keyword associated with this set of tests that will be included in the file names of all outputted CSVs. For example, use 'paradigm' to call your files 'paradigm_verb_test_summmary.csv' etc.")
    parser.add_argument("--for_nouns", action="store_true", help="If False, it's assumed to be for_verbs instead!")
    args = parser.parse_args()

    global OUTPUT_DIR
    global OUTPUT_FILE_IDENTIFIER
    global TEST_SECTIONS
    OUTPUT_DIR = args.output_dir
    OUTPUT_FILE_IDENTIFIER = args.output_file_identifier
    summary_output_file_path = OUTPUT_DIR + "/" + OUTPUT_FILE_IDENTIFIER
    if args.for_nouns:
        summary_output_file_path += "_noun_test_summary.csv"
    else:
        summary_output_file_path += "_verb_test_summary.csv"
    TEST_SECTIONS = get_test_sections_from_paradigm_map(args.paradigm_map_path)

    results = read_logs(args.input_file_name, args.yaml_source_csv_dir, args.for_nouns)
    output_line = prepare_output(results)
    prev_output_line = get_prev_output_line(summary_output_file_path)
    if prev_output_line == output_line:
        print(f"Did not write to CSV ({summary_output_file_path}) as there were no changes to the test results (or date!).")
    else:
        write_to_csv(output_line, summary_output_file_path)
    print_summary_stats(results, args.for_nouns)

if __name__ == "__main__":
    main()