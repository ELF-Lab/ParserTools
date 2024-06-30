"""A script for summarizing results of morphological analysis tests on OPD forms."""

import os
from re import findall, search
from datetime import date

OUTPUT_FILE_NAME = "test_summary.csv"
INPUT_FILE_NAME = "opd-test.log"
TEST_SECTIONS = ["VAIO", "VAI_V", "VAI_VV", "VAI_am", "VAI_n", "VII_V", "VII_VV", "VII_d", "VII_n", "VTA_C", "VTA_Cw", "VTA_aw", "VTA_n", "VTA_s", "VTI_aa", "VTI_am", "VTI_i", "VTI_oo"]

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
    total_percent_forms_with_no_results = round((total_forms_with_no_results / total_forms) * 100, 2)
    # Put the summary info at the *start* of the output line
    total_output = str(total_precision) + "%," + str(total_recall) + "%," + str(total_forms) + "," + str(total_forms_with_no_results) + " (" + str(total_percent_forms_with_no_results) + "%),"
    output_line = total_output + output_line

    # First column is the date!
    output_line = str(date.today()) + ","  + output_line

    return output_line

def read_logs():
    results = {}
    file = open(INPUT_FILE_NAME, "r")
    test_section = ""
    for line in file:
        # Get the name of the current test section
        if line.startswith("YAML test file"):
            test_section = line.strip()
            test_section = test_section.replace("YAML test file database_yaml_output/", "")
            test_section = test_section.replace(".yaml", "")
            false_pos = 0
            false_neg = 0
            number_of_forms = 0
            number_of_forms_with_no_results = 0

        # Get the number of forms being tested in this section
        if "1/" in line:
            # The format is [1/X], where we want X
            denominator_starting_pos = line.index("1/") + 2
            denominator_ending_pos = line.index("]") - 1
            number_of_forms = int(line[denominator_starting_pos: denominator_ending_pos + 1])

        # "Missing" = an OPD analysis that the FST failed to produce
        elif "Missing results" in line:
            false_neg += (1 + line.count(","))

        # "Unexpected" = an analysis produced by the FST not shared by the OPD
        elif search(r"Unexpected results: [a-z]", line):
            false_pos += (1 + line.count(","))

        elif search(r"Unexpected results: \+\?", line):
            number_of_forms_with_no_results += 1

        # The final line for this section -- get the # of passes (true pos), and calculate summary stats
        elif line.startswith("Total"):
            # There's a pass for every correctly predicted analysis = true positives
            # The # of passes is the first number in this line
            true_pos = int((findall(r"[0-9]+", line))[0])

            test_section_results = {"true_pos": true_pos, "false_pos": false_pos, "false_neg": false_neg, "number_of_forms": number_of_forms, "number_of_forms_with_no_results": number_of_forms_with_no_results}
            results.update({test_section: test_section_results})

    assert len(results) > 0, "\nERROR: The log file didn't have any test results to read!"
    return results

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

def main():
    results = read_logs()
    output_line = prepare_output(results)
    prev_output_line = get_prev_output_line()
    if prev_output_line == output_line:
        print(f"Did not write to CSV ({OUTPUT_FILE_NAME}) as there were no changes to the test results (or date!).")
    else:
        write_to_csv(output_line)

main()
