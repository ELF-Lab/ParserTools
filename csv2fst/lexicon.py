import pandas as pd
import os
import re

from paradigm_slot import ParadigmSlot, entry2str, LexcEntry, escape
from log import info, warn
from lexc_comment import comment_block

class Lexicon:
    @staticmethod
    def __get_paradigm(row:pd.core.series.Series,
                       klass_map:pd.core.series.Series) -> str:
        """Return the inflectional class (like "VTA_n") for an OPD entry.
        
        The argument row represents an OPD dictionary entry like:
        
        lemma              stem              part_of_speech_id
        "naawakwe-miijin"  "naawakwe-miiji"  "vti3"

        klass_map contains patterns which are used to determine the correct
        inflectional class. E.g.:

        Class    OPDClass    MatchElement     Pattern
        "VTI_i"  "vti3"      "stem"           "^.*i$"

        - "Class" the inflectional class in our FST
        - "OPDClass" the corresponding POS in OPD (needs to match 
          part_of_speech_id)
        - "MatchElement" whether the inflectional class is determined by the 
          lemma or stem 
        - "Pattern" a regular expression which needs to match either the lemma or
          stem (depending on "MatchElement").
  
        The function finds the first matching pattern for row in klass_map and
        returns its "Class"."""
        
        for _, pattern in klass_map.iterrows():
            if row["part_of_speech_id"].lower() != pattern["OPDClass"].lower():
                continue
            element = \
                (row["lemma"] if pattern["MatchElement"] == "lemma" else row["stem"])
            if re.match(pattern["Pattern"], element):
                return pattern["Class"]
        raise ValueError(f"No matching pattern for lexical entry: {row.to_dict()}")
            
    def __init__(self,
                 conf:dict,
                 lexc_path:str,
                 read_lexical_database:bool,
                 regular:bool):
        self.conf = conf
        self.lexc_path = lexc_path
        self.regular = regular
        self.lexicons = {"Root":set()}

        csv_names = conf["regular_csv_files" if regular else "irregular_csv_files"]
        for name in csv_names:
            csv_file = os.path.join(conf["source_path"], f"{name}.csv")
            info(f"Reading lexicon entries from {csv_file}")
            table = pd.read_csv(csv_file, keep_default_na=False)
            for _, row in table.iterrows():
                paradigm_slot = ParadigmSlot(row, conf, regular)
                paradigm_slot.extend_lexicons(self.lexicons)

        if read_lexical_database:
            self.read_lexemes_from_database()
            
    def read_lexemes_from_database(self) -> None:
        """Read OPD dictionary entries from an external CSV file given by
        the "lexical_database" field in the configuration file.

        This function maps OPD POS tags like vti3 to inflectional
        classes like BorderLakesMorph VTI_i. It then adds each the OPD
        lexical entry into the appropriate lexc sublexicon (like
        VTI:Stems) with an appropriate continuation lexicon (like
        VTI:Class=VTI_i:Boundary).

        The mapping from OPD POS tags to BorderLakesMorph inflectional
        classes is based on a mapping CSV file. This file is specified
        in the "class_map" field in the configuration file.
        """
        
        info(f"Reading external lexical database {self.conf['lexical_database']}\n",
             f"Reading class mapping {self.conf['class_map']}")
        klass_map = pd.read_csv(self.conf["class_map"])
        lexeme_database = pd.read_csv(self.conf["lexical_database"],
                                      keep_default_na=False)
        skipped = 0
        for _, row in lexeme_database.iterrows():
            try:
                klass = Lexicon.__get_paradigm(row,klass_map)
                paradigm = klass.split("_")[0]
                self.lexicons[f"{paradigm}:Stems"].add(
                    LexcEntry(f"{paradigm}:Stems",
                              escape(row["lemma"]),
                              escape(row["stem"]),
                              f"{paradigm}:Class={klass}:Boundary"))
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
        print("Multichar_Symbols",file=lexc_file)
        multichar_symbols = sorted(list(ParadigmSlot.multichar_symbols))
        print(" ".join(multichar_symbols), file=lexc_file)
        print("", file=lexc_file)
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
