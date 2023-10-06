# csv2yaml

This will house the tools for converting csv spreadsheets of Ojibwe (and eventually, we hope, Algonquian languages more generally) to yaml files that can be used to test the performance of an FST.

## How to Run `create_yaml.py`
- Put all [the .csv files](https://github.com/ELF-Lab/BorderLakesMorph/tree/main/Spreadsheets) in the `csv2yaml` directory.  In this example, I've put them into a subdirectory called `spreadsheets`.
- Run the following (for more information on the arguments, check the argument help in `create_yaml.py`):  
`python3 csv2yaml/create_yaml.py "csv2yaml/spreadsheets/" "csv2yaml/"`
