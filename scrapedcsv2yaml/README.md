# scrapedcsv2yaml


## How to Run `create_yaml_from_scraped.py`
- Clone the BorderLakesMorph repo (or just make sure you have [the scraped .csv file](https://github.com/ELF-Lab/BorderLakesMorph/blob/main/Database/inflectional_forms.csv) downloaded somewhere).  
- Run the following (from the parent `ParserTools` directory) to create the formatted csv (for more information on the arguments, check the argument help in `create_yaml_from_scraped.py`):  
`python3 scrapedcsv2yaml/create_csv_from_scraped.py "~/BorderLakesMorph/Database/inflectional_forms.csv" "scrapedcsv2yaml/subj_obj_tags.csv" "scrapedcsv2yaml/csv_output/"`
- Then to generate the yaml, run:  
`python3 csv2yaml/create_yaml.py "scrapedcsv2yaml/csv_output/" "scrapedcsv2yaml/"`