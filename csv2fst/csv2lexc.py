import click
import json
from os.path import join as pjoin

from lexicon import Lexicon
from templates import render_pre_element_lexicon, render_root_lexicon
from log import info
from paradigm_slot import ParadigmSlot

@click.command()
@click.option('--config-files', required=True, help="JSON config files separated by commas. E.g. verb_conf.json,noun_conf.json")
@click.option('--source-path', required=True, help="Path to the source files for the FST (e.g. your BorderLakesMorph directory)")
@click.option('--database-path', required=False, default="", help="Path to lexical database directory")
@click.option('--lexc-path', required=True,
              help="Directory where output lexc files are stored")
@click.option('--read-lexical-database', required=False, default=True,
              help="Whether to include lexemes from an external lexicon database")
def main(config_files,source_path,lexc_path,database_path,read_lexical_database):
    config_files = config_files.split(",")
    info(f"Got {len(config_files)} configuration files: {', '.join(config_files)}")

    # Collect POS root lexicons like NounRoot and VerbRoot. We need to
    # refer to these from root.lexc
    pos_root_lexicons = set()
    for config_file in config_files:
        info(f"Processing configuration file {config_file}:")
        config = json.load(open(config_file))
        info(json.dumps(config, indent=2))
        pos_root_lexicons.add(config["root_lexicon"])
        
        # We'll first compile regular paradigms into a LEXC file 
        info("Reading spreadsheets for regular paradigms from directory:",
             f"{pjoin(source_path,config['morphology_source_path'])}")
        lexicon = Lexicon(config,
                          source_path,
                          lexc_path,
                          database_path,
                          read_lexical_database,
                          regular=True)
        info(f"Writing lexc output to {config['regular_lexc_file']}")
        lexicon.write_lexc()

        # We'll then compile irregular paradigms into a different LEXC
        # file. These need to be separated because, later on, phonological
        # rules are only applied to regular paradigms.
        if config['irregular_lexc_file'] != "None":
            info("Reading spreadsheets for irregular paradigms from directory:",
                 f"{pjoin(source_path,config['morphology_source_path'])}")
            config["root_lexicon"] += "Irregular"
            pos_root_lexicons.add(config["root_lexicon"])
            irregular_lexicon = Lexicon(config,
                                        source_path,
                                        lexc_path,
                                        database_path,
                                        read_lexical_database=False,
                                        regular=False)
            info(f"Writing lexc output to {config['irregular_lexc_file']}")
            irregular_lexicon.write_lexc()

        if config["template_path"] != "None":
            info("Reading prefix template file from:",
                 f"{config['template_path']}")
            info("Reading prefix spreadsheets from directory:",
                 f"{config['pv_source_path']}")
            info(f"Writing lexc output to directory {lexc_path}")
            pos_root_lexicons.add(config["prefix_root"])
            render_pre_element_lexicon(config,source_path,lexc_path)
            
    render_root_lexicon(pjoin(source_path,"templates","root.lexc.j2"),
                        lexc_path)
#    Lexicon.write_root_lexc(pjoin(lexc_path,"root.lexc"), pos_root_lexicons)

if __name__=="__main__":
    main()
