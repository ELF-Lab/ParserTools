from paradigm_slot import ParadigmSlot, entry2str, LexcEntry
import json
import pandas as pd
from sys import stderr
import os
import re

class Lexicon:
    @staticmethod
    def __get_paradigm(row,klass_map):
        for _, pattern in klass_map.iterrows():
            if row["part_of_speech_id"].lower() != pattern["OPDClass"].lower():
                continue
            element = (row["lemma"] if pattern["MatchElement"] == "lemma"
                                    else row["stem"])
            if re.match(pattern["Pattern"], element):
                return pattern["Class"]
        raise ValueError(f"No matching pattern for lexical entry: {row}")
            
    def __init__(self, conf:dict, lexc_path:str, read_lexical_database:bool, regular:bool):
        self.conf = conf
        self.lexc_path = lexc_path
        self.regular = regular
        self.lexicons = {"Root":set()}
        for fn in conf["regular_csv_files" if regular else "irregular_csv_files"]:
            path = os.path.join(conf["source_path"],f"{fn}.csv")
            print(f"Reading lexicon entries from {path}", file=stderr)
            table = pd.read_csv(path, keep_default_na=False)
            for _, row in table.iterrows():
                paradigm_slot = ParadigmSlot(row, conf, regular)
                paradigm_slot.extend_lexicons(self.lexicons)
        if read_lexical_database:
            self.read_lexemes_from_database()
            
    def read_lexemes_from_database(self):
        print(f"Reading external lexical database {self.conf['lexical_database']}", file=stderr)
        print(f"Reading class mapping {self.conf['class_map']}", file=stderr)
        klass_map = pd.read_csv(self.conf["class_map"])
        lexeme_database = pd.read_csv(self.conf["lexical_database"], keep_default_na=False)
        skipped = 0
        for _, row in lexeme_database.iterrows():
            try:
                klass = Lexicon.__get_paradigm(row,klass_map)
                paradigm = klass.split("_")[0]
                self.lexicons[f"{paradigm}:Stems"].add(
                    LexcEntry(f"{paradigm}:Stems",
                              row["lemma"],
                              row["stem"],
                              f"{paradigm}:Class={klass}:Boundary"))
            except ValueError as e:
                print(e)
                print("Skipping lexical entry which does not match any patterns\n")
                skipped += 1
        print(f"Checked {len(lexeme_database)} lexical entries.", file=stderr)
        print(f"Added {len(lexeme_database) - skipped} entries to lexc file.", file=stderr) 
        print(f"Skipped {skipped} invalid ones", file=stderr)

    def print_lexc(self):
        lexc_fn = os.path.join(self.lexc_path,
                               self.conf["regular_lexc_file" if self.regular
                                         else "irregular_lexc_file"])
        lexc_file = open(lexc_fn,"w")
        print("Multichar_Symbols",file=lexc_file)
        multichar_symbols = sorted(list(ParadigmSlot.multichar_symbols))
        print(" ".join(multichar_symbols), file=lexc_file)
        print("", file=lexc_file)
        print(f"Writing {len(self.lexicons)} sublexicons:", file=stderr)
        for lexicon in self.lexicons:            
            lexc_rows = sorted(list(self.lexicons[lexicon]))
            print(f"  {lexicon} ({len(lexc_rows)} entries)", file=stderr)
            print(f"LEXICON {lexicon}", file=lexc_file)
            for row in lexc_rows:
                print(entry2str(row), file=lexc_file)
            print("", file=lexc_file)
