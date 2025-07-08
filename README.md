# FSTmorph
This repository houses a set of language-neutral tools for converting CSVs to a finite-state transducer (FST), as well as for testing that FST via YAML files.

## Contents
- [User Instructions](#user-instructions)
    - [Installation](#installation)
    - [Using FSTmorph](#using-fstmorph)
- [The `csv2lexc.py` script](#the-csv2lexcpy-script)
    - [The external lexical database](#the-external-lexical-database)
- [Citation](#citation)

## User Instructions
#### Installation
This package can be installed via pip:  
`pip install fstmorph`

The distribution files can also be downloaded directly from the `dist/` folder.

#### Using FSTmorph
A thorough example of how to use this package is given in [OjibweMorph](https://github.com/ELF-Lab/OjibweMorph), outlining how to build, test, and use an FST in Ojibwe using FSTmorph.  The [Makefile](https://github.com/ELF-Lab/OjibweMorph/blob/main/Makefile) there outlines how the code in this repo is utilized.

That said, this FST-generating code is intended to be applicable for other Algonquian languages and beyond -- if you have the necessary spreadsheets for your target language, it should be compatible with this code!

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

## Citation
To cite this work or the contents of the repository in an academic work, please use the following:

> [Hammerly, C., Livesay, N., Arppe A., Stacey, A., & Silfverberg, M. (Submitted) OjibweMorph: An approachable morphological parser for Ojibwe](https://christopherhammerly.com/publication/ojibwemorph/OjibweMorph.pdf)
