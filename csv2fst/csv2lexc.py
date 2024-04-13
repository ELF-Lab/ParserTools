import click
import json

from lexicon import Lexicon
from templates import render_pv_lexicon
from log import info

@click.command()
@click.option('--config-file', required=True, help="JSON config file")
@click.option('--lexc-path', required=True,
              help="Directory where output lexc files are stored")
@click.option('--read-lexical-database', required=False, default=True,
              help="Whether to include lexemes from an external lexicon database")
def main(config_file,lexc_path,read_lexical_database):
    info(f"Configure file {config_file}:")
    config = json.load(open(config_file))
    info(json.dumps(config, indent=2))

    # We'll first compile regular paradigms into a LEXC file 
    info("Reading spreadsheets for regular paradigms from directory:",
         f"{config['source_path']}")
    lexicon = Lexicon(config,
                      lexc_path,
                      read_lexical_database,
                      regular=True)
    info(f"Writing lexc output to {config['regular_lexc_file']}")
    lexicon.write_lexc()

    # We'll then compile irregular paradigms into a different LEXC
    # file. These need to be separated because, later on, phonological
    # rules are only applied to regular paradigms.
    info("Reading spreadsheets for irregular paradigms from directory:",
         f"{config['source_path']}")
    irregular_lexicon = Lexicon(config,
                                lexc_path,
                                read_lexical_database=False,
                                regular=False)
    info(f"Writing lexc output to {config['irregular_lexc_file']}")
    irregular_lexicon.write_lexc()

    info("Reading preverb template file from directory:",
         f"{config['template_path']}")
    info("Reading preverb spreadsheets from directory:",
         f"{config['pv_source_path']}")
    info(f"Writing lexc output to directory {lexc_path}")
    render_pv_lexicon(config,lexc_path)
    
if __name__=="__main__":
    main()
