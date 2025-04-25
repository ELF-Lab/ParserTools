# csv2fst

This directory houses the tools for converting CSV spreadsheets of
language data to lexc files and a foma-based FST.  
Examples are given for Ojibwe, with the relevant language data accessible in other repos.  However, this FST-generating code is intended to be applicable for other Algonquian languages and beyond -- if you have the necessary spreadsheets for your target language, it should be compatible with this code!

## Dependencies for the `csv2fst.py` script

You will need to install the foma compiler and flookup program (which
is part of the foma toolkit). On Mac or Linux, the easiest way to install is via [homebrew](https://formulae.brew.sh/formula/foma).  Just use the command `brew install foma`.  Alternatively, there are other installation instructions [here](https://blogs.cornell.edu/finitestatecompling/2016/08/24/installing-foma/) (including for Windows users).
> Note for Windows users: In addition to the page given above, we found [these instructions](https://ufal.mff.cuni.cz/~zeman/vyuka/morfosynt/lab-twolm/get-foma.html) useful for installing.  Also, ensure that the directory you add to your PATH immediately contains `foma.exe` and `flookup.exe`.  For example, if the path to `foma.exe` is `C:\Program Files (x86)\Foma\win32\foma.exe`, then add `C:\Program Files (x86)\Foma\win32` (not `C:\Program Files (x86)\Foma\`) to your PATH.

This project uses [poetry](https://python-poetry.org/) to manage python requirements.  These can be installed as follows:
1. Navigate to `ParserTools/csv2fst`.
2. Create a virtual environment (using the python command that works on your system e.g., `python` instead of `python3` if needed):
```
python3 -m venv myvenv
```
3. Activate the virtual environment.  
On Mac or Linux, run:
```
source myvenv/bin/activate  
```   
On Windows, run:
```
source myvenv/Scripts/activate
```
4. Update `pip` and `setuptools`:
```
pip3 install -U pip setuptools
```
5. Install `poetry`:
```
pip3 install poetry
```
6. Use poetry to install the project into the virtual environment:
```
poetry install
```

Now, the dependencies are set up!

Eventually, when you're done running the virtual environment, you can close it via:
```
deactivate myvenv
```

> Note: The `Makefile` in this directory begins with some variables you can change if you run into errors.  For example, you can change the command for running python (on Windows, we had to change this from `python3` to `python`).

If you're working towards building the example FST for Ojibwe, once you're done with installing these prerequisites, carry on with the instructions in [OjibweMorph](https://github.com/ELF-Lab/OjibweMorph#building-the-fst).

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

## Building an FST
The FST is built using a Makefile.  Before building, there are three variables within the Makefile which must be set to point to the right directory locations:  
- `MORPHOLOGYSRCDIR` points to a directory that contains most of the morphological information needed to build the FST.  The example directory (for Border Lakes Ojibwe) is [OjibweMorph](https://github.com/ELF-Lab/OjibweMorph).
- `LEMMAS_DIR` points to a directory that contains CSVs listing all the lemmas that will be used to build the FST.  An example directory (for Border Lakes Ojibwe) is [OjibweLexicon/OPD](https://github.com/ELF-Lab/OjibweLexicon/tree/main/OPD).
     - This variable can also be set to a list of directories (each containing CSVs to be used), separated by a comma. 
- `OUTPUT_DIR` points to the directory where all files generated will go.  Note that in order for the testing code to work (i.e., when running `make check`), this **must be a relative path** (for some reason).

You should go into the Makefile and edit the values of these variables so that the correct directory is specified.  Once complete, you can run `make all` (or just `make`) to build the FST (e.g., `ojibwe.fomabin`). This will create a directory `generated` which contains the FST, lexc files and XFST rules.

Alternatively, rather than editing the Makefile contents, you can just specify the directory paths when you call `make all`.  For example:
```
make all MORPHOLOGYSRCDIR=~/Documents/OjibweMorph LEMMAS_DIR=~/Documents/OjibweLexicon/OPD OUTPUT_DIR=../../OjibweMorph/FST
```
These variables should also be set when running `make clean`.

Additionally, there are two other variables that must be specified if you're going to run the tests for the FST:
- `SPREADSHEETS_FOR_YAML_DIR` points to a directory which contains CSVs for running the YAML tests.  An example directory (for Border Lakes Ojibwe) is [OjibweLexicon/OPD/for_yaml](https://github.com/ELF-Lab/OjibweLexicon/tree/main/OPD/for_yaml).
- `PARADIGM_MAPS_DIR` points to a directory which contains paradigm maps created for sorting words into different categories, but used here because they contain a complete list of 'Class' values that become the test sections (e.g., VAI_V, VAI_VV, etc.).  An example directory (for Border Lakes Ojibwe) is [OjibweLexicon/resources](https://github.com/ELF-Lab/OjibweLexicon/tree/main/resources).

So when running `make check` to run the FST tests, you either need to edit all five variables right in the Makefile, or supply their values when calling `make check`:
```
make check MORPHOLOGYSRCDIR=~/Documents/OjibweMorph LEMMAS_DIR=~/Documents/OjibweLexicon/OPD SPREADSHEETS_FOR_YAML_DIR=~/Documents/OjibweLexicon/OPD/for_yaml PARADIGM_MAPS_DIR=~/Documents/OjibweLexicon/resources OUTPUT_DIR=../../OjibweMorph/FST
```

Also written into the Makefile are the expected names of many of these files (e.g., the paradigm map file for the verb tests of the FST being called `VERBS_paradigm_map.csv`), so if any of these names differ, the Makefile will have to be updated accordingly.

## Using the FST
Successfully compiling the FST will result in a `fomabin` file being created.  An example of using that file is given below:
```
foma                                # run foma
load FST/generated/ojibwe.fomabin   # load the FST
up wiigwaas                         # input an inflected form -- as output, you should get an analysis
down wiigwaas+NI+SG                 # input an analysis -- as output, you should get an inflected form
quit                                # stop running foma
```

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
[`verbs.json`](https://github.com/ELF-Lab/OjibweMorph/blob/main/config/verbs.json)
in the [OjibweMorph](https://github.com/ELF-Lab/OjibweMorph)
repository for an example.

You need to specify the following parameters:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `comments`  | Comments. | `"This is a comment"` |
| `source_path` | Directory where source CSV files reside. | `"~/Documents/OjibweMorph/VerbSpreadsheets/"` |
| `regular_csv_files` | List of CSV files which contain **regular** paradigms (please omit `.csv` suffix) | `["VAI_IND","VTA_CNJ",...]` |
| `irregular_csv_files` | List of CSV files which contain **irregular** paradigms (please omit `.csv` suffix) | `["VAI_IRR"]` |
| `lexical_database` | External CSV lexical database file. | `"VERBS.csv"` |
| `regular_lexc_file` | Filename for generated lexc file containing **regular** paradigms. | `"ojibwe_verbs_regular.lexc"` | 
| `irregular_lexc_file` | Filename for generated lexc file containing **irregular** paradigms. | `"ojibwe_verbs_irregular.lexc"` | 
| `morph_features` | This field specifies the order in which morphological features are realized in FST output fields. The elements in the list have to match columns of the spurce CSV files. |  `["Paradigm", "Order", "Negation", "Mode", "Subject", "Object"]` |
| `missing_tag_marker` | Tag which indicates missing values of features in the source CSV files. E.g. intransitive verbs won't have an object, and this tag is used to mark that fact. | `"NA"` |
| `missing_form_marker` | Tag which indicates paradigm gaps | `"MISSING"` |
| `multichar_symbols` | List of multi-character symbols which are used in the source CSV files | `["i1", "w1"]` |
| `pre_element_tag` | A tag which is used to indicate the position of pre-elements like preverbs and prenouns in the lexc files | `"[PREVERB]"`|
|`pv_source_path`| This should point to your `PVSpreadsheets` directory | `"~/Documents/OjibweMorph/PVSpreadsheets/"` |
| `template_path`| Path to jinja2 templates.  Note that (for some reason) this file path **cannot** use a tilde symbol. | `"/Users/YourName/Documents/OjibweMorph/templates"` |

### The external lexical database

Additional lexemes are supplied in CSV files. For example, here are the first few rows of the [lexical database file of verbs](https://github.com/ELF-Lab/OjibweLexicon/blob/main/OPD/VERBS.csv) for Border Lakes Ojibwe, sourced from the [Ojibwe People's Dictionary](https://ojibwe.lib.umn.edu) (OPD): 

```
Lemma,Stem,Paradigm,Class,Translation,Source
aazhoogaadebi,aazhoogaadebi,VAI,VAI_V,NONE,https://ojibwe.lib.umn.edu/main-entry/aazhoogaadebi-vai
aayaazhoogaadebi,aayaazhoogaadebi,VAI,VAI_V,NONE,https://ojibwe.lib.umn.edu/main-entry/aazhoogaadebi-vai
aazhooshkaa,aazhooshkaa,VAI,VAI_VV,NONE,https://ojibwe.lib.umn.edu/main-entry/aazhooshkaa-vai
```

The lemma and stem must agree with the forms in the source spreadsheets where applicable (stored in `source_path` as specified above).

In the JSON configuration file, the path to the lexical database is supplied under the key `lexical_database`.
