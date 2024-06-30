# scrapedcsv2yaml
This code was created to convert scraped OPD data into a spreadsheet with more standard formatting, which can then have the `csv2yaml` code run on it to produce yaml output.

## How to Run `create_yaml_from_scraped.py`
- Run the following to create the formatted csv:   
`python3 scrapedcsv2yaml/create_csv_from_scraped.py "../OPDDatabase/data/full_batch_lemma.json" "scrapedcsv2yaml/subj_obj_tags.csv" "scrapedcsv2yaml/csv_output/"`
    - The first argument refers to the csv that is being converted and should be modified to match its location on your system.
    - For more information on the arguments, check the argument help in `create_yaml_from_scraped.py`.
- Then to generate the yaml, run:  
`python3 csv2yaml/create_yaml.py "scrapedcsv2yaml/csv_output/" "scrapedcsv2yaml/"`