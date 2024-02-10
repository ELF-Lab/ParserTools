# csv2fst

This directory houses the tools for converting csv spreadsheets of
Ojibwe (and eventually, we hope, Algonquian languages more generally)
to lexc files and a foma-based FST.

## Dependencies

You will need to install the foma compiler and flookup program (which
is part of the foma toolkit). Install them using these
[instructions](https://blogs.cornell.edu/finitestatecompling/2016/08/24/installing-foma/)
or [homebrew](https://formulae.brew.sh/formula/foma).

To install python library requirements, run:
```
pip3 install -r requirements.txt
```

In order to build the FST, you will need to clone the
BorderLakesMorph
[repository](https://github.com/ELF-Lab/BorderLakesMorph) which
contains all the source data for the FST model.

If you want to run YAML tests, you will also need to install the
[giella-core](https://github.com/giellalt/giella-core) repository. You should:

1. Clone the `giella-core` repository
2. In the `giella-core` directory, run `./autogen.sh`, `./configure`, `make` and `make install`

Then, add the path to the giella-core repository to your shell startup files. E.g. if you're running `zsh`, you should add the following to the `.zshenv` file in your home directory (where you change directory path appropriately):

```
export GTCORE=~/src/giella-core # Change this path to match the location of your giella-core repo
```

## Building the Ojibwe FST

The Makefile requires modifications: 1. Modify the `MORPHOLOGYSRCDIR`
variable to point to your BorderLakesMorph repo (or a different source
directory if you are building for a different language/dialect).

You should now be able to run `make all` to build the FST. This will
create a directory `generated` which contains the FST, lexc files and
XFST rules.

## Running YAML tests

The Makefile requires modifications:
1. You may potentially need to modify the `MORPHTEST` variable to
point to your copy of the `morph-test.py` script (you might not need
to do anything if you have installed `giella-core`).

You should now be able to run `make all` and `make check`. This will
generate three log files:

* `yaml-test.log` (tests for the subset of the Ojibwe morphology
which we currently understand well)
* `core-yaml-test.log` (there is more uncertainty and
dialectal variation in the tests)
* `opd-test.log` (these tests check integration of an external lexical resource)
The

The first two log files should show very few failures (5-15 fails per file). The third one will probably contain more failures

## The `csv2lexc.py` script

```
Usage: csv2lexc.py [OPTIONS]

Options:
  --config-file TEXT              JSON config file  [required]
  --lexc-path TEXT                Directory where output lexc files are stored [required]
  --read-lexical-database BOOLEAN
                                  Whether to include lexemes from an external
                                  lexicon database
  --help                          Show this message and exit.
```

### JSON configuration files

You need to specify a JSON configuration file which controls the
generation of lexc files. See
[`ojibwe_verbs.json`](https://github.com/ELF-Lab/BorderLakesMorph/blob/main/ojibwe_verbs.json)
in the [BorderLakesMorph](https://github.com/ELF-Lab/BorderLakesMorph)
repository for an example.

You need to specify the following parameters:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `comments`  | Comments. | `"This is a comment"` |
| `source_path` | Directory where source CSV files reside. | `"~/src/BorderLakesMorph/Spreadsheets/"` |
| `regular_csv_files` | List of CSV files which contain **regular** paradigms (please omit `.csv` suffix) | `["VAI_IND","VTA_CNJ",...]` |
| `irregular_csv_files` | List of CSV files which contain **irregular** paradigms (please omit `.csv` suffix) | `["VAI_IRR"]` |
| `lexical_database` | External CSV lexical database file. | `"verb_entries_from_dictionary.csv"` |
| `class_map` | A mapping from inflectional classes in the external lexical database to inflectional classes usind in the FST (i.e. the classes in the source CSV files). See further description below. | `"verb_class_map.csv"` |
| `regular_lexc_file` | Filename for generated lexc file containing **regular** paradigms. | `"ojibwe_verbs_regular.lexc"` | 
| `irregular_lexc_file` | Filename for generated lexc file containing **irregular** paradigms. | `"ojibwe_verbs_irregular.lexc"` | 
| `morph_features` | This field specifies the order in which morphological features are realized in FST output fields. The elements in the list have to match columns of the spurce CSV files. |  `["Paradigm", "Order", "Negation", "Mode", "Subject", "Object"]` |
| `missing_tag_marker` | Tag which indicates missing values of features in the source CSV files. E.g. intransitive verbs won't have an onbject, and this tag is used to mark that fact. | `"NA"` |
| `missing_form_marker` | Tag which indicates paradigm gaps | `"MISSING"` |
| `multichar_symbols` | List of multi-character symbols which are used in the source CSV files | `["i1", "w1"]` |
| `pre_element_tag` | A tag which is used to indicate the position of pre-elements like preverbs and prenouns in the lexc files | `"[PREVERB]"`

### The external lexical database

TODO

### Inflectional class mapping

TODO
