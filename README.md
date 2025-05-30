# ParserTools
This repository houses a set of language-neutral tools for converting CSVs to a finite-state transducer (FST), as well as for testing that FST via YAML files.

## Contents
- [User Instructions](#user-instructions)
    - [Getting set up to build the FST](#getting-set-up-to-build-the-fst)
    - [Building the FST](#building-the-fst)
    - [Running the YAML tests](#running-the-yaml-tests)
- [Citation](#citation)

## User Instructions
Examples are given for Ojibwe, with the relevant language data accessible in other repos.  However, this FST-generating code is intended to be applicable for other Algonquian languages and beyond -- if you have the necessary spreadsheets for your target language, it should be compatible with this code!

### Getting set up to build the FST
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

If you're working towards building the example FST for Ojibwe, once you're done with installing these prerequisites, carry on with the instructions in [OjibweMorph](https://github.com/ELF-Lab/OjibweMorph#building-the-fst).  But make sure you keep the virtual environment you set up here up and running!
- Just change directories so that you end up back in your local copy of OjibweMorph, ready to run commands there, with this virtual environment still active.  For example, if you installed OjibweMorph and ParserTools in the same directory, just use the command `cd ../..OjibweMorph/` (because you're currently in `ParserTools/csv2fst/`).
- If you get a `ModuleNotFoundError` when running commands in OjibweMorph, it may be that you are no longer in the virtual environment (and so the modules installed in the virtual environment are not accessible).
- You can always check that the name of the virtual environment still appears in your command line prompt to know if it is active.

### Building the FST
The FST is built using a Makefile.  Before building, there are three variables within the Makefile which must be set to point to the right directory locations:  
- `MORPHOLOGYSRCDIR` points to a directory that contains most of the morphological information needed to build the FST.  The example directory (for Border Lakes Ojibwe) is [OjibweMorph](https://github.com/ELF-Lab/OjibweMorph).
- `LEMMAS_DIR` points to a directory that contains CSVs listing all the lemmas that will be used to build the FST.  An example directory (for Border Lakes Ojibwe) is [OjibweLexicon/OPD](https://github.com/ELF-Lab/OjibweLexicon/tree/main/OPD).
    - This variable can also be set to a list of directories (each containing CSVs to be used), separated by a comma. 
- `OUTPUT_DIR` points to the directory where all files generated will go.  Note that in order for the testing code to work (i.e., when running `make check`), this **must be a relative path** (for some reason).

You should go into the Makefile and edit the values of these variables so that the correct directory is specified.  Once complete, you can run `make all` (or just `make`) to build the FST (e.g., `ojibwe.fomabin`). This will create a directory `generated` which contains the FST, lexc files and XFST rules.  Once complete, you can use the FST -- check [here](https://github.com/ELF-Lab/OjibweMorph?tab=readme-ov-file#using-the-fst) for an example.

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

### Running the YAML Tests
The code for running tests based on the generated YAML files comes from [giella-core](https://github.com/giellalt/giella-core).  A version of their `morph-test.py` script is included in this repo, modified to customize the .log output format.

Run the tests with `make check`. This will generate three log files:
* `paradigm-test.log`: A smaller set of tests covering the noun and verb spreadsheets in `OjibweMorph`.
* `opd-test.log`: A larger set of tests covering an external lexical resource, [the OPD](https://ojibwe.lib.umn.edu).

## Citation
To cite this work or the contents of the repository in an academic work, please use the following:

> [Hammerly, C., Livesay, N., Arppe A., Stacey, A., & Silfverberg, M. (Submitted) OjibweMorph: An approachable morphological parser for Ojibwe](https://christopherhammerly.com/publication/ojibwemorph/OjibweMorph.pdf)
