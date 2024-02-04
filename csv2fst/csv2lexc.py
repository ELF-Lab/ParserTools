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
    print(f"Reading spreadsheets from directory: {config['path']}", file=stderr)
    lexicon = Lexicon(config)
    print(f"Writing lexc output to {config['lexc_file']}", file=stderr)
    lexicon.print_lexc()
    
if __name__=="__main__":
    main()
