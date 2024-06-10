# csv2yaml

This will house the tools for converting csv spreadsheets of Ojibwe (and eventually, we hope, Algonquian languages more generally) to yaml files that can be used to test the performance of an FST.

## How to Run `create_yaml.py`

- Run the following, replacing `/VerbSpreadsheets/` with the appropriate directory on your system:  
`python3 csv2yaml/create_yaml.py "/VerbSpreadsheets/" "csv2yaml/" --non-core-tags=Dub,Prt,PrtDub`
    - The first argument is the directory containing the .csv files that you want to convert ([example here](https://github.com/ELF-Lab/OjibweMorph/tree/main/VerbSpreadsheets)).
    - The argument `--non-core-tags` specifies tags which should not be included in core YAML test files like `VTA_IND-core.yaml`.
    - For more information on the arguments, check the argument help in `create_yaml.py`.