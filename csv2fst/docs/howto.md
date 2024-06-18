# Installation and running scripts

## Compilation of the FST using the `Makefile`

Compilation depends on three repos: OjibweMorph, OPDDatabase and ParserTools. These need to be cloned:

```
$ git clone git@github.com:ELF-Lab/OjibweMorph.git
$ git clone git@github.com:ELF-Lab/OPDDatabase.git
$ git clone git@github.com:ELF-Lab/ParserTools.git 
```

You then need to build the lexical database in OPDDatabase. Remember to also install python library requirements:

```
$ cd OPDDatabase
$ pip3 install -r requirements.txt
$ make
$ cd ..
```

`make` will print a lot of information about the compilation process. You may want to keep track of how many skipped OPD entries there are for nouns, verbs and all other word classes. The number of skipped entries for nouns and verbs should be < 100 each (37 skipped lexemes for nouns and 56 for verbs when Miikka built on 2024/06/18). For other word classes, there should be no skipped entries. 

Then you need to run `make` in ParserTools, which builds the FST in the directors ParserTools/csv2fst/generated. Remember to also install python library requirements. Before you run make, you will need to edit two Makefile variables:

* `MORPHOLOGYSRCDIR` which should point to your OjibweMorph clone.
* `DATABASEDIR` which should point to your OPDDatabase clone

```
$ cd ParserTools/csv2fst
$ pip3 install -r requirements.txt
$ make
```

You can then test the FST by loading it from the directory `generated` using foma:

```
$ foma

Foma, version 0.10.0
Copyright © 2008-2021 Mans Hulden
This is free software; see the source code for copying conditions.
There is ABSOLUTELY NO WARRANTY; for details, type "help license"

Type "help" to list all commands available.
Type "help <topic>" or help "<operator>" for further help.

foma[0]: load generated/ojibwe.fomabin
5.2 MB. 153690 states, 336756 arcs, Cyclic.
foma[1]: up waabam
waabam+VTA+Imp+Sim+2SgSubj+3SgProxObj
waabam+VTA+Imp+Sim+2SgSubj+3PlProxObj
```

## Optional: Running tests using the `Makefile`

ParserTools offers automated tests to ensure that the FST has been compiled correctly. These are dependent on external scripts by the [Giellatekno project](https://giellatekno.uit.no/index.eng.html). Note that **tests are not a requirement for building and running the FST**.

If you want to run YAML tests, you will need to install the
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

Additionally, `Makefile` requires modifications. You may potentially need to modify the `MORPHTEST` variable to point to your copy of the Giellatekno script `morph-test.py` (you might not need to do anything if you have installed `giella-core`).

You should now be able to run `make check`. This will generate three log files:

* `yaml-test.log` (tests for the subset of the Ojibwe morphology which we currently understand well)
* `core-yaml-test.log` (there is more uncertainty and dialectal variation in the tests)
* `opd-test.log` (these tests check integration of an external lexical resource)

The first two log files should show very few failures (5-15 fails per file). The third one test coverage on exampke forms from the Ojibwe People's Dictionary and will contain more failures.

## The `ParserTools/csv2fst/csv2lexc.py` script

How to compile lexc-files (for nouns and verbs) using `csv2lexc.py`:

```
# OjibweMorph and OPDDatabase (or a different set of morphological paradigms and another lexical database)
# are required for compilation
$ export MORPHOLOGY_DIR=/path/to/OjibweMorph
$ export LEXICAL_DIR=/path/to/OPDDatabase

$ python3 csv2lexc.py --config-files $MORPHOLOGY_DIR/config/ojibwe_nouns.json,$MORPHOLOGY_DIR/config/ojibwe_verbs.json \
                      --source-path  $MORPHOLOGY_DIR \
                      --database-path $LEXICAL_DIR \
                      --lexc-path generated_lexc_code \
                      --read-lexical-database True
```

Depending on how you've defined the configuration files, the command might generate the following files in the directory `generated_lexc_code`:

```
ojibwe_irregular_verbs.lexc   # Irregular verbs
ojibwe_nouns.lexc             # Nouns
ojibwe_verbs.lexc             # Verbs
preverbs.lexc                 # Preverbs
prenouns.lexc                 # Prenouns
root.lexc                     # The root lexicon file contains Multicharacter_Symbols and LEXICON Root
```

Description of required command-line arguments for `csv2lexc.py`:

| Argument | Description |
|----------|-------------|
| `config-files` | Comma-separated list of configuration files for lexc compilation. One is required for each word class (string) |
| `source-path` | Path to OjibweMorph or another morphological paradigm repository (string) |
| `database-path` | Path to OPDDatabase or another lexical database (string) |
| `lexc-path` | Target directory for generated lexc files (string) |
| `read-lexical-database` | Whether to include lexemes from database (True|False) |

## The `ParserTools/csv2fst/assets/compile_fst.xfst` script

ParserTools contains a convenient script `ParserTools/csv2fst/assets/compile_fst.xfst` for compiling an FST from lexc and xsft files. To use the script, you will first need to combine the lexc-files into a master lexc-file. This is done using the UNIX `cat` command. Note that you will need to retain the name `all.lexc`:

```
$ cd generated_lexc_code

# You can cat the files in almost any order but root.lexc always needs to be the first lexicon file. 
$ cat root.lexc prenouns.lexc preverbs.lexc ojibwe_verbs.lexc ojibwe_nouns.lexc ojibwe_irregular_verbs.lexc > all.lexc
```

You then need to copy over the xfst rule script from `OjibweMorph/xfst` and `compile_fst.xsft` from `ParserTools/csv2fst/assets/`:

```
$ export MORPHOLOGY_DIR=/path/to/OjibweMorph
$ export PARSER_TOOLS=/path/to/ParserTools

$ cp $MORPHOLOGY_DIR=/xfst/phonology.xfst .
$ cp $PARSER_TOOLS/asssets/compile_fst.xfst .

foma -f compile_fst.xfst
```

This generates two output files: 

* a binary FST file `ojibwe.fomabin`, and
* an FST file in ATT text format `ojibwe.att`

You can read either of these into foma to test them:

```
Testing ojibwe.fomabin:

$ foma

Foma, version 0.10.0
Copyright © 2008-2021 Mans Hulden
This is free software; see the source code for copying conditions.
There is ABSOLUTELY NO WARRANTY; for details, type "help license"

Type "help" to list all commands available.
Type "help <topic>" or help "<operator>" for further help.

foma[0]: load ojibwe.fomabin 
5.1 MB. 151484 states, 332934 arcs, Cyclic.
foma[1]: up waabam
waabam+VTA+Imp+Sim+2SgSubj+3SgProxObj
waabam+VTA+Imp+Sim+2SgSubj+3PlProxObj
```

```
Testing ojibwe.att:

$ foma

Foma, version 0.10.0
Copyright © 2008-2021 Mans Hulden
This is free software; see the source code for copying conditions.
There is ABSOLUTELY NO WARRANTY; for details, type "help license"

Type "help" to list all commands available.
Type "help <topic>" or help "<operator>" for further help.

foma[0]: read att ojibwe.att 
Reading AT&T file: ojibwe.att
5.1 MB. 151484 states, 332934 arcs, Cyclic.
foma[1]: up waabam
waabam+VTA+Imp+Sim+2SgSubj+3PlProxObj
waabam+VTA+Imp+Sim+2SgSubj+3SgProxObj
```
