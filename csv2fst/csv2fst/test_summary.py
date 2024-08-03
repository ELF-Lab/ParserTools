"""A script for summarizing results of morphological analysis tests on OPD forms."""

import os
from re import findall, search
from datetime import date
import pandas as pd

OUTPUT_FILE_NAME = "test_summary.csv"
INPUT_FILE_NAME = "opd-test.log"
TEST_SECTIONS = ["VAIO", "VAI_V", "VAIPL_V", "VAI_VV", "VAIPL_VV", "VAI_am", "VAI_m", "VAI_n", "VAIPL_n", "VAI_rcp", "VAI_rfx", "VII_V", "VII_VV", "VIIPL_VV", "VII_d", "VIIPL_d", "VII_n", "VTA_C", "VTA_Cw", "VTA_aw", "VTA_n", "VTA_s", "VTI_aa", "VTI_am", "VTI_i", "VTI_oo"]
YAML_FOLDER = "./database_yaml_output"
DO_PRINT_FORMS_WITH_NO_RESULTS = False

def write_to_csv(output_line):
    HEADER_1 = "Date,"
    HEADER_2 = ","
    summary_sections = ["Total"]
    summary_sections.extend(TEST_SECTIONS)
    for section in summary_sections:
        HEADER_1 += section + ","
        HEADER_1 += ",,,"
        HEADER_2 += "Precision,Recall,Forms,Forms Without Results,"

    if not os.path.isfile(OUTPUT_FILE_NAME):
            with open(OUTPUT_FILE_NAME, "w+") as csv_file:
                print(HEADER_1, file = csv_file)
                print(HEADER_2, file = csv_file)
    with open(OUTPUT_FILE_NAME, "a") as csv_file:
            csv_file.write(output_line + "\n")
    
    print("Wrote to", OUTPUT_FILE_NAME)
    csv_file.close()

def get_prev_output_line():
    prev_output_line = ""
    if os.path.isfile(OUTPUT_FILE_NAME):
        with open(OUTPUT_FILE_NAME, "r") as csv_file:
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

def read_logs():
    results = {}
    forms_with_no_results = []
    file = open(INPUT_FILE_NAME, "r")
    test_section = ""
    for line in file:
        # Get the name of the current test section
        if line.startswith("YAML test file"):
            test_section = line.strip()
            test_section = test_section[test_section.index("/") + 1:]
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

        # Some FST analyses are "Unexpected" because they're empty!
        elif search(r"Unexpected results: \+\?", line):
            number_of_forms_with_no_results += 1
            form_start = line.index("[FAIL] ") + len("[FAIL] ")
            form_end = line.index(" =>") - 1
            forms_with_no_results.append({"form": line[form_start:form_end + 1].strip(), "pos": test_section})

        elif line.startswith("True"): # A final line with summary info
            number_of_forms = int(line.partition("Unique inflected forms being tested: ")[2])

        # The final line summarative for this section -- get the # of passes (true pos), and calculate summary stats
        elif line.startswith("Total"):
            # There's a pass for every correctly predicted analysis = true positives
            # The # of passes is the first number in this line
            true_pos = int((findall(r"[0-9]+", line))[0])

            test_section_results = {"true_pos": true_pos, "false_pos": false_pos, "false_neg": false_neg, "number_of_forms": number_of_forms, "number_of_forms_with_no_results": number_of_forms_with_no_results}
            results.update({test_section: test_section_results})

    if DO_PRINT_FORMS_WITH_NO_RESULTS:
        print_forms_with_no_results(forms_with_no_results)

    assert len(results) > 0, "\nERROR: The log file didn't have any test results to read!"
    return results

def print_forms_with_no_results(form_list):
    SCRAPED_CSV_PATH = "~/ParserTools/scrapedcsv2yaml/csv_output/inflectional_forms_for_yaml.csv"
    ERRONEOUS_FORMS_CSV_PATH = "~/OPDDatabase/data/OPDPatch.csv"

    if len(form_list) > 0:
        # Read in the spreadsheet of scraped forms to get more info about this form
        scraped_forms = pd.read_csv(SCRAPED_CSV_PATH, keep_default_na = False)
        # Read in the spreadsheet of forms that have already been identified as OPD errors,
        # because they don't need to be investigated again!
        erroneous_forms = pd.read_csv(ERRONEOUS_FORMS_CSV_PATH, keep_default_na = False)
        erroneous_lemmas = [row["OPDLemma"] for _, row in erroneous_forms.iterrows()]

        current_section = form_list[0]["pos"]
        print(f"------ {current_section}: ------")
        # Go through each of the forms we flagged as having no results
        for form in form_list:
            # Print a new header for each section e.g., VAIO, VAI_V, etc.
            if form["pos"] != current_section:
                current_section = form["pos"]
                print(f"\n\n------ {current_section}: ------")

            # Find the form we're looking for in the big spreadsheet
            for _, row in scraped_forms.iterrows():
                row = row.to_dict()
                if form["form"] == row["Form1Surface"]:
                    # Check that this form isn't in our list of already-known errors
                    if row["Lemma"] not in erroneous_lemmas:
                        print("Form:", form["form"])
                        print(f"Info from OPD: Order: {row['Order']}, Class: {row['Class']}, Lemma: {row['Lemma']}, Stem: {row['Stem']}, Subject: {row['Subject']}, Object: {row['Object']}, Mode: {row['Mode']}, Negation: {row['Negation']}\n")
                    break # Stop looking when we've found it!

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

# test_summary.csv's header has a section for every class (e.g., VAI_am, VAI_m, etc.)
# If a new class has been added, there'll be nowhere to include those results in the CSV!
# You'll have to delete your existing CSV and run this code again, so that a new CSV with the
# correct headers is created.
# And don't forget to update TEST_SECTIONS with the new section!
# This check will flag this scenario.
# I didn't want this all to happen automatically, in case you want to save your old CSV first.
def check_test_sections():
    test_sections_in_yaml = []
    for root, dirs, files in os.walk(YAML_FOLDER):
        for file_name in files:
            if not "core" in file_name:
                test_sections_in_yaml.append(file_name.partition(".")[0])

    for test_section in test_sections_in_yaml:
        if test_section not in TEST_SECTIONS:
            print(f"\nA new test section ({test_section}) has been detected.  You should delete your current test_summary.csv, add the new section to TEST_SECTIONS, and re-run this, because we need a new CSV header to capture the current test sections!\nExiting...")
            exit()

def main():
    check_test_sections()
    results = read_logs()
    output_line = prepare_output(results)
    prev_output_line = get_prev_output_line()
    if prev_output_line == output_line:
        print(f"Did not write to CSV ({OUTPUT_FILE_NAME}) as there were no changes to the test results (or date!).")
    else:
        write_to_csv(output_line)

main()
