import argparse
import pandas as pd
import json
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '../csv2yaml'))
from create_yaml import create_output_directory

# Parameters for the user to specify
OUTPUT_FILE_NAME = "inflectional_forms_for_yaml.csv"
STEMS_TO_EXCLUDE = ["akwaakwak", "banzw", "baakindesijiged", "baasindibeshkoozo", "begaki-ozaawaakiganed", "biimitaag", "gawishimo'", "gikas", "giitakizine'", "gwayakomaagwad", "ikwabiitaw", "ishkwegamaag", "makadewitawag", "begakiozaawaakiganed", "miiwanaand", "onzw", "ozhibii'igetamaw", "waazhwi", "wiijishimotaadiwag", "zagwakizowag"]
PRINT_MISSING_INFO_SUMMARY = False

POS_TO_KEEP = ["vai + o", "vta", "vai", "vii", "vti", "vti2", "vti3", "vti4"]
POS_WITH_CLASS_IN_FILE_NAME = ["VAI", "VTA", "VII", "VTI", "VTI2", "VTI3", "VTI4"]
ALL_OPD_ORDERS = {"ch-conj", "conj", "ic", "imp", "ind", "part"}
PERMITTED_ORDER_CONVERSIONS = {"conj": "Cnj", "imp": "Imp", "ind": "Ind"} # Just add entries here once we're supporting other orders!
VOWELS = ["i", "e", "o", "a"]
RECIPROCAL_LEMMA_ENDING = "wag"
RECIPROCAL_STEM_ENDING = "di"
REFLEXIVE_LEMMA_ENDING = "dizo"
EMPTY_FIELD_MARKER = "NONE"
# These will be filled out by reading in the relevant file
PARTICIPANT_TAG_CONVERSIONS = {}
POSSIBLE_PARTICIPANTS = []

def read_subj_objs_tags(subj_obj_tags_csv):
    global PARTICIPANT_TAG_CONVERSIONS
    global POSSIBLE_PARTICIPANTS

    conversions_list = pd.read_csv(subj_obj_tags_csv)
    for i, tag_conversion in conversions_list.iterrows():
        if "/" in tag_conversion["OurTag"]:
            tags = tag_conversion["OurTag"].split("/")
            PARTICIPANT_TAG_CONVERSIONS[tag_conversion["OPDTag"]] = [tags[0], tags[1]]
        else:
            PARTICIPANT_TAG_CONVERSIONS[tag_conversion["OPDTag"]] = tag_conversion["OurTag"]
    POSSIBLE_PARTICIPANTS = PARTICIPANT_TAG_CONVERSIONS.keys()

def process_json(file_name):
    scraped_data = json.load(open(file_name))
    forms_with_info = []

    for row in scraped_data:
        # Grab only the verbs!
        if row["pos_type"] in POS_TO_KEEP:
            forms_and_stem = row["section_inflection_forms"]
            # Check if there's any inflectional forms
            if len(forms_and_stem) > 1:
                # Missing info check
                if "lemma" in row and "stem" in forms_and_stem[-1] and "pos_type" in row:
                    stem_etc = {"Lemma": row["lemma"], "Stem": forms_and_stem[-1]["stem"], "POS": row["pos_type"]}
                    # Add each inflectional form
                    for form in forms_and_stem[:-1]:
                        form_with_info = {"Inflectional Form": form["word"], "Abbreviated Gloss": form["desc"]}
                        form_with_info.update(stem_etc)
                        form_with_info = tidy_entry(form_with_info)
                        if missing_info_check(form_with_info):
                            form_with_info = format_entry(form_with_info)
                            forms_with_info.append(form_with_info)

                elif PRINT_MISSING_INFO_SUMMARY:
                    print("\nForm(s) excluded due to missing lemma/stem/pos. Info:")
                    print(row)

    return forms_with_info

