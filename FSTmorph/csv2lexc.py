"""Script for compiling a set of lexc files from the following resources:

   * CSV files representing inflection tables (these live in `source_path`)
   * Lexical database files in CSV format (these live in `database_paths`)
   * Configuration files for different word classes (these live in `source_path`/config)

   `config_files` is a comma-separated list of .json configuration file names read from
    the directory `source_path`/config

   `source_path` gives the path the directory containing morphological information,
   plus phonological rules.  An example for Ojibwe is OjibweMorph.

   `database_paths` gives the path to 1+ directories where CSVs containing lexical information
   (lemmas/stems) are stored.  An example for Ojibwe would be OjibweLexicon/OPD.

   The output lexc files root.lexc, languagename_POS.lexc (for each word class POS) and potentially
   preverbs.lexc and/or prenouns.lexc will be written into the directory `lexc_path`.

   The boolean parameter `read_lexical_database` determines whether we're including the lexical 
   entries from the database.

   To compile the lexc files, you can use the unix command `cat` to combine them into a file
   all.lexc. The file root.lexc should be at the top of all.lexc. Apart from that, order doesn't
   matter when concatenating.
"""

import click
import json
from os.path import join as pjoin

from fstmorph.src.lexicon import LexcFile
from fstmorph.src.templates import render_pre_element_lexicon, render_root_lexicon
from fstmorph.src.log import set_verbose, info

# Can be imported into other scripts, or called from the command line via main()
def csv2lexc(config_files, source_path, lexc_path, database_paths, lexical_data_to_exclude, read_lexical_database, add_derivations, alt_tag, verbose):
    set_verbose(verbose)
    if verbose:
        info("Compiling in verbose mode. Omit --verbose to disable.")
    else:
        info("Compiling in non-verbose mode. For more detailed diagnostics, use option --verbose=True.")
    config_files = config_files.split(",")
    info(f"Got {len(config_files)} configuration files: {', '.join(config_files)}")
    database_paths = database_paths.split(",")

    # Collect POS root lexicons like NounRoot and VerbRoot. We need to
    # refer to these from root.lexc
    pos_root_lexicons = set()
    for config_file in config_files:
        info(f"Processing configuration file {config_file}:")
        config = json.load(open(config_file))
        config["database_src_dirs"] = database_paths
        config["append_alt_tag"] = alt_tag
        info(json.dumps(config, indent=2),force=False)
        pos_root_lexicons.add(config["root_lexicon"])
        
        # We'll first compile regular paradigms into a LEXC file 
        info("Reading spreadsheets for regular paradigms from directory:",
             f"{pjoin(source_path,config['morphology_source_path'])}")
        lexicon = LexcFile(config,
                           source_path,
                           lexc_path,
                           database_paths,
                           lexical_data_to_exclude,
                           read_lexical_database,
                           add_derivations,
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
            irregular_lexicon = LexcFile(config,
                                         source_path,
                                         lexc_path,
                                         database_paths,
                                         lexical_data_to_exclude,
                                         read_lexical_database=False,
                                         add_derivations=False,
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

@click.command()
@click.option('--config-files', required=True, help="JSON config files separated by commas. E.g. verb_conf.json, noun_conf.json")
@click.option('--source-path', required=True, help="Path to the source files for the FST (e.g. your OjibweMorph directory)")
@click.option('--database-paths', required=False, help="Path to lexical database directory for lemmas.  Can be multiple file paths separated by commas.")
@click.option('--lexical-data-to-exclude', required=False, default=None, help="Data from database-paths that should NOT be included in the FST")
@click.option('--lexc-path', required=True,
              help="Directory where output lexc files are stored")
@click.option('--read-lexical-database', required=False, default=True,
              help="Whether to include lexemes from an external lexicon database")
@click.option('--add-derivations', required=True,
              help="Whether to include derivational morphology")
@click.option('--alt-tag', required=False, default=False,
              help="If this option is enabled, a \"+Alt\" tag is appended to \"non-standard\" analyses")
@click.option('--verbose', required=False, default=False,
              help="Print very detailed diagnostics")
def main(config_files, source_path, lexc_path, database_paths, lexical_data_to_exclude, read_lexical_database, add_derivations, alt_tag, verbose):
    csv2lexc(config_files, source_path, lexc_path, database_paths, lexical_data_to_exclude, read_lexical_database, add_derivations, alt_tag, verbose)

if __name__=="__main__":
    main()
