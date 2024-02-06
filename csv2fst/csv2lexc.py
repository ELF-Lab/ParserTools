from sys import stderr
import click
import json

from lexicon import Lexicon

@click.command()
@click.option('--config-file', required=True, help="JSON config file")
@click.option('--lexc-path', required=True,
              help="Directory where output lexc files are stored")
@click.option('--read-lexical-database', required=False, default=True,
              help="Whether to include lexemes from an external lexicon database")
def main(config_file,lexc_path,read_lexical_database):
    print(f"Configure file {config_file}:", file=stderr)
    config = json.load(open(config_file))
    print(json.dumps(config, indent=2), file=stderr)

    # We'll first compile regular paradigms into a LEXC file 
    print(f"Reading spreadsheets from directory: {config['source_path']}", file=stderr)
    lexicon = Lexicon(config, lexc_path, read_lexical_database, regular=True)
    print(f"Writing lexc output to {config['regular_lexc_file']}", file=stderr)
    lexicon.print_lexc()

    # We'll then compile irregular paradigms into a different LEXC
    # file. These need to be separated because, later on, phonological
    # rules are only applied to regular paradigms.
    print(f"Reading spreadsheets for irregular paradigms from directory:",
          "{config['source_path']}", file=stderr)
    irregular_lexicon = Lexicon(config,
                                lexc_path,
                                read_lexical_database=False,
                                regular=False)
    print(f"Writing lexc output to {config['irregular_lexc_file']}", file=stderr)
    irregular_lexicon.print_lexc()
    
if __name__=="__main__":
    main()