# Takes one row at a time
# Returns a bool, True = keep it in, False = remove it
def missing_info_check(form_with_info):
    # Check for missing stem OR an erroenous stem we noticed
    has_a_stem = (form_with_info["Stem"] != "" and not (form_with_info["Stem"] in STEMS_TO_EXCLUDE))

    has_a_subj = False
    glosses = form_with_info["Abbreviated Gloss"].split()
    if len(glosses) > 0:
        potential_subj = glosses[0]
        if potential_subj in POSSIBLE_PARTICIPANTS:
            has_a_subj = True

    has_an_order = False
    # To be thorough, check if both a) one of the permitted orders is listed and b) none of the non-permitted orders are
    for permitted_order in PERMITTED_ORDER_CONVERSIONS.keys():
        if permitted_order in glosses:
            has_an_order = True
            for non_permitted_order in (ALL_OPD_ORDERS - PERMITTED_ORDER_CONVERSIONS.keys()):
                if non_permitted_order in glosses:
                    has_an_order = False

    contains_weird_punctuation = "=" in form_with_info["Inflectional Form"]
    has_a_form = form_with_info["Inflectional Form"] != ""

    if PRINT_MISSING_INFO_SUMMARY:
        if not (has_an_order and has_a_stem and has_a_subj and not(contains_weird_punctuation)):
            print(f"\nInflectional form: {form_with_info['Inflectional Form']} (lemma: {form_with_info['Lemma']})")
            print("Abbreviated gloss:", form_with_info["Abbreviated Gloss"])
        if not (has_an_order):
            print("Problem: This stem did not have an Order that we recognized (i.e., one of ind, conj, imp, part, ic, or ch-conj).")
        if not (has_a_stem):
            print("Problem: This form has an empty stem.")
        if not (has_a_subj):
            print("Problem: This form has no subject.")

    return has_an_order and has_a_stem and has_a_subj and has_a_form and not(contains_weird_punctuation)

def tidy_entry(form_with_info):
    # Stems are typically written with a final hyphen, which should be removed
    if form_with_info["Stem"].endswith("-"):
        form_with_info["Stem"] = form_with_info["Stem"][:-1]
    # This check, however, is to fix erroneous forms!
    if form_with_info["Inflectional Form"].startswith("-"):
        form_with_info["Inflectional Form"] = form_with_info["Inflectional Form"][2:]
    for field_name in form_with_info.keys():
        form_with_info[field_name] = form_with_info[field_name].strip()

    form_with_info["OPD POS"] = form_with_info["POS"] # Save this
    if form_with_info["POS"] == "vai + o":
        form_with_info["POS"] = "vaio"
    form_with_info["POS"] = form_with_info["POS"].upper()

    return form_with_info

# Manages the adding of fields we need for our new CSV
def format_entry(form_with_info):
    form_with_info = add_order(form_with_info)

    # Dictionary uses VTI/VTI2/VTI3/VTI4 as POS, but we want to convert all of those to just VTI
    # However, this info lets us easily determine class
    # So we will assign class *first* before we lose those labels, then lose them!
    form_with_info = add_class(form_with_info)
    if "VTI" in form_with_info["POS"]:
        form_with_info["POS"] = "VTI"

    form_with_info = add_person_and_number(form_with_info)

    form_with_info = add_mode(form_with_info)

    form_with_info = add_negation(form_with_info)

    return form_with_info

def add_order(form_with_info):
    short_gloss = form_with_info["Abbreviated Gloss"]
    order = None

    for possible_order in PERMITTED_ORDER_CONVERSIONS.keys():
        if possible_order in short_gloss:
            order = PERMITTED_ORDER_CONVERSIONS[possible_order]
            break # Match found! Stop looking

    if not order:
        print(f"\nERROR: Form {form_with_info['Inflectional Form']} does not have an expected order value.  Please investigate this form in the spreadsheet and update the code accordingly.  Exiting...")
        sys.exit()
    else:
        form_with_info["Order"] = order
        return form_with_info

# Add an entry to the dict that indicates the class of the stem (e.g. n, am, etc.)
# For some POS, like VAIO, we don't want the class in the file name at all
def add_class(form_with_info):
    pos = form_with_info["POS"]
    stem = form_with_info["Stem"]

    verb_class = ""
    if pos == "VTA":
        if stem.endswith("aw"):
            verb_class = "aw"
        elif stem.endswith("w") and not stem[-2] in VOWELS:
            verb_class = "Cw"
        elif stem.endswith("n"):
            verb_class = "n"
        # This condition is needlessly explicit, just to be clear about the categories
        elif not stem[-1] in VOWELS and not stem[-1] == "s" and not stem[-1] == "n":
            verb_class = "C"
        elif stem[-1] == "s":
            verb_class = "s"
        # Remaining classes: irr
    elif pos == "VAI":
        if stem.endswith("n"):
            verb_class = "n"
        elif stem.endswith("m") and stem[-2] != "a":
            verb_class = "m"
        elif stem.endswith("m") and stem[-2] == "a":
            verb_class = "am"
        elif (stem[-1] in VOWELS and stem[-2] in VOWELS) or stem.endswith("e"):
            verb_class = "VV"
        elif stem[-1] in VOWELS:
            verb_class = "V"
        # Remaining classes: rcp, rfx
    elif pos == "VII":
        if stem.endswith("d"):
            verb_class = "d"
        elif stem.endswith("n"):
            verb_class = "n"
        elif (stem [-1] in VOWELS and stem[-2] in VOWELS) or stem.endswith("e"):
            verb_class = "VV"
        elif stem [-1] in VOWELS:
            verb_class = "V"
        # Remaining classes: none!
    if "VTI" in pos:
        if pos == "VTI":
            verb_class = "am"
        elif pos == "VTI2":
            verb_class = "oo"
        elif pos == "VTI3":
            verb_class = "i"
        elif pos == "VTI4":
            verb_class = "aa"

    # Make sure we assigned a class where needed
    if verb_class:
        form_with_info["Class"] = verb_class
    elif pos in POS_WITH_CLASS_IN_FILE_NAME:
        print(f"\nERROR: You need to assign a class (e.g. info about the final characters in the stem) to a form with this stem: {form_with_info['Stem']}. (POS: {pos})  Exiting...")
        sys.exit()
    return form_with_info

