"""Class for representing a lexc file."""

import pandas as pd
import os
from os.path import join as pjoin

from .lexc_path import LexcPath, DerivationPath, entry2str, LexcEntry, escape
from .log import info, warn
from .lexc_comment import comment_block

class LexcFile:
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
            LexcFile.write_multichar_symbols(LexcPath.multichar_symbols,
                                            root_lexc_file)
            print("LEXICON Root", file=root_lexc_file)
            for lexicon_name in pos_root_lexicons:
                print(f"{lexicon_name} ;", file=root_lexc_file)
            print("", file=root_lexc_file)
        
    def __init__(self,
                 conf:dict,
                 source_path:str,
                 lexc_path:str,
                 database_paths:str,
                 lexical_data_to_exclude:str,
                 read_lexical_database:bool,
                 add_derivations:bool,
                 regular:bool):
        """Initialize the lexicon using a configuration file. Parameters: 
           * `conf` configuration 
           * `source_path` path to OjibweMorph repo
           * `lexc_path` destination directory for lexc code
           * `database_paths` paths to lexical data CSVs (with lemmas/stems)
           * `lexical_data_to_exclude` path to CSV listing lexical data to NOT include
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
            info(f"Reading inflection table from {csv_file}",force=False)
            table = pd.read_csv(csv_file, keep_default_na=False)
            for _, row in table.iterrows():
                lexc_path = LexcPath(row, conf, regular)
                lexc_path.extend_lexicons(self.lexicons)

        if read_lexical_database:
            self.read_lexemes_from_database(database_paths, lexical_data_to_exclude)

        if add_derivations and "derivational_csv_file" in conf:
            self.add_derivations()
            
    def read_lexemes_from_database(self, database_paths, lexical_data_to_exclude) -> None:
        """Read lemma/stem entries from one or more external CSV file
        given by the "lexical_database" field in the configuration file.
        The CSVs are located in the directory(s) listed in database_paths.

        This function adds each lexical entry into the appropriate lexc
        sublexicon (like VTI:Stems) with an appropriate continuation
        lexicon (like VTI:Class=VTI_i:Boundary).

        Forms from any of the lexical sources can be excluded, as specified in
        the CSV given in `lexical_data_to_exclude`.  Each entry there specifies
        a form by providing the source (which lexical database CSV), the field
        (e.g., lemma, POS), and the value of that field.

        """
        # Determine which forms to exclude, as specified by the user
        # Each row of the CSV specifies the "Field" and its "Value"
        # e.g., to exclude all forms with lemma X, Field=Lemma and Value=X
        classes_to_exclude = []
        lemmas_to_exclude = []
        paradigms_to_exclude = []
        stems_to_exclude = []
        # There may have been no CSV supplied (if no exclusions necessary)
        if lexical_data_to_exclude:
            exclusion_info = pd.read_csv(lexical_data_to_exclude)
            for index, row in exclusion_info.iterrows():
                field = row["Field"]
                if field == "Class":
                    classes_to_exclude.append(row['Value'])
                elif field == "Lemma":
                    lemmas_to_exclude.append(row['Value'])
                elif field == "Paradigm":
                    paradigms_to_exclude.append(row['Value'])
                elif field == "Stem":
                    stems_to_exclude.append(row['Value'])
                else:
                    print(f"ERROR: CSV with forms to exclude ({lexical_data_to_exclude}) has an erroneous row.",
                          f"\nRow {index} has the Field '{field}', which is not a recognized value.",
                          f"\nRecognized values are: Class, Lemma")

        info(f"Reading in {len(database_paths)} lexical database input(s).")
        # Read through *each* lexical database source
        for database_path in database_paths:
            info(f"Reading external lexical database {self.conf['lexical_database']} from directory {database_path}\n")
            if self.conf["lexical_database"] != "None":
                lexeme_database = pd.read_csv(os.path.join(database_path,
                                                self.conf["lexical_database"]),
                                                keep_default_na=False)

                # Determine which forms to exclude, as specified by the user
                # Each row of the CSV specifies the "Field" and its "Value"
                # e.g., to exclude all forms with lemma X, Field=Lemma and Value=X
                classes_to_exclude = []
                lemmas_to_exclude = []
                paradigms_to_exclude = []
                stems_to_exclude = []
                # There may have been no CSV supplied (if no exclusions necessary)
                if lexical_data_to_exclude:
                    exclusion_info = pd.read_csv(lexical_data_to_exclude)
                    for index, row in exclusion_info.iterrows():
                        directory = row["Directory"]
                        # Only apply exclusions intended for this lexical database source
                        if database_path.endswith(directory):
                            field = row["Field"]
                            if field == "Class":
                                classes_to_exclude.append(row['Value'])
                            elif field == "Lemma":
                                lemmas_to_exclude.append(row['Value'])
                            elif field == "Paradigm":
                                paradigms_to_exclude.append(row['Value'])
                            elif field == "Stem":
                                stems_to_exclude.append(row['Value'])
                            else:
                                print(f"ERROR: CSV with forms to exclude ({lexical_data_to_exclude}) has an erroneous row.",
                                    f"\nRow {index} has the Field '{field}', which is not a recognized value.",
                                    f"\nRecognized values are: Class, Lemma")

                # Extract the data from the lexical database file
                skipped = 0
                excluded = 0
                for _, row in lexeme_database.iterrows():
                    try:
                        klass = row.Class
                        paradigm = row.Paradigm
                        lemma = row.Lemma
                        stem = row.Stem
                        # Only proceed if this stems is *not* to be excluded
                        if not(klass in classes_to_exclude) and not(lemma in lemmas_to_exclude) and not(paradigm in paradigms_to_exclude) and not (stem in stems_to_exclude):
                            self.lexicons[f"{paradigm}_Stems"].add(
                                LexcEntry(f"{paradigm}_Stems",
                                        escape(lemma),
                                        escape(stem),
                                        f"{paradigm}_Class={klass}_Boundary"))
                        else:
                            excluded += 1
                    except ValueError as e:
                        warn(e)
                        skipped += 1
                info(f"Checked {len(lexeme_database)} lexical entries.\n",
                    f"Added {len(lexeme_database) - skipped} entries to lexc file.\n",
                    f"Skipped {skipped} invalid entries.\n",
                    f"Excluded {excluded} entries specified by the user.")

    def add_derivations(self):
        der_csv = pd.read_csv(pjoin(self.source_path, self.conf["derivational_csv_file"]))
        for _, row in der_csv.iterrows():
            DerivationPath(row,self.conf).extend_lexicons(self.lexicons)
            
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
        info(f"Writing {len(self.lexicons)} sublexicons:",force=False)
        for lexicon in self.lexicons:            
            lexc_rows = sorted(list(self.lexicons[lexicon]))
            info(f"  {lexicon} ({len(lexc_rows)} entries)",force=False)
            try:
                print(comment_block(lexicon) + "\n", file=lexc_file)
            except ValueError as e:
                warn(f"Failed to generate comment block: {e}")
            print(f"LEXICON {lexicon}", file=lexc_file)
            for row in lexc_rows:
                print(entry2str(row), file=lexc_file)
            print("", file=lexc_file)
