# yaml_tests
This directory houses the tools for converting CSV spreadsheets of lexical data to YAML files that can be used to test the performance of an FST.

## How to Run `create_yaml.py`
- Run the following, updating the arguments as needed:  
`python3 yaml_tests/create_yaml.py "~/OjibweMorph/VerbSpreadsheets/" "~/OjibweMorph/config/verbs.json" "yaml_tests/" --non-core-tags=Dub,Prt,PrtDub`
    - The first argument is the directory containing the .csv files that you want to convert ([example here](https://github.com/ELF-Lab/OjibweMorph/tree/main/VerbSpreadsheets)).
    - The second argument is the path to a .json configuration file, described [here](https://github.com/ELF-Lab/ParserTools/tree/dev/csv2fst#json-configuration-files).
    - The third argument is the output directory where the YAML files will be written to (in their own subdirectory).
    - The argument `--non-core-tags` is optional and specifies tags which should not be included in 'core' YAML test files like `VTA_IND-core.yaml`.
    - For more information on the arguments, check the argument help in `create_yaml.py`.
- Another example (running on a different POS):  
`python3 yaml_tests/create_yaml.py "~/OjibweMorph/NounSpreadsheets/" "~/OjibweMorph/config/nouns.json" "yaml_tests/" --pos=noun`

## How to Run `run_yaml_tests.py`
As mentioned in the main README, this script comes from [giella-core](https://github.com/giellalt/giella-core)'s `morph-test.py`, just adapted to print .log files with information more relevant here.
- Run the following, updating the arguments as needed:  
`python3 run_yaml_tests.py --app flookup --surface --mor ../../OjibweMorph/FST/check-generated/ojibwe.fomabin ../../OjibweMorph/FST/paradigm_yaml_output/NA_C.yaml`
    - The first filepath argument is the location of the FST being tested.
    - The second filepath argument contains the YAML file with the forms the FST is being tested on.

## How to Run `summarize_tests.py`
- Run the following, updating the arguments as needed:  
`python3 summarize_tests.py --input_file_name ../../OjibweMorph/FST/paradigm-test.log --yaml_source_csv_dir ../../OjibweMorph/VerbSpreadsheets --paradigm_map_path ../../OjibweLexicon/resources/VERBS_paradigm_map.csv --output_dir . --output_file_identifier "paradigm"`
    - The `input_file_name` argument is the path to the test output file we are summarizing.
    - The `yaml_source_csv_dir` argument is the path to the dir containing the YAML used to create the tests.  This is included because if you run this script and use it to generate additional files, such as a list of forms with no analyses whatsoever (this is currently done by altering boolean values at the top of the script), it will include additional information about those forms which it searches the CSV to find (because that info is not included in the YAML files themselves).
    - The `paradigm_map_path` argument is the filepath to the relevant paradigm map file.  This is basically just used as a list of all possible **classes**, which are used as categories in the summary CSV.
    - The `output_dir` argument is the path to the directory where the summary CSV will be written.
    - The `output_file_identifier` is a string that acts as an ID for these tests.  It will be included in the filename for the summary CSV.  This is used so that you can run mulitple sets of tests and generate multiple corresponding summary CSVs with clear names.
