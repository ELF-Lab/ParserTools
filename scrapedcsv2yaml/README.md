# scrapedcsv2yaml


## How to Run `create_yaml_from_scraped.py`
- Put [the scraped .csv file](https://github.com/ELF-Lab/BorderLakesMorph/blob/main/Database/inflectional_forms.csv) in the `scrapedcsv2yaml` directory.  
- Run the following (from the parent `ParserTools` directory) (for more information on the arguments, check the argument help in `create_yaml_from_scraped.py`):  
`python3 csv2yaml/create_yaml_from_scraped.py "scrapedcsv2yaml/inflectional_forms.csv" "scrapedcsv2yaml/"`