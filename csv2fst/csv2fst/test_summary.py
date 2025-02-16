"""A script for summarizing results of morphological analysis tests on OPD forms."""

import argparse
import os
from re import findall, search
from datetime import date
import pandas as pd

OUTPUT_FILE_PATH = ""
NOUN_OUTPUT_FILE_NAME = "noun_test_summary.csv"
VERB_OUTPUT_FILE_NAME = "verb_test_summary.csv"
TEST_SECTIONS = []
DO_PRINT_FORMS_WITH_NO_RESULTS = False # If true, ensure the below path is correct for your system
DO_PRINT_FORMS_WITH_ONLY_UNEXPECTED_RESULTS = False # If true, ensure the below path is correct for your system
NOUN_PARADIGM_MAP_PATH = "~/OPDDatabase/assets/NOUNS_paradigm_map.csv"
VERB_PARADIGM_MAP_PATH = "~/OPDDatabase/assets/VERBS_paradigm_map.csv"
FORMS_WITH_NO_ANALYSES_FILE = "forms_with_no_analyses.csv"
FORMS_WITH_ONLY_UNEXPECTED_ANALYSES_FILE = "forms_with_only_unexpected_results.csv"

def get_test_sections_from_paradigm_map(paradigm_map_file):
    test_sections = set()
    paradigm_map = pd.read_csv(paradigm_map_file)
    for i, row in paradigm_map.iterrows():
        test_sections.add(row["Class"])

    test_sections = sorted(list(test_sections))
    return test_sections

def write_to_csv(output_line):
    HEADER_1 = "Date,"
    HEADER_2 = ","
    summary_sections = ["Total"]
    summary_sections.extend(TEST_SECTIONS)
    for section in summary_sections:
        HEADER_1 += section + ","
        HEADER_1 += ",,,"
        HEADER_2 += "Precision,Recall,Forms,Forms Without Results,"

    if not os.path.isfile(OUTPUT_FILE_PATH):
            with open(OUTPUT_FILE_PATH, "w+") as csv_file:
                print(HEADER_1, file = csv_file)
                print(HEADER_2, file = csv_file)
    with open(OUTPUT_FILE_PATH, "a") as csv_file:
            csv_file.write(output_line + "\n")
    
    print("Wrote to", OUTPUT_FILE_PATH)
    csv_file.close()

def get_prev_output_line():
    prev_output_line = ""
    if os.path.isfile(OUTPUT_FILE_PATH):
        with open(OUTPUT_FILE_PATH, "r") as csv_file:
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

def read_logs(input_file_name, scraped_csv_path, for_nouns):
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

        # "Missing" = an OPD analysis that the FST failed to produce
        elif "Missing results" in line:
            false_neg += (1 + line.count(","))

        # "Unexpected" = an analysis produced by the FST not shared by the OPD
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
        if for_nouns:
            output_file = "noun_" + FORMS_WITH_NO_ANALYSES_FILE
        else:
            output_file = "verb_" + FORMS_WITH_NO_ANALYSES_FILE
        print(f"\nWriting to {output_file}...")
        print_form_sublist_as_csv(forms_with_no_results, scraped_csv_path, output_file)

    if DO_PRINT_FORMS_WITH_ONLY_UNEXPECTED_RESULTS:
        if for_nouns:
            output_file = "noun_" + FORMS_WITH_ONLY_UNEXPECTED_ANALYSES_FILE
        else:
            output_file = "verb_" + FORMS_WITH_ONLY_UNEXPECTED_ANALYSES_FILE
        if any_passes:
            print(f"Writing to {output_file}...")
            print_form_sublist_as_csv(forms_with_only_unexpected_results, scraped_csv_path, output_file)
        else:
            print(f"\nRequested print of {output_file}, but the log file does not contain *passes*, which are necessary to determine these forms.  Please generate the log file again, making sure --hide-passes is NOT specified.\nHint: this probably means going into the Makefile, finding where your .log file is generated (i.e., a call to morph-test.py), and removing the --hide-passes flag.")

    assert len(results) > 0, "\nERROR: The log file didn't have any test results to read!"
    return results

# Print a subset of the reformatted scrape CSV, with only rows for certain forms
def print_form_sublist_as_csv(form_list, scraped_csv_path, output_file):
    if len(form_list) > 0:
        # Read in the spreadsheet of scraped forms to get more info about this form
        scraped_forms = pd.read_csv(scraped_csv_path, keep_default_na = False)
        scraped_forms = scraped_forms.sort_values(by='Class', ignore_index=True) # To accelerate the search process
        paradigm_indices = {}
        new_csv = pd.DataFrame() # To print (the subset of the scrape)

        print("Number of forms to write:", len(form_list))
        # Go through each of the forms we flagged as wanting to print
        for i, form in enumerate(form_list):
            update_increment = 100
            if i % update_increment == 0:
                if i + update_increment < len(form_list):
                    print(f"Writing forms {i}-{i + update_increment - 1}...")
                else:
                    print(f"Writing forms {i}-{len(form_list) - 1}...")
            # Check if we know the starting point for this paradigm/pos yet
            if form["pos"] not in paradigm_indices.keys():
                index = scraped_forms["Class"].searchsorted(form["pos"], side = 'left')
                paradigm_indices.update({form["pos"]: index})

            # Find the form we're looking for in the big spreadsheet
            inflectional_form = form["form"]
            search_starting_point = paradigm_indices[form["pos"]]
            for _, row in (scraped_forms[search_starting_point:]).iterrows():
                row = row.to_dict()
                if inflectional_form == row["Form1Surface"]:
                    new_csv = new_csv._append(row, ignore_index = True)
                    break # Stop looking when we've found it!

        # Print the results
        new_csv.to_csv(output_file, index = False)

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
    parser = argparse.ArgumentParser(prog="test_summary")
    parser.add_argument("--input_file_name", type=str, help="The .log file that is being read in.")
    parser.add_argument("--scraped_csv_path", type=str, help="The .csv file containing the language data.")
    parser.add_argument("--output_dir", type=str, help="The directory where output files will be written.")
    parser.add_argument("--for_nouns", action="store_true", help="If False, it's assumed to be for_verbs instead!")
    args = parser.parse_args()

    # Configure the summary for nouns OR verbs
    global TEST_SECTIONS
    global OUTPUT_FILE_PATH
    if args.for_nouns:
        TEST_SECTIONS = get_test_sections_from_paradigm_map(NOUN_PARADIGM_MAP_PATH)
        OUTPUT_FILE_PATH = args.output_dir + "/" + NOUN_OUTPUT_FILE_NAME
    else:
        TEST_SECTIONS = get_test_sections_from_paradigm_map(VERB_PARADIGM_MAP_PATH)
        OUTPUT_FILE_PATH = args.output_dir + "/" + VERB_OUTPUT_FILE_NAME

    results = read_logs(args.input_file_name, args.scraped_csv_path, args.for_nouns)
    output_line = prepare_output(results)
    prev_output_line = get_prev_output_line()
    if prev_output_line == output_line:
        print(f"Did not write to CSV ({OUTPUT_FILE_PATH}) as there were no changes to the test results (or date!).")
    else:
        write_to_csv(output_line)
    print_summary_stats(results, args.for_nouns)

main()
