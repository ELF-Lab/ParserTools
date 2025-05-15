# csv2fst
This directory houses the tools for converting CSV spreadsheets of
language data to lexc files and a foma-based FST.  

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