# Add 1SG, 3PLObv, etc.
# Transitive verbs (VTA, VTI) will have two participants
# Intransitive verbs (VAI, VII) will have one participant
# Seems like VAIO can go either way
def add_person_and_number(form_with_info):
    short_gloss = form_with_info["Abbreviated Gloss"].split()
    if "-" in short_gloss:
        short_gloss.remove("-")

    # Add info for the first participant
    subject_participant = short_gloss[0]
    form_with_info["Subject"] = PARTICIPANT_TAG_CONVERSIONS[subject_participant]
    # If there's a second participant (i.e. it's transitive), add their info too
    if len(short_gloss) > 1 and short_gloss[1] in POSSIBLE_PARTICIPANTS:
        object_participant = short_gloss[1]
        form_with_info["Object"] = PARTICIPANT_TAG_CONVERSIONS[object_participant]
    # The OPD doesn't explicitly assign objects to VAIOs, but they all have them implicitly (by definition)
    elif form_with_info["POS"] == "VAIO":
        form_with_info["Object"] = "0Sg"
    # The OPD doesn't give reciprocals objects.  We want to explicitly specify their obj is the same as their subj!
    # The same is true of *reflexives*!
    elif form_with_info["POS"] == "VAI" and (form_with_info["Lemma"].endswith(RECIPROCAL_LEMMA_ENDING) and form_with_info["Stem"].endswith(RECIPROCAL_STEM_ENDING)) or (form_with_info["Lemma"].endswith(REFLEXIVE_LEMMA_ENDING)):
        form_with_info["Object"] = form_with_info["Subject"]
    else:
        form_with_info["Object"] = EMPTY_FIELD_MARKER

    # Our tags also have "Subj" or "Obj" at the end e.g., 2SgSubj
    if type(form_with_info["Subject"]) == str:
        form_with_info["Subject"] = form_with_info["Subject"] + "Subj"
    elif type(form_with_info["Subject"]) == list:
        form_with_info["Subject"] = [x + "Subj" for x in form_with_info["Subject"]]

    if form_with_info["Object"] != EMPTY_FIELD_MARKER:
        if type(form_with_info["Object"]) == str:
            form_with_info["Object"] = form_with_info["Object"] + "Obj"
        elif type(form_with_info["Object"]) == list:
            form_with_info["Object"] = [(x + "Obj") for x in form_with_info["Object"]]

    return form_with_info

# Neu, Prt, Dub, DubPrt, with Neu being the default
def add_mode(form_with_info):
    short_gloss = form_with_info["Abbreviated Gloss"]

    if "pret" in short_gloss and "dub" in short_gloss:
        mode = "DubPrt"
    elif "pret" in short_gloss:
        mode = "Prt"
    elif "dub" in short_gloss:
        mode = "Dub"
    elif "imp" in short_gloss: # Imperatives get their own mode: simple
        mode = "Sim"
    else:
        mode = "Neu"

    form_with_info["Mode"] = mode

    return form_with_info

# Neg, Pos, with Pos being the default
def add_negation(form_with_info):
    short_gloss = form_with_info["Abbreviated Gloss"]

    if "neg" in short_gloss:
        negation = "Neg"
    elif "imp" in short_gloss: # Imperatives don't get a negation value
        negation = ""
    else:
        negation = "Pos"

    if negation:
        form_with_info["Negation"] = negation
    return form_with_info

