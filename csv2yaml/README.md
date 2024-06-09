# csv2yaml

This will house the tools for converting csv spreadsheets of Ojibwe (and eventually, we hope, Algonquian languages more generally) to yaml files that can be used to test the performance of an FST.

## How to Run `create_yaml.py`
- The first argument of `create_yaml.py` is the directory containing the .csv files that you want to convert ((example here)[https://github.com/ELF-Lab/OjibweMorph/tree/main/VerbSpreadsheets]).
- Run the following (for more information on the arguments, check the argument help in `create_yaml.py`):  
`python3 csv2yaml/create_yaml.py "/VerbSpreadsheets/" "csv2yaml/" --non-core-tags=Dub,Prt,PrtDub`
- The argument `--non-core-tags` specifies tags which should not be included in core YAML test files like `VTA_IND-core.yaml`.
