from sys import stderr
import click
import json

from lexicon import Lexicon

@click.command()
@click.option('--config-file', required=True, help='JSON config file')
def main(config_file):
    print(f"Configure file {config_file}:", file=stderr)
    config = json.load(open(config_file))
    print(json.dumps(config, indent=2), file=stderr)

    # We'll first compile regular paradigms into a LEXC file 
    print(f"Reading spreadsheets from directory: {config['path']}", file=stderr)
    lexicon = Lexicon(config, regular=True)
    print(f"Writing lexc output to {config['regular_lexc_file']}", file=stderr)
    lexicon.print_lexc()

    # We'll then compile irregular paradigms into a different LEXC
    # file. These need to be separated because, later on, phonological
    # rules are only applied to regular paradigms.
    print(f"Reading spreadsheets for irregular paradigms from directory: {config['path']}", file=stderr)
    irregular_lexicon = Lexicon(config, regular=False)
    print(f"Writing lexc output to {config['irregular_lexc_file']}", file=stderr)
    irregular_lexicon.print_lexc()
    
if __name__=="__main__":
    main()
