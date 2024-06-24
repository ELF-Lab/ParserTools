"""Class for representing a lexc file."""

import pandas as pd
import os
from os.path import join as pjoin
import re

from lexc_path import LexcPath, entry2str, LexcEntry, escape
from log import info, warn
from lexc_comment import comment_block

class Lexicon:
    @staticmethod
    def write_multichar_symbols(multichar_symbol_set, lexc_file):
        """Write the `Multichar_Symbols` section into a lexc_file"""
        print("Multichar_Symbols",file=lexc_file)
        multichar_symbols = sorted(list(multichar_symbol_set))
        print(" ".join(multichar_symbols), file=lexc_file)
        print("", file=lexc_file)

    @staticmethod
    def write_root_lexc(root_lexc_filename,pos_root_lexicons):
        """Write the `LEXICON Root` into a lexc_file. Each POS has their own
           custom root lexicon (e.g. VerbRoot and NounRoot) which the
           master root lexicon needs to reference.

        """
        with open(root_lexc_filename,"w") as root_lexc_file:
            Lexicon.write_multichar_symbols(LexcPath.multichar_symbols,
                                            root_lexc_file)
            print("LEXICON Root", file=root_lexc_file)
            for lexicon_name in pos_root_lexicons:
                print(f"{lexicon_name} ;", file=root_lexc_file)
            print("", file=root_lexc_file)
        
    def __init__(self,
                 conf:dict,
                 source_path:str,
                 lexc_path:str,
                 database_path:str,
                 read_lexical_database:bool,
                 regular:bool):
        """Initialize the lexicon using a configuration file. Parameters: 
           * `conf` configuration 
           * `source_path` path to OjibweMorph repo
           * `lexc_path` destination directory for lexc code
           * `database_path` path to OPDDatabase
           * `read_lexical_database` whether to include lexemes from database 
           * `regular` whether this is a lexc file for regular or irregular lexemes 
        """
        self.conf = conf
        self.root_lexicon = conf["root_lexicon"]
        self.source_path = source_path        
        self.lexc_path = lexc_path
        self.regular = regular
        self.lexicons = {self.root_lexicon:set()}
        LexcPath.update_multichar_symbol_set(self.conf)
        
        csv_names = conf["regular_csv_files" if regular else "irregular_csv_files"]
        for name in csv_names:
            csv_file = os.path.join(os.path.join(self.source_path,
                                                 conf["morphology_source_path"]), f"{name}.csv")
            info(f"Reading lexicon entries from {csv_file}")
            table = pd.read_csv(csv_file, keep_default_na=False)
            for _, row in table.iterrows():
                lexc_path = LexcPath(row, conf, regular)
                lexc_path.extend_lexicons(self.lexicons)

        if read_lexical_database:
            self.read_lexemes_from_database(database_path)
            
    def read_lexemes_from_database(self, database_path) -> None:
        """Read OPD dictionary entries from an external CSV file given by the
        "lexical_database" field in the configuration file. The CVS is
        located in the directory given by database_path

        This function maps OPD POS tags like vti3 to inflectional
        classes like BorderLakesMorph VTI_i. It then adds each the OPD
        lexical entry into the appropriate lexc sublexicon (like
        VTI:Stems) with an appropriate continuation lexicon (like
        VTI:Class=VTI_i:Boundary).

        The mapping from OPD POS tags to BorderLakesMorph inflectional
        classes is based on a mapping CSV file. This file is specified
        in the "class_map" field in the configuration file.

        """
        
        info(f"Reading external lexical database {self.conf['lexical_database']} from directory {database_path}\n")
        if self.conf["lexical_database"] != "None":
            lexeme_database = pd.read_csv(os.path.join(database_path,
                                                       self.conf["lexical_database"]),
                                          keep_default_na=False)
            skipped = 0
            for _, row in lexeme_database.iterrows():
                try:
                    klass = row.Class
                    paradigm = row.Paradigm
                    self.lexicons[f"{paradigm}_Stems"].add(
                        LexcEntry(f"{paradigm}_Stems",
                                  escape(row.Lemma),
                                  escape(row.Stem),
                                  f"{paradigm}_Class={klass}_Boundary"))
                except ValueError as e:
                    warn(e)
                    skipped += 1
            info(f"Checked {len(lexeme_database)} lexical entries.\n",
                 f"Added {len(lexeme_database) - skipped} entries to lexc file.\n",
                 f"Skipped {skipped} invalid ones")

    def write_lexc(self) -> None:
        """Write contents to lexc file. If this is a regular lexc file, write
           to the file given by the field "regular_lexc_file" in the
           configuration file. Otherwise, write to the file given by
           "irregular_lexc_file".
        """
        
        lexc_fn = os.path.join(self.lexc_path,
                               self.conf["regular_lexc_file" if self.regular
                                         else "irregular_lexc_file"])
        lexc_file = open(lexc_fn,"w")
        info(f"Writing {len(self.lexicons)} sublexicons:")
        for lexicon in self.lexicons:            
            lexc_rows = sorted(list(self.lexicons[lexicon]))
            info(f"  {lexicon} ({len(lexc_rows)} entries)")
            try:
                print(comment_block(lexicon) + "\n", file=lexc_file)
            except ValueError as e:
                warn("Failed to generate comment block: {e}")
            print(f"LEXICON {lexicon}", file=lexc_file)
            for row in lexc_rows:
                print(entry2str(row), file=lexc_file)
            print("", file=lexc_file)
