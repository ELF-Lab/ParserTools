# csv2yaml

This directory houses the tools for converting CSV spreadsheets of lexical data to YAML files that can be used to test the performance of an FST.

## How to Run `create_yaml.py`

- Run the following, updating the arguments as needed:  
`python3 csv2yaml/create_yaml.py "~/OjibweMorph/VerbSpreadsheets/" "~/OjibweMorph/config/verbs.json" "csv2yaml/" --non-core-tags=Dub,Prt,PrtDub`
    - The first argument is the directory containing the .csv files that you want to convert ([example here](https://github.com/ELF-Lab/OjibweMorph/tree/main/VerbSpreadsheets)).
    - The second argument is the path to a .json configuration file, described [here](https://github.com/ELF-Lab/ParserTools/tree/dev/csv2fst#json-configuration-files).
    - The third argument is the output directory where the YAML files will be written to (in their own subdirectory).
    - The argument `--non-core-tags` is optional and specifies tags which should not be included in 'core' YAML test files like `VTA_IND-core.yaml`.
    - For more information on the arguments, check the argument help in `create_yaml.py`.
- Another example (running on a different POS):  
`python3 csv2yaml/create_yaml.py "~/OjibweMorph/NounSpreadsheets/" "~/OjibweMorph/config/nouns.json" "csv2yaml/" --pos=noun`
