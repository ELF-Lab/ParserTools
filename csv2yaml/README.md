# csv2yaml

This will house the tools for converting csv spreadsheets of Ojibwe (and eventually, we hope, Algonquian languages more generally) to yaml files that can be used to test the performance of an FST.

## How to Run `create_yaml.py`
- Put all [the .csv files](https://github.com/ELF-Lab/BorderLakesMorph/tree/main/Spreadsheets) in the `csv2yaml` directory
- Run the script once for each type of file
    - e.g. `python3 csv2yaml/create_yaml.py --vii "csv2yaml/VII_CNJ.csv"`
    - e.g. `python3 csv2yaml/create_yaml.py --vai "csv2yaml/VAI_CNJ.csv"`
    - etc.