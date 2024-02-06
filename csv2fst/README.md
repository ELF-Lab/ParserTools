# csv2fst

This directory houses the tools for converting csv spreadsheets of Ojibwe (and eventually, we hope, Algonquian languages more generally) to lexc files and a foma-based FST.

## Dependencies

You will need to install the foma compiler and flookup program (which is part of the foma toolkit). Install them using these [instructions](https://blogs.cornell.edu/finitestatecompling/2016/08/24/installing-foma/) or [homebrew](https://formulae.brew.sh/formula/foma).

To install python library requirements, run:
```
pip3 install -r requirements.txt
```

In order to build the FST, you will need to clone the
BorderLakesMorph
[repository](https://github.com/ELF-Lab/BorderLakesMorph) which
contains all the source data for the FST model.

If you want to run YAML tests, you will also need to install the [giella-core](https://github.com/giellalt/giella-core) repository.

## Building the Ojibwe FST

The Makefile requires modifications:
1. Modify the `BORDERLAKESMORPH` variable to point to your BorderLakesMorph repo.

You should now be able to run `make all` to build the FST. This will
create a directory `generated` which contains the FST, lexc files and
XFST rules.

## Running YAML tests

The Makefile requires modifications:
1. You may potentially need to modify the `MORPHTEST` variable to
point to your copy of the `morph-test.py` script (you might not need
to do anything if you have installed `giella-core`).

You should now be able to run `make all` and `make check`. This will generate two log files `yaml-test.log` and `core-yaml-test.log`. The first file represents tests for the subset of the Ojibwe morphology which we currently understand better. There is more uncertainty and dialectal variation in the tests presented in `yaml-test.log`. 

Both log files should show very few failures (5-15 fails per file).

## The `csv2lexc.py` script

```
Usage: csv2lexc.py [OPTIONS]

Options:
  --config-file TEXT              JSON config file  [required]
  --lexc-path TEXT                Directory where output lexc files are stored
                                  [required]
  --read-lexical-database BOOLEAN
                                  Whether to include lexemes from an external
                                  lexicon database
  --help                          Show this message and exit.
```

### JSON config files
```
{
  "comments": "You should modify the 'path' entry to match your CSV source directory",
  "source_path": "~/src/BorderLakesMorph/Spreadsheets/",
  "regular_csv_files": [
    "VAIO_CNJ",
    "VAIO_IMP",
    "VAIO_IND",
    "VAI_CNJ",
    "VAI_IMP",
    "VAI_IND",
    "VAI_Reflex_Recip",
    "VII_CNJ",
    "VII_IND",
    "VTA_CNJ",
    "VTA_IMP",
    "VTA_IND",
    "VTI_CNJ",
    "VTI_IMP",
    "VTI_IND"
  ],
  "irregular_csv_files": [
    "VTA_IRR"
  ],
  "lexical_database": "~/src/BorderLakesMorph/Database/main_entries-VERBS_fields-lemma-stem-POS.csv",
  "class_map": "~/src/BorderLakesMorph/Database/VERBS_paradigm_map.csv",  
  "regular_lexc_file": "ojibwe_verbs.lexc",
  "irregular_lexc_file": "ojibwe_irregular_verbs.lexc",
  "morph_features": [
    "Paradigm",
    "Order",
    "Negation",
    "Mode",
    "Subject",
    "Object"
  ],
  "missing_tag_marker": "NA",
  "missing_form_marker": "MISSING",
  "multichar_symbols": [
    "i1"
  ],
  "pre_element_tag": "[PREVERB]"
```
