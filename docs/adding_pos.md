# Example Use: Adding a New Part-of-Speech (POS)
The following outlines how to add support for a new POS to the FST, using the example of proper nouns being added to the Ojibwe FST.
1. Create a config file in the morphological source.
    - For example: create `proper_nouns.json` in `OjibweMorph/config/`.
    - You also need to make sure this config file is being given as a command-line argument to `csv2lexc.py`, but this was taken care of automatically by the `Makefile` in `OjibweMorph` which generates the list of config files based on the contents of `config/`.
    - Check out [the docs](morphological_source.md#configuration-files-json) for more info on what the config values mean.  Not all are necessary for basic functioning.
        - The following *must* be set and their values must be *correct*
            - `morphology_source_path`
            -`regular_csv_files`
            - `lexical_database`
            - `morph_features` (assuming you want the analysis to contain any info!)
        - The following *must* be set, but their value can really be anything -- just choose something specific to this POS:
            - `pos`
            - `root_lexicon`
            - `regular_lexc_file`
        - The following *must* be set, but you can just use the default/null value (described in the config docs):
            - `irregular_csv_files`
            - `irregular_lexc_file`
            - `missing_tag_marker`
            - `missing_form_marker`
            - `multichar_symbols`
            - `template_path`
2. Add the root name to the template for building `root.lexc`.
    - For example: add `ProperNounRoot` to the end of `OjibweMorph/templates/root.lexc.j2`.
3. Create a paradigm spreadsheet in the morphological source.
    - For example: create `PROPER_NOUN.csv` in one of the `OtherSpreadsheets/` folders in `OjibweMorph`.
    - There's more info in [the docs](morphological_source.md#morphological-paradigms-csv), but basically there are six mandatory columns for this spreadsheet: `Paradigm`, `Class`, `Lemma`, `Stem`, `Form1Surface`, and `Form1Split`.
    - There has to be at least one row for every possible paradigm and class value.
        - For example, there are two possibilities for proper nouns: paradigm and class being `PersonName`, or paradigm and class being `PlaceName`.  Therefore, there are two rows in `PROPER_NOUN.csv`.
4. Not required, but if you want the FST to handle more than a few cases, you'll need a spreadsheet in the lexical source.
    - For example: add `PROPER_NOUNS.csv` to `OjibweLexicon/OPD/`.
    - As outlined in [the docs](lexical_source.md), the six columns are mandatory (`Lemma`, `Stem`, `Paradigm`, `Class`, `Translation`, and `Source`), but only four require real values; `Translation` and `Source` can be `NONE`.