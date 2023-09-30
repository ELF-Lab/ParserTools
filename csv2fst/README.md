# csv2fst

This directory houses the tools for converting csv spreadsheets of Ojibwe (and eventually, we hope, Algonquian languages more generally) to lexc files that can be used to compile a foma-based FST.

## Dependencies

The project requires the foma compiler and flookup program. Install them using these [instructions](https://blogs.cornell.edu/finitestatecompling/2016/08/24/installing-foma/) or using [homebrew](https://formulae.brew.sh/formula/foma).

To install python library requirements, run:
```
pip3 install -r requirements.txt
```

In order to build the FST, you will need to get a clone of the
BorderLakesMorph
[repository](https://github.com/ELF-Lab/BorderLakesMorph) which
contains all the source data for the FST model.

If you want to run YAML tests, you will also need to install the [giella-core](https://github.com/giellalt/giella-core) repository.

## Building the Ojibwe FST

The Makefile requires some modifications:

1. Modify the `CSVDIR` path so that it points to your `BorderLakesMorph/Spreadsheets` directory.
2. Modify the `OPDDATABASE` so that it points to your `BorderLakesMorph/Database/main_entries-VERBS_fields-lemma-stem-POS.csv` file.
3. Modify `FSTSCRIPT` so that it points to your `BorderLakesMorph/xfst/phonology.xfst` file

After setting all paths, you should be able to run `make all` to build
the FST. This will create a directory `generated` which contains the
FST, lexc files and XFST rules.

## Running YAML test

The Makefile requires some modifications:

1. You may potentially need to modify the `MORPHTEST` variable to
point to your copy of the `morph-test.py` script (you might not need
to do anything if you have installed `giella-core`).

You should not be able to run `make all` and `make check`.