# Sometimes there is a 2-to-1 mapping b/w OPD tags and our tags
# For example, 3 -> 3SGProx/3PLProx
# We want to convert such forms to TWO forms, one with each tag
def handle_ambiguous_participant_tags(forms_with_info):
    for i, form in enumerate(forms_with_info):
        if type(form["Subject"]) == list:
            # Split it into two forms
            form_2 = form.copy()
            form_2["Subject"] = form["Subject"][1]
            form["Subject"] = form["Subject"][0]
            # Remove the original, and put these two forms back into the list
            forms_with_info.pop(i)
            forms_with_info.insert(i, form)
            forms_with_info.insert(i, form_2)

        if type(form["Object"]) == list:
            # Split it into two forms
            form_2 = form.copy()
            form_2["Object"] = form["Object"][1]
            form["Object"] = form["Object"][0]
            # Remove the original, and put these two forms back into the list
            forms_with_info.pop(i)
            forms_with_info.insert(i, form)
            forms_with_info.insert(i, form_2)

    return forms_with_info

# Reminder: forms_with_info is a list of dicts
def write_new_csv(forms_with_info, output_dir):
    # I believe 4 is the most inflectional forms with the same analysis?
    CSV_HEADER = "Paradigm,Order,Class,Lemma,Stem,Subject,Object,Mode,Negation,Form1Surface,Form1Split,Form1Source,Form2Surface,Form2Split,Form2Source,Form3Surface,Form3Split,Form3Source,Form4Surface,Form4Split,Form4Source,"
    prev_analysis = ""
    line_count = 0

    with open(output_dir + OUTPUT_FILE_NAME, "w+") as csv:
        csv.write(CSV_HEADER)
        for form_with_info in forms_with_info:
            # Compile all the analysis info
            analysis_to_write = form_with_info["POS"] + "," + form_with_info["Order"] + ","
            if "Class" in form_with_info.keys():
                analysis_to_write += form_with_info["POS"] + "_" + form_with_info["Class"] + ","
            else:
                analysis_to_write += form_with_info["POS"] + ","
            analysis_to_write += form_with_info["Lemma"] + "," + form_with_info["Stem"] + "," + form_with_info["Subject"] + "," + form_with_info["Object"] + "," + form_with_info["Mode"] + ","
            if "Negation" in form_with_info.keys():
                analysis_to_write += form_with_info["Negation"] + ","
            else:
                analysis_to_write += ","

            # If this is the first line with this analysis, finish off the previous line and start a fresh one
            if prev_analysis != analysis_to_write:
                line_count += 1
                csv.write("\n") # First, complete the last line
                csv.write(analysis_to_write) # Now start writing this analysis on a new line
            # If not, do nothing -- just carry on adding to the previous line
            # In either case, write the current form
            csv.write(form_with_info["Inflectional Form"] + ",")
            csv.write(",,")
            prev_analysis = analysis_to_write

    return line_count

def write_database_csv(forms_with_info, output_dir):
    CSV_HEADER = "lemma,stem,part_of_speech_id\n"
    DATABASE_CSV_NAME = "main_entries-VERBS_fields-lemma-stem-POS.csv"

    lemma_set = set()
    for form_with_info in forms_with_info:
        output_line = form_with_info["Lemma"] + "," + form_with_info["Stem"] + "," + form_with_info["OPD POS"] + "\n"
        lemma_set.add(output_line)

    with open(output_dir + DATABASE_CSV_NAME, "w") as csv:
        csv.write(CSV_HEADER)
        for lemma_line in sorted(lemma_set):
            csv.write(lemma_line)

def main():
    # Sets up argparse.
    parser = argparse.ArgumentParser(prog="create_if_yaml")
    parser.add_argument("inflectional_forms_json", type=str, help="Path to the spreadsheet.")
    parser.add_argument("subj_obj_tags_csv", type=str, help="Path to the csv containing the tag conversions between OPD and our subj/obj tags.")
    parser.add_argument("output_parent_directory", type=str, help="Path to the folder where the yaml files will be saved (inside their own subdirectory).")
    parser.add_argument("-print_database_csv", action='store_true', help="Indicates if we should print the list of all stems (with lemma and POS).")
    args = parser.parse_args()

    read_subj_objs_tags(args.subj_obj_tags_csv)

    output_directory = create_output_directory(args.output_parent_directory)

    forms_with_info = process_json(args.inflectional_forms_json)

    forms_with_info = handle_ambiguous_participant_tags(forms_with_info)

    line_count = write_new_csv(forms_with_info, output_directory)

    if args.print_database_csv:
        write_database_csv(forms_with_info, output_directory)

    print(f"Wrote CSV with {len(forms_with_info)} inflectional forms in {line_count} lines to", output_directory + OUTPUT_FILE_NAME)

if __name__ == '__main__':
    main()
