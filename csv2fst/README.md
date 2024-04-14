# csv2fst

This directory houses the tools for converting csv spreadsheets of
Ojibwe (and eventually, we hope, Algonquian languages more generally)
to lexc files and a foma-based FST.

## Dependencies for the `csv2fst.py` script

You will need to install the foma compiler and flookup program (which
is part of the foma toolkit). Install them using these
[instructions](https://blogs.cornell.edu/finitestatecompling/2016/08/24/installing-foma/)
or [homebrew](https://formulae.brew.sh/formula/foma).

To install python library requirements, run:
```
pip3 install -r requirements.txt
```

In order to build the Border Lakes Ojibwe FST, you will need to clone the
[BorderLakesMorph repository](https://github.com/ELF-Lab/BorderLakesMorph) which
contains all the source data for the FST model.

## Dependencies for YAML tests (optional)

If you want to run YAML tests, you will also need to install the
[giella-core](https://github.com/giellalt/giella-core) repository. You should:

1. Clone the `giella-core` repository
2. You may need to install ICU for enhanced Unicode character set support:
     * On a Mac, you can install it by `brew install icu4c`. This will install the program `uconv`, which is used by `giella-core`, but will not add it to your `PATH` environmental variable, so you'll need to manually edit `PATH`. Run `brew info icu4c` to check where the program is located. The info command also prints instructions for adding the `uconv` location to `PATH`. You probably need to open a new terminal window after editing `PATH` to activate the changes
     * On Linux, you can run `sudo apt install libicu52=52.1-6` and `sudo apt-get install libicu-dev` (**not tested**)
3. You may need to install GNU `autotools` in order to run `autogen.sh` 
     * On mac, you can install these by running `brew install autoconf automake libtool`
     * On Linux, do `sudo apt-get install autotools-dev` and `sudo apt-get install autoconf`
5. In the `giella-core` directory, run `./autogen.sh`, `./configure`, `make` (probably doesn't do anything) and `make install` in this order

Then, add the path to the `giella-core` repository to your shell startup files. E.g. if you're running `zsh`, you should add the following to the `.zshenv` file in your home directory (where you change the directory path appropriately):

```
export GTCORE=~/src/giella-core # Change this path to match the location of your giella-core repo
```

If you're running `bash`, this export probably needs to go to your `.bashrc` or `.profile` file (or both to be on the safe side).

You will need to open a new terminal, after you're done with installation in order to activate the `$GTCORE` variable. 

## Building the Border Lakes Ojibwe FST

The Makefile requires modifications: 1. Modify the `MORPHOLOGYSRCDIR`
variable to point to your BorderLakesMorph repo.

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
| `source_path` | Directory where source CSV files for verbs reside. | `"~/src/BorderLakesMorph/VerbSpreadsheets/"` |
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
| `pre_element_tag` | A tag which is used to indicate the position of pre-elements like preverbs and prenouns in the lexc files | `"[PREVERB]"`|
|`pv_source_path`| This should point to your PVSpreadsheets directory (this is a subdirectory of BorderLakesMorph) | "~/src/BorderLakesMorph/PVSpreadsheets/" |

### The external lexical database

Additional lexemes are supplied in a 3-column CSV file. Here are the first rows of the lexical database file for BorderLakes Ojibwe, which stems from the [Ojibwe People's Dictionary]() (OPD): 

```
lemma,stem,part_of_speech_id
ayaan,aya,vti4
gidaan,gidaa,vti4
de-miijin,de-miiji,vti3
gigizhebaa-miijin,gigizhebaa-miiji,vti3
miijin,miiji,vti3
naadin,naad,vti3
```

This file is located in the BorderLakesMorph repo in the subdirectory `Database`.

The columns represent:

1. Lemma (this has to agree with the lemma forms in `BorderLakesMorph/Spreadsheets`)
2. Stem (this has to agree with the stems in `BorderLakesMorph/Spreadsheets`)
3. POS tag following OPD guidelines 

In the JSON configuration file, the path to the lexical database is supplied under the key `lexical_database`.

### Inflectional class mapping

OPD pos tags, need to be maped into inflectional classes like `VTA_s` used in the paradigm spreadsheets in `BorderLakesMorph/Spreadsheets`. This mapping is realized by a specific csv file which can be given using the key `class_map` in the JSON configuration file.

Here is the mapping which translates OPD pos tags to inflectional classes for the Border Lakes Ojibwe FST ([BorderLakesMorph/Database/VERBS_paradigm_map.csv](https://github.com/ELF-Lab/BorderLakesMorph/blob/main/Database/VERBS_paradigm_map.csv)):

```
Class,OPDClass,MatchElement,Pattern
VAI_V,vai,lemma,"^.*[^aiou][aiou]$"
VAI_VV,vai,lemma,"^.*(aa|ii|oo|e)$"
VAI_am,vai2,lemma,"^.*am$"
VAI_m,vai,lemma,"^.*m$"
VAI_n,vai,lemma,"^.*n$"
VAI_rcp,vai,stem,"^.*idi$"
VAI_rcp,vai,lemma,"^.*diwag$"
VAI_rfx,vai,stem,"^.*idizo$"
VAIO,vai+o,lemma,"^.*$"
VII_VV,vii,lemma,"^.*(aa|ii|oo|e)$"
VII_V,vii,lemma,"^.*[^iou][iou]$"
VII_d,vii,lemma,"^.*d$"
VII_n,vii,lemma,"^.*n$"
VTA_C,vta,lemma,"^.*[bcdfghjklmptz']$"
VTA_C,vta,lemma,"^.*[^bcdfghjklmnpstzwa']w$"
VTA_Cw,vta,stem,"^.*[bcdfghjklmnpstwz']w$"
VTA_aw,vta,lemma,"^.*aw$"
VTA_n,vta,stem,"^.*n$"
VTA_s,vta,stem,"^.*s$"
VTI_am,vti1,lemma,"^.*an$"
VTI_i,vti3,stem,"^.*i$"
VTI_oo,vti2,lemma,"^.*oon$"
VTI_aa,vti4,lemma,"^.*aan$"
```

Each row defines a test which determines the inflectional class. The test is based on the OPD POS tag, the lemma/stem of the lexical entry and a regular expression pattern, which has to be matched in order to group a lexeme to a specific inflectional class:

1. The intended inflectional class in the paradigm spreadsheets
2. The POS tag in the lexical database
3. Whether to test the regular expression pattern on the lemma or stem of the lexeme
4. The regular expression pattern

Each test is run in order until a matching one is found.

E.g. consider the row (lemma,stem,POS):
```
aatwaakowebin,aatwaakowebin,vta
```
The inflectional class will be `VTA_n` because this lexeme matches the test:
```
VTA_n,vta,stem,"^.*n$"
```
because the POS is `vta` and the stem matches the regular expression `^.*n$`.
