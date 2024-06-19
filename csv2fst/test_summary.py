"""A script for summarizing results of morphological analysis tests on OPD forms."""

import os
from re import search, sub
from datetime import date

OUTPUT_FILE_NAME = "test_summary.csv"
INPUT_FILE_NAME = "opd-test.log"
# If you view in Excel, this will prevent fractions from being interpreted as dates
ADD_APOSTROPHE = True
PRINT_DETAILED_EVAL = False
TEST_SECTIONS = ["VAIO", "VAI_V", "VAI_VV", "VAI_am", "VAI_n", "VII_V", "VII_VV", "VII_d", "VII_n", "VTA_C", "VTA_Cw", "VTA_aw", "VTA_n", "VTI_aa", "VTI_am", "VTI_i", "VTI_oo"]



def write_to_csv(output_line):
    HEADER = "Date," + ",".join(TEST_SECTIONS) +  ",Total passes,Total passes (%)"
    if not os.path.isfile(OUTPUT_FILE_NAME):
            with open(OUTPUT_FILE_NAME, "w+") as csv_file:
                print(HEADER, file = csv_file)
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
    output_line = str(date.today()) + "," # First column is the date!
    total_passes = 0
    total_tests = 0
    for test_section in TEST_SECTIONS:
        if ADD_APOSTROPHE:
            output_line += "'"
        # If we don't have an expected section (maybe due to some recent reorganizing), you can just say 0/0 failures
        if not (test_section in results.keys()):
            output_line += "N/A,"
        else:
            # Add the results from this test section to our output line
            output_line += results[test_section][0]
            if PRINT_DETAILED_EVAL:
                output_line += " False pos: " + str(results[test_section][1]) + " False neg: " + str(results[test_section][2])
            output_line += ","
            total_passes += int((results[test_section][0].partition("/"))[0])
            total_tests += int((results[test_section][0].partition("/"))[2])
    
    # Last columns are the total count and then percent
    output_line += str(total_passes) + "/" + str(total_tests) + ","
    output_line += "{:.0%}".format(total_passes / total_tests)

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
        elif "Missing results" in line:
            false_neg += 1
        elif search("Unexpected results: [a-z]", line):
            false_pos += 1
        # Get the # of fails / # of tests
        elif line.startswith("Total"):
            section_results = line.strip()
            section_results = section_results.replace("Total passes: ", "")
            section_results = sub(", Total fails: [0-9]+, Total: ", "/", section_results)
            results.update({test_section: [section_results, false_pos, false_neg]})

    assert len(results) > 0, "\nERROR: The log file didn't have any test results to read!"
    return results

def main():
    results = read_logs()
    output_line = prepare_output(results)
    prev_output_line = get_prev_output_line()
    if prev_output_line == output_line:
        print(f"Did not write to CSV ({OUTPUT_FILE_NAME}) as there were no changes to the test results (or date!).")
    else:
        write_to_csv(output_line)

main()
